import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";

import ProgressBar from "../components/common/ProgressBar";
import NPCBubble from "../components/game/NPCBubble";
import SceneDialogue from "../components/game/SceneDialogue";
import KaraokeBackdrop from "../components/game/KaraokeBackdrop";
import InstagramDMHeader from "../components/game/InstagramDMHeader";
import InstagramBubble from "../components/game/InstagramBubble";
import UserInput from "../components/game/UserInput";
import ManyangCoach from "../components/game/ManyangCoach";
import SoundToggle from "../components/game/SoundToggle";
import SceneTransition from "../components/game/SceneTransition";
import StageSupportPanel from "../components/game/StageSupportPanel";

import type { GameStage } from "../data/episode01stages";
import { episode01Stages } from "../data/episode01stages";
import { episode02Stages } from "../data/episode02stages";
import { episode03Stages } from "../data/episode03stages";

import {
  createSession,
  sendChat,
  getSessionState,
  getEpisodeDetail,
} from "../services/api";

import type { Scores } from "../types/chat";
import type { EpisodeDetailResponse, EpisodeStageResponse } from "../types/episode";
import { registerFallbackEpisode } from "../services/resilience";
import useGameSound from "../hooks/useGameSound";

const EPISODE_META: Record<
  string,
  { num: string; title: string; layout: "chat" | "scene" }
> = {
  EP01: { num: "01", title: "시험기간 스터디 그룹", layout: "chat" },
  EP02: { num: "02", title: "SNS에서 시작된 유혹", layout: "chat" },
  EP03: { num: "03", title: "학원가에서 받은 음료", layout: "chat" },
};

const STAGES_BY_EPISODE: Record<string, GameStage[]> = {
  EP01: episode01Stages,
  EP02: episode02Stages,
  EP03: episode03Stages,
};

const AXIS_LABEL: Record<string, string> = {
  risk_awareness: "위험 인지",
  refusal: "거절 대응",
  help_request: "도움 요청",
};

function backendStageToGameStage(stage: EpisodeStageResponse): GameStage {
  const isAdvanced = stage.type.endsWith("_advanced");
  const baseLabel = AXIS_LABEL[stage.evaluation_axis] ?? stage.evaluation_axis;

  return {
    id: stage.stage_number,
    stageid: stage.stage_id,
    title: stage.title,
    location: stage.location,
    description: stage.description,
    messages: stage.messages.map((message) => ({
      sender: message.speaker,
      text: message.text,
    })),
    question: stage.question,
    evaluation: stage.evaluation_criteria,
    scoreType: isAdvanced ? `${baseLabel} 심화` : baseLabel,
  };
}

const SKILL_ICON: Record<string, string> = {
  "위험 인지": "🛡️",
  "거절 대응": "💬",
  "거절 대응 심화": "💬",
  "도움 요청": "🤝",
  "도움 요청 심화": "🤝",
};

export default function PlayPage() {
  const { episodeId = "EP01" } = useParams();
  const localStages = useMemo(
    () => STAGES_BY_EPISODE[episodeId] ?? null,
    [episodeId]
  );
  const [remoteEpisode, setRemoteEpisode] = useState<EpisodeDetailResponse | null>(null);
  const [episodeLoadError, setEpisodeLoadError] = useState("");
  const [isEpisodeLoading, setIsEpisodeLoading] = useState(localStages === null);

  useEffect(() => {
    let cancelled = false;

    if (localStages) {
      setRemoteEpisode(null);
      setEpisodeLoadError("");
      setIsEpisodeLoading(false);
      return () => {
        cancelled = true;
      };
    }

    setIsEpisodeLoading(true);
    setEpisodeLoadError("");

    getEpisodeDetail(episodeId)
      .then((episode) => {
        if (cancelled) return;
        setRemoteEpisode(episode);

        const mappedStages = episode.stages.map(backendStageToGameStage);
        registerFallbackEpisode(episode.episode_id, mappedStages);
      })
      .catch((error) => {
        if (cancelled) return;
        console.error("DB Episode load failed", error);
        setEpisodeLoadError(
          "에피소드 정보를 불러오지 못했습니다. 공개 상태와 /api/episodes/" +
            episodeId +
            " 응답을 확인해주세요."
        );
      })
      .finally(() => {
        if (!cancelled) setIsEpisodeLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [episodeId, localStages]);

  const stages = useMemo(() => {
    if (localStages) return localStages;
    return remoteEpisode?.stages.map(backendStageToGameStage) ?? [];
  }, [localStages, remoteEpisode]);

  const episodeMeta = EPISODE_META[episodeId] ?? {
    num: episodeId.replace(/^EP/i, "") || episodeId,
    title: remoteEpisode?.title ?? "새 에피소드",
    layout: "chat" as const,
  };
  const isScene = episodeMeta.layout === "scene";
  const sessionStorageKey = `manyang_session_${episodeId}`;

  const [stageIndex, setStageIndex] = useState(0);
  const [answersByStage, setAnswersByStage] = useState<Record<number, string>>({});
  const [answered, setAnswered] = useState(false);
  const [draftMessage, setDraftMessage] = useState("");
  const [sceneLineIndex, setSceneLineIndex] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [npcResponses, setNpcResponses] = useState<Record<number, string>>({});
  const [feedbackByStage, setFeedbackByStage] = useState<Record<number, string>>({});
  const [, setScores] = useState<Scores>({
    risk_awareness: 0,
    refusal: 0,
    help_request: 0,
  });
  const [nextStageId, setNextStageId] = useState<string | null>(null);
  const [retryRequired, setRetryRequired] = useState(false);
  const [showStageIntro, setShowStageIntro] = useState(true);
  const [npcIntroComplete, setNpcIntroComplete] = useState(false);
  const [sceneConfirmed, setSceneConfirmed] = useState(false);

  const conversationRef = useRef<HTMLDivElement>(null);
  const { enabled: soundEnabled, toggle: toggleSound, play: playSound } =
    useGameSound();

  const handleNpcIntroComplete = useCallback(() => {
    setNpcIntroComplete(true);
  }, []);

  const currentStage = stages[stageIndex];

  useEffect(() => {
    const el = conversationRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [stageIndex, answered, draftMessage, npcResponses]);

  useEffect(() => {
    if (!currentStage) {
      return;
    }

    setNpcIntroComplete(currentStage.messages.length === 0);
    setSceneConfirmed(!currentStage.supportPanel);
    setShowStageIntro(true);
    const timer = window.setTimeout(() => setShowStageIntro(false), 950);

    return () => window.clearTimeout(timer);
  }, [stageIndex, currentStage]);

  useEffect(() => {
    if (isEpisodeLoading || stages.length === 0) return;

    let cancelled = false;

    async function restoreOrCreateSession() {
      try {
        setErrorMessage("");
        const savedSessionId = sessionStorage.getItem(sessionStorageKey);

        if (savedSessionId) {
          try {
            const sessionState = await getSessionState(savedSessionId);
            if (cancelled) return;

            setSessionId(savedSessionId);
            setScores(sessionState.scores);

            const restoredIndex = stages.findIndex(
              (stage) => stage.stageid === sessionState.current_stage
            );

            if (restoredIndex !== -1) {
              setStageIndex(restoredIndex);
            }

            return;
          } catch {
            sessionStorage.removeItem(sessionStorageKey);
          }
        }

        const result = await createSession(episodeId);

        if (!cancelled) {
          setSessionId(result.session_id);
          sessionStorage.setItem(sessionStorageKey, result.session_id);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(
            error instanceof Error ? error.message : "세션 생성에 실패했습니다."
          );
        }
      }
    }

    restoreOrCreateSession();

    return () => {
      cancelled = true;
    };
  }, [episodeId, sessionStorageKey, stages, isEpisodeLoading]);

  if (isEpisodeLoading) {
    return (
      <div className="play-page">
        <p>에피소드를 불러오는 중이에요...</p>
      </div>
    );
  }

  if (!currentStage) {
    return (
      <div className="play-page">
        <p>{episodeLoadError || "아직 준비 중인 에피소드입니다."}</p>
      </div>
    );
  }

  const isCurrentStageDM = currentStage.location === "인스타그램 DM";
  const sceneMessages = currentStage.messages;
  const sceneNpcDone = sceneLineIndex >= sceneMessages.length;
  const sceneCurrentMessage = sceneMessages[sceneLineIndex];
  const skillIcon = SKILL_ICON[currentStage.scoreType] ?? "✨";
  const responseReady = isScene ? sceneNpcDone : npcIntroComplete;

  const handleSceneAdvance = () => {
    playSound("tap");
    setSceneLineIndex((prev) => Math.min(prev + 1, sceneMessages.length));
  };

  const handleAnswer = async (message: string) => {
    if (!sessionId || isSubmitting) return;

    try {
      playSound("tap");
      setIsSubmitting(true);
      setErrorMessage("");

      // 재입력 후 새 답변을 보내는 순간에는 이전의 "다시 답해보세요" 상태를
      // 잠시 해제합니다. 새 응답이 다시 불충분하면 아래 결과 처리에서
      // retryRequired=true로 돌아가고, 의미 있는 답변이면 정상 완료됩니다.
      setRetryRequired(false);

      setAnswersByStage((prev) => ({
        ...prev,
        [currentStage.id]: message,
      }));

      const result = await sendChat({
        session_id: sessionId,
        episode_id: episodeId,
        stage_id: currentStage.stageid,
        message,
      });

      setNpcResponses((prev) => ({
        ...prev,
        [currentStage.id]: result.npc_response,
      }));
      setFeedbackByStage((prev) => ({
        ...prev,
        [currentStage.id]: result.feedback,
      }));
      setNextStageId(result.next_stage);
      setDraftMessage("");

      if (result.retry_required) {
        // "ㅇㅇ", "ㅋㅋ"처럼 평가하기 어려운 답변은 같은 장면에서 다시 입력받습니다.
        // 사용자 입력과 NPC 안내는 채팅에 보여주되 STEP 완료/다음 버튼은 만들지 않습니다.
        setRetryRequired(true);
        setAnswered(false);
        playSound("feedback");
        return;
      }

      setRetryRequired(false);
      const sessionState = await getSessionState(sessionId);
      setScores(sessionState.scores);
      setAnswered(true);
      playSound(result.is_episode_complete ? "complete" : "feedback");
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

  const handleNext = () => {
    playSound("transition");

    if (!nextStageId) {
      window.location.assign(
        `/result?episodeId=${episodeId}&sessionId=${sessionId}`
      );
      return;
    }

    const nextIndex = stages.findIndex((stage) => stage.stageid === nextStageId);

    if (nextIndex === -1) {
      setErrorMessage("다음 단계를 찾을 수 없습니다.");
      return;
    }

    setStageIndex(nextIndex);
    setAnswered(false);
    setRetryRequired(false);
    setDraftMessage("");
    setSceneLineIndex(0);
    setNpcIntroComplete(false);
    setNextStageId(null);
  };

  return (
    <main
      className={`play-page play-page--immersive${
        currentStage.supportPanel
          ? sceneConfirmed
            ? " play-page--scene-collapsed"
            : " play-page--scene-view"
          : ""
      }`}
    >
      {showStageIntro && (
        <SceneTransition
          step={currentStage.id}
          title={currentStage.title}
          location={currentStage.location}
        />
      )}

      <div className="play-topbar play-topbar--game">
        <div className="play-topbar-main">
          <header className="game-header game-header--compact">
            <span className="episode-eyebrow">EPISODE {episodeMeta.num}</span>
            <h1>{episodeMeta.title}</h1>
          </header>

          <ProgressBar
            currentStage={currentStage.id}
            totalStages={stages.length}
          />
        </div>

        <SoundToggle enabled={soundEnabled} onToggle={toggleSound} />
      </div>

      <section className="stage-header stage-header--focus">
        <div>
          <span className="stage-kicker">STEP {currentStage.id}</span>
          <h2>{currentStage.title}</h2>
        </div>
        <span className="stage-location">📍 {currentStage.location}</span>
      </section>

      <section className="scene-brief" aria-label="현재 상황">
        <div className="scene-brief-icon" aria-hidden="true">🎬</div>
        <div>
          <span className="scene-brief-label">지금 상황</span>
          <p>{currentStage.description}</p>
        </div>
      </section>

      {currentStage.supportPanel && (
        <StageSupportPanel
          panel={currentStage.supportPanel}
          compact={sceneConfirmed}
          onConfirm={() => {
            playSound("tap");
            setSceneConfirmed(true);
            setNpcIntroComplete(false);
          }}
          onReopen={() => {
            playSound("tap");
            setSceneConfirmed(false);
          }}
        />
      )}

      {(!currentStage.supportPanel || sceneConfirmed) && (
      <div className="play-layout play-layout--focused">
        <section className="play-chat play-chat--focused">
          <section
            className={
              isScene
                ? "chat-window chat-window--vn chat-window--focused"
                : "chat-window chat-window--focused"
            }
          >
            {isScene && <KaraokeBackdrop />}
            {!isScene && isCurrentStageDM && (
              <InstagramDMHeader username={currentStage.messages[0]?.sender ?? ""} />
            )}

            <div
              className={
                isScene
                  ? "conversation conversation--vn conversation--focused"
                  : "conversation conversation--focused"
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
                        {currentStage.messages[currentStage.messages.length - 1]
                          ?.sender ?? ""}
                      </span>
                      <p className="vn-line-text">
                        {npcResponses[currentStage.id]}
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <>
                  {isCurrentStageDM ? (
                    <InstagramBubble
                      key={`intro-${currentStage.stageid}`}
                      messages={currentStage.messages}
                      onRevealComplete={handleNpcIntroComplete}
                    />
                  ) : (
                    <NPCBubble
                      key={`intro-${currentStage.stageid}`}
                      messages={currentStage.messages}
                      onRevealComplete={handleNpcIntroComplete}
                    />
                  )}

                  {answersByStage[currentStage.id] &&
                    (isCurrentStageDM ? (
                      <div className="ig-message ig-message--me">
                        <div className="ig-bubble ig-bubble--me">
                          {answersByStage[currentStage.id]}
                        </div>
                      </div>
                    ) : (
                      <div className="npc-message npc-message--me">
                        <div className="npc-bubble npc-bubble--me">
                          {answersByStage[currentStage.id]}
                        </div>
                      </div>
                    ))}

                  {answersByStage[currentStage.id] &&
                    npcResponses[currentStage.id] &&
                    (isCurrentStageDM ? (
                      <InstagramBubble
                        messages={[
                          {
                            sender:
                              currentStage.messages[currentStage.messages.length - 1]
                                ?.sender ?? "",
                            text: npcResponses[currentStage.id],
                          },
                        ]}
                      />
                    ) : (
                      <NPCBubble
                        messages={[
                          {
                            sender:
                              currentStage.messages[currentStage.messages.length - 1]
                                ?.sender ?? "",
                            text: npcResponses[currentStage.id],
                          },
                        ]}
                      />
                    ))}

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
                        <div className="npc-bubble npc-bubble--me">
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                        </div>
                      </div>
                    )
                  )}
                </>
              )}
            </div>

            {isSubmitting && (
              <div className="ai-loading ai-loading--game">
                <span className="ai-loading-dot" />
                마냥이가 답변을 보고 있어요...
              </div>
            )}

            {errorMessage && <div className="api-error">{errorMessage}</div>}

            {!answered && responseReady && (
              <section
                className={`response-focus-card${retryRequired ? " response-focus-card--retry" : ""}`}
                aria-label="내 대응 입력"
              >
                <div className="response-focus-card__lead">
                  <span className="response-focus-card__eyebrow">
                    {retryRequired ? "한 번 더 말해볼까?" : "✨ 이제 네 차례야"}
                  </span>
                  <strong>{currentStage.question}</strong>
                  <p>
                    정답을 고르는 대신, 이 상황의 상대에게 실제로 말하듯 직접 입력해보세요.
                  </p>
                </div>

                <UserInput
                  onSubmit={handleAnswer}
                  onChange={setDraftMessage}
                  disabled={isSubmitting || !sessionId}
                  placeholder="상대에게 실제로 뭐라고 말할래?"
                />
              </section>
            )}

            {!answered && !responseReady && (
              <div className="response-focus-wait" role="status" aria-live="polite">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span>상대의 말을 먼저 들어보세요.</span>
              </div>
            )}
          </section>

          {(answered || retryRequired) && feedbackByStage[currentStage.id] && (
            <section className="coach-dock" aria-label="마냥이 코칭">
              <div className="skill-focus-pill">
                <span aria-hidden="true">{skillIcon}</span>
                <span>이번에 연습한 영역</span>
                <strong>{currentStage.scoreType}</strong>
              </div>

              <ManyangCoach feedback={feedbackByStage[currentStage.id]} />

              <p className="coach-dock-note">
                {retryRequired
                  ? "이번 답변은 단계 완료로 처리하지 않았어요. 아래 입력창에서 다시 답해보세요."
                  : "정확한 3축 점수는 에피소드가 끝난 뒤 결과 화면에서 확인할 수 있어요."}
              </p>
            </section>
          )}

          {answered && !retryRequired && (
            <button className="next-button next-button--game" onClick={handleNext}>
              {currentStage.id === stages.length ? "결과 확인하기" : "계속하기"}
              <span aria-hidden="true">→</span>
            </button>
          )}
        </section>
      </div>
      )}
    </main>
  );
}
