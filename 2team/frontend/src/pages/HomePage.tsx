import { useEffect, useRef, useState } from "react";

import manyangSitting from "../assets/마냥_기본.png";
import manyangLying from "../assets/마냥_홈 소개.png";

const INTRO_TEXT =
  "안녕하냥, 나는 마냥이다옹! 위험한 순간, 거절하기 어려운 순간에 너와 함께 연습할거다냥. 실제 대화처럼 다양한 상황을 겪어보면서 나를 지키는 방법을 같이 배워보자냥.";
const CTA_TEXT = "오늘은 어떤 상황을 함께 연습해볼까냥?";

function HomePage() {
  const handleStart = () => {
    window.location.href = "/tutorial";
  };

  const [introText, setIntroText] = useState("");
  const [ctaText, setCtaText] = useState("");
  const [phase, setPhase] = useState<"intro" | "cta" | "ready">("intro");
  const skippedRef = useRef(false);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    if (prefersReducedMotion) {
      setIntroText(INTRO_TEXT);
      setCtaText(CTA_TEXT);
      setPhase("ready");
      return;
    }

    let timer = 0;
    let introIndex = 0;
    let ctaIndex = 0;

    const typeCta = () => {
      if (skippedRef.current) return;

      ctaIndex += 1;
      setCtaText(CTA_TEXT.slice(0, ctaIndex));

      if (ctaIndex < CTA_TEXT.length) {
        timer = window.setTimeout(typeCta, 34);
      } else {
        timer = window.setTimeout(() => setPhase("ready"), 180);
      }
    };

    const typeIntro = () => {
      if (skippedRef.current) return;

      introIndex += 1;
      setIntroText(INTRO_TEXT.slice(0, introIndex));

      if (introIndex < INTRO_TEXT.length) {
        timer = window.setTimeout(typeIntro, 24);
      } else {
        timer = window.setTimeout(() => {
          setPhase("cta");
          typeCta();
        }, 320);
      }
    };

    timer = window.setTimeout(typeIntro, 420);

    return () => window.clearTimeout(timer);
  }, []);

  const skipIntro = () => {
    skippedRef.current = true;
    setIntroText(INTRO_TEXT);
    setCtaText(CTA_TEXT);
    setPhase("ready");
  };

  const isCtaVisible = phase === "cta" || phase === "ready";
  const isReady = phase === "ready";

  return (
    <main className="home-page">
      {!isReady && (
        <button
          type="button"
          className="home-skip-intro"
          onClick={skipIntro}
          aria-label="인트로 바로 보기"
        >
          바로 보기
        </button>
      )}

      <div className="home-content" onClick={!isReady ? skipIntro : undefined}>
        <section className="home-hero home-reveal home-reveal--visible">
          <div className="home-character-box home-character-box--pop">
            <img
              src={manyangSitting}
              alt="마냥이 캐릭터"
              className="home-character-img"
            />
          </div>

          <div className="home-bubble home-bubble--right home-bubble--live">
            <p aria-live="polite">
              {introText}
              {phase === "intro" && <span className="home-typing-caret" aria-hidden="true" />}
            </p>
          </div>
        </section>

        <section
          className={`home-cta home-reveal ${
            isCtaVisible ? "home-reveal--visible" : ""
          }`}
          aria-hidden={!isCtaVisible}
        >
          <div className="home-bubble home-bubble--left home-bubble--live">
            <p aria-live="polite">
              {ctaText}
              {phase === "cta" && <span className="home-typing-caret" aria-hidden="true" />}
            </p>

            <button
              type="button"
              className={`home-start-button ${isReady ? "home-start-button--ready" : ""}`}
              onClick={(event) => {
                event.stopPropagation();
                handleStart();
              }}
              disabled={!isReady}
            >
              시작하기
            </button>
          </div>

          <div className="home-character-box home-character-box--pop">
            <img
              src={manyangLying}
              alt="마냥이 캐릭터"
              className="home-character-img"
            />
          </div>
        </section>
      </div>

      <footer className="home-footer">
        <p>
          청소년 사이버상담센터 <strong>1388</strong> · 24시 마약류 상담센터{" "}
          <strong>1899-0893</strong> · 한국마약퇴치운동본부{" "}
          <strong>1342-1342</strong>
        </p>
      </footer>
    </main>
  );
}

export default HomePage;
