import { useEffect, useState } from "react";

import manyangImg from "../assets/마냥_기본.png";
import { getEpisodes } from "../services/api";
import type { EpisodeSummaryResponse } from "../types/episode";

interface EpisodeItem {
  id: string;
  num: string;
  title: string;
  description: string;
  locked: boolean;
}

const FALLBACK_EPISODES: EpisodeItem[] = [
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
    title: "SNS에서 시작된 유혹",
    description: "SNS에서 살 빠지는 약을 준다는 DM이 왔다면?",
    locked: false,
  },
  {
    id: "EP03",
    num: "03",
    title: "학원가에서 받은 음료",
    description: "학원가에서 낯선 사람이 무료 음료를 나눠준다면?",
    locked: false,
  },
];

function toEpisodeItem(episode: EpisodeSummaryResponse): EpisodeItem {
  const number = episode.episode_id.replace(/^EP/i, "");
  return {
    id: episode.episode_id,
    num: number || episode.episode_id,
    title: episode.title,
    description: episode.description,
    locked: false,
  };
}

function EpisodeListPage() {
  const [episodes, setEpisodes] = useState<EpisodeItem[]>(FALLBACK_EPISODES);
  const [isLoading, setIsLoading] = useState(true);
  const [usingFallback, setUsingFallback] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadEpisodes() {
      try {
        const result = await getEpisodes();
        if (cancelled) return;

        setEpisodes(result.map(toEpisodeItem));
        setUsingFallback(false);
      } catch (error) {
        console.error("Episode list load failed", error);
        if (cancelled) return;

        setEpisodes(FALLBACK_EPISODES);
        setUsingFallback(true);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    loadEpisodes();

    return () => {
      cancelled = true;
    };
  }, []);

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

      {isLoading && (
        <p className="episode-list-status">에피소드를 불러오는 중이에요...</p>
      )}
      {!isLoading && usingFallback && (
        <p className="episode-list-status">
          서버 목록을 불러오지 못해 기본 에피소드만 표시하고 있어요.
        </p>
      )}

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
                <span className="episode-item-num">Episode {episode.num}</span>
                <strong className="episode-item-title">{episode.title}</strong>
                <span className="episode-item-desc">{episode.description}</span>
              </span>

              <span className="episode-item-arrow" aria-hidden="true">→</span>
            </button>
          </li>
        ))}
      </ul>

      <p className="episode-list-footer">청소년 마약 예방 교육 콘텐츠</p>
    </main>
  );
}

export default EpisodeListPage;
