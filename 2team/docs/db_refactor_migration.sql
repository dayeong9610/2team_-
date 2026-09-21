-- ============================================================================
-- 마냥이 DB 통합 마이그레이션
-- 목적:
--   episode_scenario -> llm_role
--   ai_evaluation    -> chat_room + chatting + score
--
-- PostgreSQL 기준입니다. 운영/공용 DB에서는 반드시 백업 후 실행하세요.
-- ============================================================================

BEGIN;

-- --------------------------------------------------------------------------
-- 1) LLM_ROLE가 Episode 저장소 역할도 하도록 확장
-- --------------------------------------------------------------------------
ALTER TABLE llm_role
    ADD COLUMN IF NOT EXISTS episode_id VARCHAR(20),
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'draft',
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE llm_role
    ALTER COLUMN title TYPE VARCHAR(120);

-- 기존 DB에서 created_at이 NOT NULL이지만 DB 기본값이 없는 경우를 보완
UPDATE llm_role
   SET created_at = CURRENT_TIMESTAMP
 WHERE created_at IS NULL;

ALTER TABLE llm_role
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uk_llm_role_episode_id'
    ) THEN
        ALTER TABLE llm_role
            ADD CONSTRAINT uk_llm_role_episode_id UNIQUE (episode_id);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_llm_role_status'
    ) THEN
        ALTER TABLE llm_role
            ADD CONSTRAINT chk_llm_role_status
            CHECK (status IN ('draft', 'published'));
    END IF;
END$$;

-- 기존 EPISODE_SCENARIO 데이터가 있으면 LLM_ROLE로 이관
DO $$
BEGIN
    IF to_regclass('public.episode_scenario') IS NOT NULL THEN
        INSERT INTO llm_role (
            episode_id,
            title,
            admin_id,
            category,
            content,
            status,
            created_at,
            updated_at
        )
        SELECT
            UPPER(episode_id),
            title,
            admin_id,
            category,
            scenario_json,
            status,
            COALESCE(created_at, CURRENT_TIMESTAMP),
            COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
        FROM episode_scenario
        ON CONFLICT (episode_id) DO UPDATE SET
            title = EXCLUDED.title,
            admin_id = EXCLUDED.admin_id,
            category = EXCLUDED.category,
            content = EXCLUDED.content,
            status = EXCLUDED.status,
            updated_at = EXCLUDED.updated_at;
    END IF;
END$$;

-- --------------------------------------------------------------------------
-- 2) CHAT_ROOM를 학생 학습 Session과 LLM_ROLE 연결 테이블로 정리
-- --------------------------------------------------------------------------
ALTER TABLE chat_room
    ADD COLUMN IF NOT EXISTS session_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS lr_num BIGINT;

-- 기존 DB의 created_at에도 서버 기본값을 보장
UPDATE chat_room
   SET created_at = CURRENT_TIMESTAMP
 WHERE created_at IS NULL;

ALTER TABLE chat_room
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

-- 예전 room_requester 컬럼이 있으면 session_id 백필에 활용
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'chat_room'
          AND column_name = 'room_requester'
    ) THEN
        EXECUTE $q$
            UPDATE chat_room
               SET session_id = COALESCE(session_id, NULLIF(room_requester, '') || '-' || room_id::text, 'legacy-' || room_id::text)
             WHERE session_id IS NULL
        $q$;
    ELSE
        UPDATE chat_room
           SET session_id = 'legacy-' || room_id::text
         WHERE session_id IS NULL;
    END IF;
END$$;

ALTER TABLE chat_room
    ALTER COLUMN session_id SET NOT NULL,
    ALTER COLUMN limits SET DEFAULT 0,
    ALTER COLUMN admin_id DROP NOT NULL,
    ALTER COLUMN lr_num DROP NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uk_chat_room_session_id'
    ) THEN
        ALTER TABLE chat_room
            ADD CONSTRAINT uk_chat_room_session_id UNIQUE (session_id);
    END IF;
END$$;

-- 예전 스키마의 추가 NOT NULL 컬럼이 남아 있어도 새 코드 INSERT가 가능하도록 기본값 부여
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='chat_room' AND column_name='title'
    ) THEN
        EXECUTE 'ALTER TABLE chat_room ALTER COLUMN title SET DEFAULT ''학습 세션''';
    END IF;
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='chat_room' AND column_name='status'
    ) THEN
        EXECUTE 'ALTER TABLE chat_room ALTER COLUMN status SET DEFAULT ''active''';
    END IF;
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='chat_room' AND column_name='room_requester'
    ) THEN
        EXECUTE 'ALTER TABLE chat_room ALTER COLUMN room_requester SET DEFAULT ''anonymous''';
    END IF;
END$$;

-- lr_num FK를 현재 모델과 맞춤
ALTER TABLE chat_room DROP CONSTRAINT IF EXISTS fk_chat_room_lr_num;
ALTER TABLE chat_room
    ADD CONSTRAINT fk_chat_room_lr_num
    FOREIGN KEY (lr_num)
    REFERENCES llm_role(lr_num)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- --------------------------------------------------------------------------
-- 3) CHATTING에 실제 대화/Stage 정보 저장
-- --------------------------------------------------------------------------
ALTER TABLE chatting
    ADD COLUMN IF NOT EXISTS stage_id VARCHAR(50),
    ADD COLUMN IF NOT EXISTS content TEXT,
    ADD COLUMN IF NOT EXISTS feedback TEXT;

UPDATE chatting
   SET stage_id = 'LEGACY_STAGE_' || chat_id::text
 WHERE stage_id IS NULL;

ALTER TABLE chatting
    ALTER COLUMN stage_id SET NOT NULL,
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uk_chatting_room_stage_chatter'
    ) THEN
        ALTER TABLE chatting
            ADD CONSTRAINT uk_chatting_room_stage_chatter
            UNIQUE (room_id, stage_id, chatter);
    END IF;
END$$;

-- --------------------------------------------------------------------------
-- 4) 기존 AI_EVALUATION 데이터가 있으면 기존 3개 테이블 구조로 이관
-- --------------------------------------------------------------------------
DO $$
BEGIN
    IF to_regclass('public.ai_evaluation') IS NOT NULL THEN
        -- llm_role이 없는 과거 평가 Episode는 draft placeholder로만 생성합니다.
        -- static JSON보다 우선 로딩되지 않도록 published로 만들지 않습니다.
        INSERT INTO llm_role (
            episode_id,
            title,
            category,
            content,
            status,
            created_at,
            updated_at
        )
        SELECT DISTINCT
            UPPER(ae.episode_id),
            UPPER(ae.episode_id),
            'user_defined',
            json_build_object(
                'episode_id', UPPER(ae.episode_id),
                'title', UPPER(ae.episode_id),
                'background', json_build_object(),
                'total_stages', 0,
                'stages', json_build_array()
            )::text,
            'draft',
            COALESCE(ae.created_at, CURRENT_TIMESTAMP),
            COALESCE(ae.created_at, CURRENT_TIMESTAMP)
        FROM ai_evaluation ae
        WHERE NOT EXISTS (
            SELECT 1 FROM llm_role lr
            WHERE lr.episode_id = UPPER(ae.episode_id)
        );

        INSERT INTO chat_room (
            session_id,
            lr_num,
            admin_id,
            limits,
            created_at
        )
        SELECT
            ae.session_id,
            lr.lr_num,
            lr.admin_id,
            0,
            COALESCE(MIN(ae.created_at), CURRENT_TIMESTAMP)
        FROM ai_evaluation ae
        JOIN llm_role lr
          ON lr.episode_id = UPPER(ae.episode_id)
        GROUP BY ae.session_id, lr.lr_num, lr.admin_id
        ON CONFLICT (session_id) DO NOTHING;

        INSERT INTO chatting (
            room_id,
            stage_id,
            chatter,
            content,
            feedback,
            created_at
        )
        SELECT
            cr.room_id,
            ae.stage_id,
            'USER',
            NULL,
            NULL,
            ae.created_at
        FROM ai_evaluation ae
        JOIN chat_room cr
          ON cr.session_id = ae.session_id
        ON CONFLICT (room_id, stage_id, chatter) DO NOTHING;

        INSERT INTO score (chat_id, category, score)
        SELECT c.chat_id, valueset.category, valueset.score
        FROM ai_evaluation ae
        JOIN chat_room cr
          ON cr.session_id = ae.session_id
        JOIN chatting c
          ON c.room_id = cr.room_id
         AND c.stage_id = ae.stage_id
         AND c.chatter = 'USER'
        CROSS JOIN LATERAL (
            VALUES
                ('risk_awareness'::varchar, ae.risk_awareness),
                ('refusal'::varchar, ae.refusal),
                ('help_request'::varchar, ae.help_request)
        ) AS valueset(category, score)
        ON CONFLICT (chat_id, category) DO UPDATE SET
            score = EXCLUDED.score;
    END IF;
END$$;

-- --------------------------------------------------------------------------
-- 5) 통합 완료 후 사용하지 않는 테이블 제거
-- --------------------------------------------------------------------------
DROP TABLE IF EXISTS ai_evaluation;
DROP TABLE IF EXISTS episode_scenario;

COMMIT;
