import manyangImg from "../assets/마냥_기본.png";

interface EpisodeItem {
  id: string;
  num: string;
  title: string;
  description: string;
  locked: boolean;
}

const episodes: EpisodeItem[] = [
  {
    id: "EP01",
    num: "01",
    title: "시험기간 스터디 그룹",
    description: "공부 잘 된다는 약을 권유받으면?",
    locked: false,
  },
  {
    id: "EP02",
    num: "02",
    title: "해외여행에서 마주친 위험한 권유",
    description: "여행 중 만난 외국인이 낯선 약을 권하면?",
    locked: false,
  },
  {
    id: "EP03",
    num: "03",
    title: "SNS 다이어트 약 DM",
    description: "인스타에서 다이어트 약을 파는 메시지가 왔어",
    locked: false,
  },
];

function EpisodeListPage() {
  const handleEpisodeClick = (id: string, locked: boolean) => {
    if (locked) return;
    window.location.assign(`/play/${id}`);
  };

  return (
    <main className="episode-list-page">
      <div className="episode-list-header">
        <div className="mascot">
          <img src={manyangImg} alt="마냥이" className="mascot-img" />
        </div>

        <div className="header-text">
          <p className="header-label">마냥이와 함께하는 거절 연습</p>
          <h1 className="header-title">
            오늘은 어떤 상황을
            <br />
            연습해볼까냥?
          </h1>
        </div>
      </div>

      <ul className="episode-list">
        {episodes.map((episode) => (
          <li key={episode.id}>
            <button
              type="button"
              className="episode-item"
              onClick={() => handleEpisodeClick(episode.id, episode.locked)}
              disabled={episode.locked}
            >
              <span className="episode-item-text">
                <span className="episode-item-num">
                  Episode {episode.num}
                </span>
                <strong className="episode-item-title">
                  {episode.title}
                </strong>
                <span className="episode-item-desc">
                  {episode.description}
                </span>
              </span>

              <span className="episode-item-arrow" aria-hidden="true">
                →
              </span>
            </button>
          </li>
        ))}
      </ul>

      <p className="episode-list-footer">청소년 마약 예방 교육 콘텐츠</p>
    </main>
  );
}

export default EpisodeListPage;
