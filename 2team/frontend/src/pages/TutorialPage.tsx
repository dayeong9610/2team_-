import manyangIntro from "../assets/마냥_기본.png";
import manyangTutorial from "../assets/마냥_튜토리얼.png";

interface GuideItem {
  icon: string;
  title: string;
  description: string;
}

const GUIDE_ITEMS: GuideItem[] = [
  {
    icon: "🎮",
    title: "게임 진행 방법",
    description:
      "상황을 잘 읽고, 어떻게 대응할지 나한테 알려달라옹! 네 대답에 따라 다음 이야기로 이어진다냥.",
  },
  {
    icon: "✍️",
    title: "자유 입력 방식",
    description:
      "정해진 선택지는 없다옹! 진짜 네가 할 것 같은 말을 그대로 적어보라냥.",
  },
  {
    icon: "🐱",
    title: "마냥이 피드백",
    description: "가끔 내가 짠 하고 나타나서 네 대답에 코칭을 해줄 거다옹!",
  },
  {
    icon: "📊",
    title: "점수 영역",
    description:
      "위험 인지, 거절 대응, 도움 요청! 이 세 가지로 네 대응을 차곡차곡 기록해둘게냥.",
  },
];

function TutorialPage() {
  const handleContinue = () => {
    window.location.href = "/episodes";
  };

  return (
    <main className="tutorial-page">
      <div className="tutorial-content">
        <div className="home-character-box">
          <img
            src={manyangIntro}
            alt="마냥이 캐릭터"
            className="home-character-img"
          />
        </div>

        <div className="home-bubble home-bubble--right">
          <p>
            안녕! 나는 마냥이다옹 😺
            <br />
            앞으로 몇 가지 상황을 보여줄거다옹.
            <br />
            정답을 맞히는 게임이 아니라 실제 상황에서 어떻게 대응할지
            직접 말해보는 연습이다옹.
          </p>
        </div>
      </div>

      <div className="tutorial-guide-row">
        <section className="tutorial-guide">
          {GUIDE_ITEMS.map((item) => (
            <div className="tutorial-guide-item" key={item.title}>
              <span className="tutorial-guide-icon" aria-hidden="true">
                {item.icon}
              </span>

              <h3 className="tutorial-guide-title">{item.title}</h3>
              <p className="tutorial-guide-desc">{item.description}</p>
            </div>
          ))}
        </section>

        <img
          src={manyangTutorial}
          alt=""
          aria-hidden="true"
          className="tutorial-decor"
        />
      </div>

      <button
        type="button"
        className="home-start-button"
        onClick={handleContinue}
      >
        이해했어(계속하기)!
      </button>

      <p className="tutorial-privacy-note">
        * 여기서 나눈 대화는 따로 저장되지 않으니 편하게 연습해보세요. *
      </p>
    </main>
  );
}

export default TutorialPage;
