import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";

import ProgressBar from "../components/common/ProgressBar";
import NPCBubble from "../components/game/NPCBubble";
import SceneDialogue from "../components/game/SceneDialogue";
import KaraokeBackdrop from "../components/game/KaraokeBackdrop";
import InstagramDMHeader from "../components/game/InstagramDMHeader";
import InstagramBubble from "../components/game/InstagramBubble";
import UserInput from "../components/game/UserInput";
import ManyangCoach from "../components/game/ManyangCoach";
import FeedbackCard from "../components/game/FeedbackCard";

import type { GameStage } from "../data/episode01stages";
import { episode01Stages } from "../data/episode01stages";
import { episode02Stages } from "../data/episode02stages";
import { episode03Stages } from "../data/episode03stages";
import { scoreLimits } from "../data/scoreLimits";

import {
  createSession,
  sendChat,
  getSessionState,
} from "../services/api";

import type {
  Scores,
} from "../types/chat";

// EpisodeListPage에 있는 제목/번호와 맞춰뒀습니다.
// layout "scene"은 대면 상황(노래방/룸카페 등)이라 메신저 채팅 대신
// 룸 배경 + 캐릭터 대사창(SceneDialogue)으로 보여줍니다.
const EPISODE_META: Record<
  string,
  { num: string; title: string; layout: "chat" | "scene" }
> = {
  EP01: { num: "01", title: "시험기간 스터디 그룹", layout: "chat" },
  EP02: { num: "02", title: "해외여행에서 마주친 위험한 권유", layout: "chat" },
  EP03: { num: "03", title: "SNS 다이어트 약 DM", layout: "chat" },
};

const STAGES_BY_EPISODE: Record<string, GameStage[]> = {
  EP01: episode01Stages,
  EP02: episode02Stages,
  EP03: episode03Stages,
};


// 마냥이가 등장할 스테이지 조합 (2~3회, 연속 등장 없음)
const MANYANG_APPEARANCE_SETS: number[][] = [
  [1, 3],
  [1, 4],
  [1, 5],
  [2, 4],
  [2, 5],
  [3, 5],
  [1, 3, 5],
];

function pickManyangStages(): number[] {
  const randomIndex = Math.floor(
    Math.random() * MANYANG_APPEARANCE_SETS.length
  );

  return MANYANG_APPEARANCE_SETS[randomIndex];
}

// =====================================================================
// PlayPage (실제 플레이 화면) — 라우트: "/play/:episodeId"
// ---------------------------------------------------------------------
// 에피소드를 실제로 플레이하는 화면입니다. 이 프로젝트에서 Backend와
// 가장 많이, 가장 실시간으로 통신하는 페이지예요. 아래 3개 API를
// 씁니다 (전부 services/api.ts에 정의, API_BASE_URL은
// http://localhost:8000/api).
//
// 1) POST /api/sessions   { episode_id }  → { session_id, episode_id,
//    current_stage }
//    - 이 화면에 처음 들어올 때(또는 복구할 세션이 없을 때) 호출.
//
// 2) POST /api/chat  { session_id, episode_id, stage_id, message }
//    → { npc_response, feedback, scores, next_stage, is_episode_complete }
//    - 사용자가 UserInput에 답변을 입력하고 전송할 때(handleAnswer)
//      호출. stage_id는 숫자 id(1~5)가 아니라 GameStage.stageid
//      문자열("EP01_STAGE01" 형태)을 보내야 합니다.
//    - 다음 Stage로 넘어갈지는 이 프론트가 정하지 않고, 응답의
//      next_stage 값을 그대로 따라갑니다(handleNext).
//
// 3) GET /api/sessions/{sessionId}  → { session_id, episode_id,
//    current_stage, completed_stages, scores, progress, is_complete }
//    - (a) 새로고침 등으로 재진입 시 sessionStorage에 저장된
//      session_id로 현재 진행 상태를 복구할 때
//    - (b) POST /api/chat 응답 직후, 서버 기준 최신 누적 점수를
//      다시 받아오기 위해(=score of record는 항상 서버)
//      두 경우 모두 호출합니다.
//
// [세션을 브라우저에 기억시키는 방법]
// 세션 자체는 Backend가 관리하지만, "이 브라우저가 지금 어떤
// session_id를 쓰고 있는지"는 sessionStorage에
// `manyang_session_{episodeId}` 라는 키로 저장해둡니다. 그래서 F5로
// 새로고침해도 세션이 끊기지 않고 이어집니다. 이 키는 ResultPage의
// "다시 도전하기" / "다른 상황 연습하러 가기"에서 지워집니다.
//
// [화면/시나리오 데이터 vs 서버 데이터 구분]
// 스토리 대사, 인물 이름, 배경 설명(data/episode0X stages.ts)은
// 전부 프론트에 하드코딩된 화면 표시용 데이터이고, Backend가 내려주는
// 것과는 별개입니다. 실제 채점/평가/피드백/다음 단계 결정은 전부
// Backend(POST /api/chat) 몫이고, 프론트는 그 결과를 화면에 표시만
// 합니다.
// =====================================================================

export default function PlayPage() {

  const { episodeId = "EP01" } = useParams();

  const stages = useMemo(
    () => STAGES_BY_EPISODE[episodeId] ?? [],
    [episodeId]
  );
  const episodeMeta = EPISODE_META[episodeId] ?? EPISODE_META.EP01;
  const isScene = episodeMeta.layout === "scene";

  const sessionStorageKey =
    `manyang_session_${episodeId}`;

  // 현재 Stage 배열 위치
  const [stageIndex, setStageIndex] =
    useState(0);

  // 스테이지별로 누적된 사용자 답변 (지난 대화 유지용)
  const [answersByStage, setAnswersByStage] =
    useState<Record<number, string>>({});

  // 답변 완료 여부
  const [answered, setAnswered] =
    useState(false);

  // 입력 중인 답변 (타이핑 표시용)
  const [draftMessage, setDraftMessage] =
    useState("");

  // 마냥이가 등장할 스테이지 (플레이 시작 시 1회만 랜덤 결정)
  const [manyangStages] =
    useState(pickManyangStages);

  // scene(비주얼노벨) 모드에서 현재 몇 번째 대사까지 넘겼는지
  const [sceneLineIndex, setSceneLineIndex] =
    useState(0);

  // 채팅 자동 스크롤용
  const conversationRef =
    useRef<HTMLDivElement>(null);

  // Backend에서 발급받은 Session ID
  const [sessionId, setSessionId] =
    useState<string | null>(null);

  // 답변 전송 중 로딩 상태
  const [isSubmitting, setIsSubmitting] =
    useState(false);

  // API 오류 메시지
  const [errorMessage, setErrorMessage] =
    useState("");

  // 실제 NPC 응답 (Stage별)
  const [npcResponses, setNpcResponses] =
    useState<Record<number, string>>({});

  // 실제 AI Feedback (Stage별)
  const [feedbackByStage, setFeedbackByStage] =
    useState<Record<number, string>>({});

  // 현재까지 누적된 점수
  const [scores, setScores] =
    useState<Scores>({
      risk_awareness: 0,
      refusal: 0,
      help_request: 0,
    });

  // Backend가 지정한 다음 Stage ID
  const [nextStageId, setNextStageId] =
    useState<string | null>(null);

  // 현재 Stage
  const currentStage =
    stages[stageIndex];

  // 지금까지 진행한 모든 Stage (지난 대화 누적 표시용)
  const visibleStages =
    stages.slice(0, stageIndex + 1);

  useEffect(() => {
    const el = conversationRef.current;

    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [stageIndex, answered, draftMessage]);

  // 진입 시 기존 Session 복구를 먼저 시도하고, 없거나 실패하면 새로 생성
  useEffect(() => {

    let cancelled = false;

    async function restoreOrCreateSession() {

      try {

        setErrorMessage("");

        const savedSessionId =
          sessionStorage.getItem(
            sessionStorageKey
          );

        if (savedSessionId) {

          try {

            // GET /api/sessions/{id} — 저장된 세션이 아직 유효한지
            // 확인하면서, 그 세션의 현재 Stage/점수를 그대로 복구
            const sessionState =
              await getSessionState(
                savedSessionId
              );

            if (cancelled) {
              return;
            }

            setSessionId(
              savedSessionId
            );

            setScores(
              sessionState.scores
            );

            const restoredIndex =
              stages.findIndex(
                (stage) =>
                  stage.stageid ===
                  sessionState.current_stage
              );

            if (restoredIndex !== -1) {
              setStageIndex(
                restoredIndex
              );
            }

            return;

          } catch {

            // 저장된 세션이 만료/삭제된 경우 새 세션으로 대체
            sessionStorage.removeItem(
              sessionStorageKey
            );
          }
        }

        // POST /api/sessions { episode_id } — 복구할 세션이 없거나
        // 만료된 경우, 완전히 새 세션을 시작
        const result =
          await createSession(
            episodeId
          );

        if (!cancelled) {

          setSessionId(
            result.session_id
          );

          sessionStorage.setItem(
            sessionStorageKey,
            result.session_id
          );
        }

      } catch (error) {

        if (!cancelled) {
          setErrorMessage(
            error instanceof Error
              ? error.message
              : "세션 생성에 실패했습니다."
          );
        }
      }
    }

    restoreOrCreateSession();

    return () => {
      cancelled = true;
    };

  }, [episodeId, sessionStorageKey, stages]);

  // 아직 콘텐츠가 준비되지 않은 에피소드
  if (!currentStage) {
    return (
      <div className="play-page">
        <p>아직 준비 중인 에피소드입니다.</p>
      </div>
    );
  }

  // 현재 Stage가 인스타그램 DM 상황인지 (EP03 일부 단계) - location으로 판단
  const isCurrentStageDM = currentStage.location === "인스타그램 DM";

  // scene 모드: 현재 Stage의 대사를 한 줄씩 보여주고, 다 넘기면 답변을 받습니다.
  const sceneMessages = currentStage.messages;
  const sceneNpcDone = sceneLineIndex >= sceneMessages.length;
  const sceneCurrentMessage = sceneMessages[sceneLineIndex];

  const handleSceneAdvance = () => {
    setSceneLineIndex((prev) => Math.min(prev + 1, sceneMessages.length));
  };


  // =========================
  // 사용자 답변
  // =========================


  const handleAnswer = async (
    message: string
  ) => {

    if (
      !sessionId ||
      isSubmitting
    ) {
      return;
    }

    try {

      setIsSubmitting(true);
      setErrorMessage("");

      // 화면에 사용자 답변 먼저 표시
      setAnswersByStage(
        (prev) => ({
          ...prev,
          [currentStage.id]:
            message,
        })
      );

      // POST /api/chat 호출. stage_id는 숫자 id가 아니라
      // "EP01_STAGE01" 같은 문자열(currentStage.stageid)이어야 함.
      const result =
        await sendChat({
          session_id:
            sessionId,

          episode_id:
            episodeId,

          stage_id:
            currentStage.stageid,

          message:
            message,
        });

      // NPC 실제 응답
      setNpcResponses(
        (prev) => ({
          ...prev,
          [currentStage.id]:
            result.npc_response,
        })
      );

      // 마냥이 실제 피드백
      setFeedbackByStage(
        (prev) => ({
          ...prev,
          [currentStage.id]:
            result.feedback,
        })
      );

      // Backend가 정한 다음 Stage
      setNextStageId(
        result.next_stage
      );

      // GET /api/sessions/{id} — 누적 점수는 Backend가 가진 값이
      // 정답이므로, POST /api/chat 응답과 별개로 다시 조회해서 맞춤
      const sessionState =
        await getSessionState(
          sessionId
        );

      setScores(
        sessionState.scores
      );

      setAnswered(true);

      setDraftMessage("");

    } catch (error) {

      setErrorMessage(
        error instanceof Error
          ? error.message
          : "답변 처리 중 오류가 발생했습니다."
      );

    } finally {

      setIsSubmitting(false);
    }
  };


  // =========================
  // 다음 Stage
  // =========================

  const handleNext = () => {

    // Backend가 이번 응답에서 next_stage를 안 줬다는 건 마지막
    // Stage를 마쳤다는 뜻 → ResultPage로 이동 (session_id를 쿼리로
    // 넘겨서 ResultPage가 GET /api/sessions/{id}/result를 부를 수 있게 함)
    if (!nextStageId) {

      window.location.assign(
        `/result?episodeId=${episodeId}&sessionId=${sessionId}`
      );

      return;
    }

    // 다음 Stage는 프론트가 임의로 stageIndex+1 하지 않고,
    // Backend가 알려준 next_stage(문자열 stageid)를 기준으로 찾음
    const nextIndex =
      stages.findIndex(
        (stage) =>
          stage.stageid
          === nextStageId
      );

    if (nextIndex === -1) {

      setErrorMessage(
        "다음 단계를 찾을 수 없습니다."
      );

      return;
    }

    setStageIndex(
      nextIndex
    );

    setAnswered(false);

    setDraftMessage("");

    setSceneLineIndex(0);

    setNextStageId(null);
  };

  const limits =
    scoreLimits[episodeId] ??
    scoreLimits.EP01;

  const scorePercent = (
    value: number,
    limit: number
  ) => {

    if (limit <= 0) {
      return 0;
    }

    return Math.min(
      100,
      Math.round(
        value / limit * 100
      )
    );
  };

  const riskPercent =
    scorePercent(
      scores.risk_awareness,
      limits.risk_awareness
    );

  const refusalPercent =
    scorePercent(
      scores.refusal,
      limits.refusal
    );

  const helpPercent =
    scorePercent(
      scores.help_request,
      limits.help_request
    );


  return (
    <div className="play-page">
      {/* =====================
          상단 (제목 + 진행도, 스크롤 시 상단 고정)
      ====================== */}

      <div className="play-topbar">
        <div className="play-topbar-main">
          <header className="game-header">
            <span>Episode {episodeMeta.num}</span>
            <h1>{episodeMeta.title}</h1>
          </header>

          <ProgressBar
            currentStage={currentStage.id}
            totalStages={stages.length}
          />
        </div>

        <div className="mini-stats-panel">
          <div className="mini-stat">
            <span className="mini-stat-label">위험 인지</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${riskPercent}%` }}
              />
            </div>
            <span className="mini-stat-value">
              {riskPercent}%
            </span>
          </div>

          <div className="mini-stat">
            <span className="mini-stat-label">거절 대응</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${refusalPercent}%` }}
              />
            </div>
            <span className="mini-stat-value">{refusalPercent}%</span>
          </div>

          <div className="mini-stat">
            <span className="mini-stat-label">도움 요청</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${helpPercent}%` }}
              />
            </div>
            <span className="mini-stat-value">{helpPercent}%</span>
          </div>
        </div>
      </div>

      {/* =====================
          Stage 제목
      ====================== */}

      <section className="stage-header">
        <span>STEP {currentStage.id}</span>
        <div className="stage-title-row">
          <h2>{currentStage.title}</h2>
          <span className="stage-location">📍 {currentStage.location}</span>
        </div>
      </section>

      {/* =====================
          스토리(좌측) + 채팅(중앙) 레이아웃
      ====================== */}

      <div className="play-layout">
        {/* ---------------------
            스토리 사이드
        ---------------------- */}

        <aside className="play-story">
          <section className="scene-description">
            <p>{currentStage.description}</p>
          </section>

          <section className="question-area">
            <h3>어떻게 대응하시겠습니까?</h3>
            <p>{currentStage.question}</p>
          </section>
        </aside>

        {/* ---------------------
            채팅
        ---------------------- */}

        <div className="play-chat">
          <section
            className={
              isScene ? "chat-window chat-window--vn" : "chat-window"
            }
          >
            {isScene && <KaraokeBackdrop />}
            {!isScene && isCurrentStageDM && (
              <InstagramDMHeader
                username={currentStage.messages[0]?.sender ?? ""}
              />
            )}

            <div
              className={
                isScene ? "conversation conversation--vn" : "conversation"
              }
              ref={conversationRef}
            >
              {isScene ? (
                <>
                  {!sceneNpcDone && (
                    <SceneDialogue
                      message={sceneCurrentMessage}
                      onAdvance={handleSceneAdvance}
                    />
                  )}

                  {sceneNpcDone && !answered && (
                    <div className="vn-line vn-line--prompt">
                      <p className="vn-line-text">
                        어떻게 대답하시겠습니까?
                      </p>
                    </div>
                  )}

                  {answered && (
                    <div className="vn-line vn-line--me">
                      <span className="vn-line-name">나</span>
                      <p className="vn-line-text">
                        {answersByStage[currentStage.id]}
                      </p>
                    </div>
                  )}

                  {answered && npcResponses[currentStage.id] && (
                    <div className="vn-line">
                      <span className="vn-line-name">
                        {currentStage.messages[
                          currentStage.messages.length - 1
                        ]?.sender ?? ""}
                      </span>
                      <p className="vn-line-text">{npcResponses[currentStage.id]}</p>
                    </div>
                  )}

                  {answered &&
                    feedbackByStage[currentStage.id] &&
                    manyangStages.includes(currentStage.id) && (
                    <div className="manyang-popup">
                      <ManyangCoach feedback={feedbackByStage[currentStage.id] ?? ""} />
                    </div>
                  )}
                </>
              ) : (
                <>
                  {visibleStages.map((stage) => {
                    const stageIsDM = stage.location === "인스타그램 DM";

                    return (
                      <div className="conversation-turn" key={stage.id}>
                        {stage.id !== 1 && (
                          <div className="conversation-turn-label">
                            STEP {stage.id} · {stage.title}
                          </div>
                        )}

                        {stageIsDM ? (
                          <InstagramBubble messages={stage.messages} />
                        ) : (
                          <NPCBubble messages={stage.messages} />
                        )}

                        {answersByStage[stage.id] &&
                          (stageIsDM ? (
                            <div className="ig-message ig-message--me">
                              <div className="ig-bubble ig-bubble--me">
                                {answersByStage[stage.id]}
                              </div>
                            </div>
                          ) : (
                            <div className="npc-message npc-message--me">
                              <div className="npc-bubble npc-bubble--me">
                                {answersByStage[stage.id]}
                              </div>
                            </div>
                          ))}

                        {answersByStage[stage.id] &&
                          npcResponses[stage.id] &&
                          (stageIsDM ? (
                            <InstagramBubble
                              messages={[
                                {
                                  sender:
                                    stage.messages[stage.messages.length - 1]
                                      ?.sender ?? "",
                                  text: npcResponses[stage.id],
                                },
                              ]}
                            />
                          ) : (
                            <NPCBubble
                              messages={[
                                {
                                  sender:
                                    stage.messages[stage.messages.length - 1]
                                      ?.sender ?? "",
                                  text: npcResponses[stage.id],
                                },
                              ]}
                            />
                          ))}
                      </div>
                    );
                  })}

                  {!answered && draftMessage.trim() && (
                    isCurrentStageDM ? (
                      <div className="ig-message ig-message--me">
                        <div className="ig-bubble ig-bubble--me">
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                        </div>
                      </div>
                    ) : (
                      <div className="npc-message npc-message--me">
                        <div className="npc-bubble npc-bubble--typing">
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                        </div>
                      </div>
                    )
                  )}

                  {answered &&
                    feedbackByStage[currentStage.id] &&
                    manyangStages.includes(currentStage.id) && (
                    <div className="manyang-popup">
                      <ManyangCoach feedback={feedbackByStage[currentStage.id] ?? ""} />
                    </div>
                  )}
                </>
              )}
            </div>

            {isSubmitting && (
              <p className="ai-loading">
                마냥이가 답변을 분석하고 있어요...
              </p>
            )}

            {errorMessage && (
              <div className="api-error">
                {errorMessage}
              </div>
            )}

            {!answered && (!isScene || sceneNpcDone) && (
              <UserInput
                onSubmit={handleAnswer}
                onChange={setDraftMessage}
                disabled={isSubmitting || !sessionId}
              />
            )}
          </section>

          {answered && (
            <section className="result-area">
              <FeedbackCard
                scoreType={currentStage.scoreType}
                scores={scores}
                limits={limits}
              />

              <button className="next-button" onClick={handleNext}>
                {currentStage.id === 5 ? "결과 확인하기" : "다음 단계"}
              </button>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}