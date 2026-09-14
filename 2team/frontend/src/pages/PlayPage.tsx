import { useState } from "react";

import ProgressBar from "../components/common/ProgressBar";
import NPCBubble from "../components/game/NPCBubble";
import UserInput from "../components/game/UserInput";
import ManyangCoach from "../components/game/ManyangCoach";
import FeedbackCard from "../components/game/FeedbackCard";

import { episode01Stages } from "../data/episode01stages";


export default function PlayPage() {

  // 현재 Stage 배열 위치
  const [stageIndex, setStageIndex] =
    useState(0);

  // 사용자가 입력한 답변
  const [userAnswer, setUserAnswer] =
    useState("");

  // 답변 완료 여부
  const [answered, setAnswered] =
    useState(false);

  // 현재 Stage
  const currentStage =
    episode01Stages[stageIndex];


  // =========================
  // 사용자 답변
  // =========================

  const handleAnswer = (
    message: string
  ) => {

    setUserAnswer(message);

    setAnswered(true);
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

      setUserAnswer("");

      setAnswered(false);

    } else {

      // Stage 5 종료
      window.location.href =
        "/result";
    }
  };


  return (
    <div className="play-page">
      {/* =====================
          상단
      ====================== */}

      <header className="game-header">
        <span>Episode 01</span>
        <h1>시험기간 스터디 그룹</h1>
      </header>

      {/* =====================
          진행도
      ====================== */}

      <ProgressBar
        currentStage={currentStage.id}
        totalStages={episode01Stages.length}
      />

      {/* =====================
          Stage 정보
      ====================== */}

      <section className="stage-header">
        <span>STEP {currentStage.id}</span>
        <h2>{currentStage.title}</h2>
        <p>📍 {currentStage.location}</p>
      </section>

      {/* =====================
          상황 설명
      ====================== */}

      <section className="scene-description">
        <p>{currentStage.description}</p>
      </section>

      {/* =====================
          NPC 대화
      ====================== */}

      <section className="conversation">
        {currentStage.messages.map((message, index) => (
          <NPCBubble key={index} message={message} />
        ))}
      </section>

      {/* =====================
          질문
      ====================== */}

      <section className="question-area">
        <h3>어떻게 대응하시겠습니까?</h3>
        <p>{currentStage.question}</p>
      </section>

      {/* =====================
          사용자 입력
      ====================== */}

      {!answered && <UserInput onSubmit={handleAnswer} />}

      {/* =====================
          답변 이후
      ====================== */}

      {answered && (
        <section className="result-area">
          <FeedbackCard
            userAnswer={userAnswer}
            scoreType={currentStage.scoreType}
          />

          <ManyangCoach stage={currentStage.id} />

          <button className="next-button" onClick={handleNext}>
            {currentStage.id === 5 ? "결과 확인하기" : "다음 단계"}
          </button>
        </section>
      )}
    </div>
  );
}