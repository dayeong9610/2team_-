function TutorialPage() {

  const handleContinue = () => {
    window.location.href = "/episodes";
  };

  return (
    <div>

      <h1>안녕! 나는 마냥이야 😺</h1>

      <p>
        다양한 상황에서
        어떻게 대처할지 연습해보자.
      </p>

      <button
        onClick={handleContinue}
      >
        계속하기
      </button>

    </div>
  );
}

export default TutorialPage;