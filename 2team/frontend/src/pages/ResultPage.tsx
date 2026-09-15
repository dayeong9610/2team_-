import { useSearchParams } from "react-router-dom";

import manyangResult from "../assets/마냥_홈 소개.png";
import { mockResult } from "../data/mockResult";

const STAT_ITEMS = [
  { key: "riskAwareness", label: "위험 인지", value: mockResult.riskAwareness },
  { key: "refusal", label: "거절 대응", value: mockResult.refusal },
  { key: "helpRequest", label: "도움 요청", value: mockResult.helpRequest },
];

function ResultPage() {
  const [searchParams] = useSearchParams();
  const episodeId = searchParams.get("episodeId") ?? "EP01";

  const handleRetry = () => {
    window.location.href = `/play/${episodeId}`;
  };

  const handleGoToEpisodes = () => {
    window.location.href = "/episodes";
  };

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

      <section className="result-stats">
        <p className="result-stats-title">오늘의 기록</p>

        {STAT_ITEMS.map((item) => (
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
