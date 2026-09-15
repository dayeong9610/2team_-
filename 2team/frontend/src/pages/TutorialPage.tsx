function TutorialPage() {
  const handleContinue = () => {
    window.location.href = "/episodes";
  };

  return (
    <main className="page-container">
      <h1>안녕! 나는 마냥이야 😺</h1>

      <p>
          앞으로 몇 가지 상황을 보여줄게.
          <br />
          정답을 맞히는 게임이 아니라
          실제 상황에서 어떻게 대응할지
          직접 말해보는 연습이야.
      </p>

      <button onClick={handleContinue}>
          이해했어(계속하기)! 
      </button>
    </main>
  );
}

export default TutorialPage;