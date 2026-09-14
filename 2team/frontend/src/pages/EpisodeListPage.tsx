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
    title: "파티에서의 낯선 권유",
    description: "모르는 사람이 음료에 뭔가를 넣으려 해",
    locked: true,
  },
  {
    id: "EP03",
    num: "03",
    title: "SNS 다이어트 약 DM",
    description: "인스타에서 다이어트 약을 파는 메시지가 왔어",
    locked: true,
  },
];

function ManyangMascot() {
  return (
    <svg
      className="mascot-svg"
      viewBox="0 0 160 175"
      aria-hidden="true"
    >
      {/* tail */}
      <path
        d="M22 158 C -8 128, -2 72, 34 54 C 54 44, 62 64, 46 74 C 30 84, 34 112, 55 132 C 66 143, 54 158, 38 158 Z"
        fill="#E58C4F"
      />

      {/* flag stick */}
      <line x1="113" y1="93" x2="133" y2="50" stroke="#C9C2B2" strokeWidth="3" strokeLinecap="round" />
      <path d="M133 50 L160 58 L136 70 Z" fill="#3D7C71" />

      {/* raised arm */}
      <path
        d="M104 148 C 118 134, 121 112, 113 95"
        stroke="#FFFFFF"
        strokeWidth="16"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M104 148 C 118 134, 121 112, 113 95"
        stroke="#D9D2C2"
        strokeWidth="16"
        strokeLinecap="round"
        fill="none"
        opacity="0.25"
      />
      <circle cx="113" cy="93" r="10" fill="#FFFFFF" stroke="#D9D2C2" strokeWidth="1.5" />

      {/* body */}
      <ellipse cx="84" cy="132" rx="54" ry="36" fill="#FFFFFF" stroke="#D9D2C2" strokeWidth="2" />

      {/* front paws */}
      <ellipse cx="62" cy="162" rx="13" ry="9" fill="#FFFFFF" stroke="#D9D2C2" strokeWidth="1.5" />
      <ellipse cx="100" cy="163" rx="11" ry="8" fill="#FFFFFF" stroke="#D9D2C2" strokeWidth="1.5" />

      {/* head */}
      <circle cx="79" cy="70" r="42" fill="#FFFFFF" stroke="#D9D2C2" strokeWidth="2" />

      {/* ears */}
      <path d="M44 46 L36 14 L68 36 Z" fill="#2B2420" />
      <path d="M116 46 L130 12 L92 34 Z" fill="#E58C4F" />
      <path d="M49 42 L45 24 L62 37 Z" fill="#F6C7AE" />
      <path d="M111 42 L119 21 L98 34 Z" fill="#F6C7AE" />

      {/* head patches */}
      <path
        d="M38 56 C 32 40, 54 28, 65 39 C 71 50, 54 67, 38 56 Z"
        fill="#2B2420"
      />
      <path
        d="M106 50 C 120 39, 124 61, 109 69 C 98 73, 95 58, 106 50 Z"
        fill="#E58C4F"
      />

      {/* blush */}
      <ellipse cx="57" cy="86" rx="6" ry="4" fill="#F6AF98" opacity="0.7" />
      <ellipse cx="104" cy="86" rx="6" ry="4" fill="#F6AF98" opacity="0.7" />

      {/* eyes */}
      <circle cx="65" cy="73" r="5" fill="#2B2420" />
      <circle cx="96" cy="73" r="5" fill="#2B2420" />
      <circle cx="67" cy="71" r="1.4" fill="#fff" />
      <circle cx="98" cy="71" r="1.4" fill="#fff" />

      {/* nose + mouth */}
      <path d="M77 83 L85 83 L81 88 Z" fill="#D9724F" />
      <path
        d="M81 88 Q 81 93 73 93 M81 88 Q 81 93 89 93"
        stroke="#2B2420"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      />

      {/* whiskers */}
      <path
        d="M27 78 L54 76 M27 90 L54 85 M131 78 L104 76 M131 90 L104 85"
        stroke="#D9D2C2"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function EpisodeListPage() {
  const handleEpisodeClick = (id: string, locked: boolean) => {
    if (locked) return;
    window.location.href = `/play/${id}`;
  };

  return (
    <main className="episode-list-page">
      <div className="episode-list-header">
        <div className="mascot">
          <ManyangMascot />
        </div>

        <div className="header-text">
          <p className="header-label">마냥이와 함께하는 거절 연습</p>
          <h1 className="header-title">
            오늘은 어떤 상황을
            <br />
            연습해볼까?
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
