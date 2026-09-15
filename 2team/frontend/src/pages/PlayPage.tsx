import { useEffect, useRef, useState } from "react";

import ProgressBar from "../components/common/ProgressBar";
import NPCBubble from "../components/game/NPCBubble";
import UserInput from "../components/game/UserInput";
import ManyangCoach from "../components/game/ManyangCoach";
import FeedbackCard from "../components/game/FeedbackCard";

import { episode01Stages } from "../data/episode01stages";
import { mockResult } from "../data/mockResult";


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

// 밑 import는 백엔드,api 연동시 사용!!
 // import { sendChat } from "../services/api";

export default function PlayPage() {

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

  // 채팅 자동 스크롤용
  const conversationRef =
    useRef<HTMLDivElement>(null);

  // 현재 Stage
  const currentStage =
    episode01Stages[stageIndex];

  // 지금까지 진행한 모든 Stage (지난 대화 누적 표시용)
  const visibleStages =
    episode01Stages.slice(0, stageIndex + 1);

  useEffect(() => {
    const el = conversationRef.current;

    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [stageIndex, answered]);


  // =========================
  // 사용자 답변
  // =========================


  // 밑 코드는 목업기준 코드 이후 백엔드,api 연동시 수정 필요
  
  const handleAnswer = (
    message: string
  ) => {

    setAnswersByStage((prev) => ({
      ...prev,
      [currentStage.id]: message,
    }));

    setAnswered(true);

    setDraftMessage("");
  };


  // =========================
  // 다음 Stage
  // =========================

  const handleNext = () => {

    // 마지막 Stage인지 확인
    if (
      stageIndex <
      episode01Stages.length - 1
    ) {

      setStageIndex(
        (prev) => prev + 1
      );

      setAnswered(false);

      setDraftMessage("");

    } else {

      // Stage 5 종료
      window.location.href =
        "/result";
    }
  };


  return (
    <div className="play-page">
      {/* =====================
          상단 (제목 + 진행도, 스크롤 시 상단 고정)
      ====================== */}

      <div className="play-topbar">
        <div className="play-topbar-main">
          <header className="game-header">
            <span>Episode 01</span>
            <h1>시험기간 스터디 그룹</h1>
          </header>

          <ProgressBar
            currentStage={currentStage.id}
            totalStages={episode01Stages.length}
          />
        </div>

        <div className="mini-stats-panel">
          <div className="mini-stat">
            <span className="mini-stat-label">위험 인지</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${mockResult.riskAwareness}%` }}
              />
            </div>
            <span className="mini-stat-value">
              {mockResult.riskAwareness}%
            </span>
          </div>

          <div className="mini-stat">
            <span className="mini-stat-label">거절 대응</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${mockResult.refusal}%` }}
              />
            </div>
            <span className="mini-stat-value">{mockResult.refusal}%</span>
          </div>

          <div className="mini-stat">
            <span className="mini-stat-label">도움 요청</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${mockResult.helpRequest}%` }}
              />
            </div>
            <span className="mini-stat-value">{mockResult.helpRequest}%</span>
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

      <div
        className={
          currentStage.id === 5
            ? "play-layout play-layout--vertical"
            : "play-layout"
        }
      >
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
          <section className="chat-window">
            <div className="conversation" ref={conversationRef}>
              {visibleStages.map((stage) => (
                <div className="conversation-turn" key={stage.id}>
                  {stage.id !== 1 && (
                    <div className="conversation-turn-label">
                      STEP {stage.id} · {stage.title}
                    </div>
                  )}

                  <NPCBubble messages={stage.messages} />

                  {answersByStage[stage.id] && (
                    <div className="npc-message npc-message--me">
                      <div className="npc-bubble npc-bubble--me">
                        {answersByStage[stage.id]}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {!answered && draftMessage.trim() && (
                <div className="npc-message npc-message--me">
                  <div className="npc-bubble npc-bubble--typing">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              )}

              {answered && manyangStages.includes(currentStage.id) && (
                <div className="manyang-popup">
                  <ManyangCoach stage={currentStage.id} />
                </div>
              )}
            </div>

            {!answered && (
              <UserInput onSubmit={handleAnswer} onChange={setDraftMessage} />
            )}
          </section>

          {answered && (
            <section className="result-area">
              <FeedbackCard scoreType={currentStage.scoreType} />

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