import manyangIntro from "../assets/마냥_기본.png";

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

          <button
            type="button"
            className="home-start-button"
            onClick={handleContinue}
          >
            이해했어(계속하기)!
          </button>
        </div>
      </div>

      <p className="tutorial-privacy-note">
        * 여기서 나눈 대화는 따로 저장되지 않으니 편하게 연습해보세요. *
      </p>
    </main>
  );
}

export default TutorialPage;