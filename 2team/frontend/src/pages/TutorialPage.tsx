import manyangIntro from "../assets/마냥_기본.png";
import manyangTutorial from "../assets/마냥_튜토리얼.png";

const FLOW_STEPS = [
  { icon: "👀", label: "장면 보기" },
  { icon: "💬", label: "상대의 말 듣기" },
  { icon: "✨", label: "내 차례" },
  { icon: "✍️", label: "직접 말하기" },
  { icon: "🐱", label: "마냥이 피드백" },
];

const GUIDE_ITEMS = [
  {
    icon: "✍️",
    title: "선택지 없이 직접 말해요",
    description: "진짜 그 자리에 있는 것처럼 네가 할 말을 그대로 입력해보세요.",
  },
  {
    icon: "💡",
    title: "힌트는 필요할 때만",
    description: "먼저 스스로 판단하고, 막막할 때만 위험 신호 힌트를 열어볼 수 있어요.",
  },
  {
    icon: "📊",
    title: "세 가지 대응을 연습해요",
    description: "위험 인지 · 거절 대응 · 도움 요청을 단계별로 연습하고 피드백을 받아요.",
  },
];

function TutorialPage() {
  const handleContinue = () => {
    window.location.href = "/episodes";
  };

  return (
    <main className="tutorial-page tutorial-page--response-first">
      <section className="tutorial-hero">
        <div className="home-character-box tutorial-hero__character">
          <img
            src={manyangIntro}
            alt="마냥이 캐릭터"
            className="home-character-img"
          />
        </div>

        <div className="home-bubble home-bubble--right tutorial-hero__bubble">
          <span className="tutorial-hero__eyebrow">마냥이와 하는 실제 대응 연습</span>
          <h1>정답을 고르는 게임이 아니야.</h1>
          <p>
            상황 속 상대에게 <strong>네가 실제로 할 말</strong>을 직접 입력해봐.
            <br />
            상대의 반응을 보고, 마지막에 내가 짧게 코칭해줄게냥.
          </p>
        </div>
      </section>

      <section className="tutorial-flow" aria-label="게임 진행 순서">
        {FLOW_STEPS.map((step, index) => (
          <div className="tutorial-flow__item" key={step.label}>
            <span className="tutorial-flow__icon" aria-hidden="true">{step.icon}</span>
            <strong>{step.label}</strong>
            {index < FLOW_STEPS.length - 1 && (
              <span className="tutorial-flow__arrow" aria-hidden="true">→</span>
            )}
          </div>
        ))}
      </section>

      <section className="tutorial-action-demo" aria-label="대응 입력 예시">
        <span className="tutorial-action-demo__eyebrow">✨ 이제 네 차례야</span>
        <strong>친구가 정체를 모르는 알약을 권한다면 뭐라고 말할래?</strong>
        <div className="tutorial-action-demo__input">
          <span>예: “난 안 먹을래. 뭔지 모르는데 먹는 건 불안해.”</span>
          <span aria-hidden="true">➤</span>
        </div>
      </section>

      <div className="tutorial-guide-row tutorial-guide-row--compact">
        <section className="tutorial-guide tutorial-guide--compact">
          {GUIDE_ITEMS.map((item) => (
            <div className="tutorial-guide-item" key={item.title}>
              <span className="tutorial-guide-icon" aria-hidden="true">{item.icon}</span>
              <h3 className="tutorial-guide-title">{item.title}</h3>
              <p className="tutorial-guide-desc">{item.description}</p>
            </div>
          ))}
        </section>

        <img
          src={manyangTutorial}
          alt=""
          aria-hidden="true"
          className="tutorial-decor tutorial-decor--compact"
        />
      </div>

      <button
        type="button"
        className="home-start-button tutorial-start-button"
        onClick={handleContinue}
      >
        이해했어, 연습 시작하기 →
      </button>

      <p className="tutorial-privacy-note">
        실제 개인정보나 민감한 정보는 입력하지 말고, 상황 대응만 편하게 연습해보세요.
      </p>
    </main>
  );
}

export default TutorialPage;
