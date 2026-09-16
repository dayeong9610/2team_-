import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import manyangResult from "../assets/마냥_홈 소개.png";

import { getSessionResult } from "../services/api";
import type { SessionResultResponse } from "../types/session";

function ResultPage() {
  const [searchParams] = useSearchParams();
  const episodeId = searchParams.get("episodeId") ?? "EP01";
  const sessionId = searchParams.get("sessionId");

  const [result, setResult] = useState<SessionResultResponse | null>(null);
  const [isLoading, setIsLoading] = useState(!!sessionId);
  const [errorMessage, setErrorMessage] = useState(
    sessionId ? "" : "결과 정보를 찾을 수 없습니다."
  );

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    let cancelled = false;

    async function loadResult() {
      try {
        const data = await getSessionResult(sessionId as string);

        if (!cancelled) {
          setResult(data);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(
            error instanceof Error
              ? error.message
              : "결과를 불러오지 못했습니다."
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadResult();

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleRetry = () => {
    window.location.assign(`/play/${result?.episode_id ?? episodeId}`);
  };

  const handleGoToEpisodes = () => {
    window.location.assign("/episodes");
  };

  const maxScore = result ? result.stage_results.length * 3 : 0;

  const toPercent = (value: number) => {
    if (maxScore <= 0) {
      return 0;
    }

    return Math.min(100, Math.round((value / maxScore) * 100));
  };

  const statItems = result
    ? [
        {
          key: "riskAwareness",
          label: "위험 인지",
          value: toPercent(result.scores.risk_awareness),
        },
        {
          key: "refusal",
          label: "거절 대응",
          value: toPercent(result.scores.refusal),
        },
        {
          key: "helpRequest",
          label: "도움 요청",
          value: toPercent(result.scores.help_request),
        },
      ]
    : [];

  return (
    <main className="result-page">
      <div className="result-hero">
        <div className="home-character-box">
          <img
            src={manyangResult}
            alt="마냥이 캐릭터"
            className="home-character-img"
          />
        </div>

        <div className="home-bubble home-bubble--right">
          <p>
            수고했다냥! Episode를 무사히 마쳤다옹.
            <br />
            오늘 연습한 대응, 실제 상황에서도 꼭 기억해두자냥.
          </p>
        </div>
      </div>

      {isLoading && <p className="result-loading">결과를 불러오는 중이에요...</p>}

      {errorMessage && <div className="api-error">{errorMessage}</div>}

      {result && (
        <>
          <section className="result-stats">
            <p className="result-stats-title">오늘의 기록</p>

            {statItems.map((item) => (
              <div className="result-stat" key={item.key}>
                <span className="result-stat-label">{item.label}</span>

                <div className="result-stat-track">
                  <div
                    className="result-stat-fill"
                    style={{ width: `${item.value}%` }}
                  />
                </div>

                <span className="result-stat-value">{item.value}%</span>
              </div>
            ))}
          </section>

          {result.stage_results.length > 0 && (
            <section className="result-stage-feedback">
              <p className="result-stats-title">단계별 마냥이 피드백</p>

              {result.stage_results.map((stage) => (
                <div className="result-stage-item" key={stage.stage_id}>
                  <strong>{stage.stage_id}</strong>
                  <p>{stage.feedback}</p>
                </div>
              ))}
            </section>
          )}
        </>
      )}

      <div className="result-actions">
        <button
          type="button"
          className="home-start-button"
          onClick={handleRetry}
        >
          다시 도전하기
        </button>

        <button
          type="button"
          className="home-start-button home-start-button--outline"
          onClick={handleGoToEpisodes}
        >
          다른 상황 연습하러 가기
        </button>
      </div>

      <footer className="home-footer">
        <p>
          청소년 상담전화 <strong>1388</strong> · 마약류 중독관리센터{" "}
          <strong>1899-0893</strong>
        </p>
      </footer>
    </main>
  );
}

export default ResultPage;
