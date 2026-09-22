import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { getEpisodeDetail } from "../services/api";
import "./ClassJoinPage.css";

type LookupState = {
  episodeId: string;
  status: "idle" | "success" | "error";
  title?: string;
  error?: string;
};

export default function ClassJoinPage() {
  const { episodeId = "" } = useParams();
  const navigate = useNavigate();
  const [inputCode, setInputCode] = useState("");
  const [lookup, setLookup] = useState<LookupState>({
    episodeId: "",
    status: "idle",
  });

  const normalized = episodeId.trim().toUpperCase();
  const manualMode = !normalized;
  const invalidCode = Boolean(normalized) && !normalized.startsWith("EP");
  const currentLookup = lookup.episodeId === normalized ? lookup : null;

  useEffect(() => {
    if (!normalized || invalidCode) {
      return;
    }

    let cancelled = false;

    getEpisodeDetail(normalized)
      .then((episode) => {
        if (cancelled) return;

        setLookup({
          episodeId: normalized,
          status: "success",
          title: episode.title,
        });

        window.setTimeout(() => {
          if (!cancelled) {
            navigate(`/play/${encodeURIComponent(episode.episode_id)}`, {
              replace: true,
            });
          }
        }, 350);
      })
      .catch(() => {
        if (cancelled) return;

        setLookup({
          episodeId: normalized,
          status: "error",
          error:
            "해당 수업 Episode를 찾을 수 없습니다. 선생님께 코드를 확인해주세요.",
        });
      });

    return () => {
      cancelled = true;
    };
  }, [invalidCode, navigate, normalized]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const code = inputCode.trim().toUpperCase();
    if (!code) return;

    navigate(`/class/${encodeURIComponent(code)}`);
  }

  const error = invalidCode
    ? "올바른 수업코드가 아닙니다."
    : currentLookup?.status === "error"
      ? currentLookup.error ?? "수업 정보를 확인할 수 없습니다."
      : "";

  const message = manualMode
    ? "선생님이 알려준 Episode 수업코드를 입력해주세요."
    : invalidCode
      ? ""
      : currentLookup?.status === "success"
        ? `${currentLookup.title ?? normalized} 수업으로 연결 중이에요.`
        : `${normalized} 수업을 확인하고 있어요.`;

  return (
    <main className="class-join-page">
      <section className="class-join-card">
        <span className="class-join-eyebrow">수업 참여</span>

        <h1>
          {manualMode
            ? "수업코드를 입력해주세요"
            : error
              ? "수업에 입장할 수 없어요"
              : "마냥이 수업에 연결 중"}
        </h1>

        <p>{error || message}</p>

        {manualMode ? (
          <form className="class-code-form" onSubmit={handleSubmit}>
            <input
              value={inputCode}
              onChange={(event) =>
                setInputCode(event.target.value.toUpperCase())
              }
              autoComplete="off"
              placeholder="예: EP02"
              aria-label="수업 코드"
            />
            <button type="submit">수업 입장</button>
          </form>
        ) : (
          <>
            <div className="class-code-chip">
              수업 코드 {normalized}
            </div>

            {error && (
              <button
                type="button"
                onClick={() => navigate("/class")}
              >
                다른 수업코드 입력
              </button>
            )}
          </>
        )}
      </section>
    </main>
  );
}
