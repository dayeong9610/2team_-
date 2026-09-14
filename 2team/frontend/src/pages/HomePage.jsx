function HomePage() {
    const handleStart = () => {
        window.location.href = "/tutorial";
    };
    return (<main className="home-page">
      <h1>😺 마냥이</h1>

      <p>
        위험한 상황에서
        나를 지키는 방법을 연습해봐!
      </p>

      <p>
        실제 상황처럼 대화하며
        대응 능력을 키워보자.
      </p>

      <button onClick={handleStart}>
        시작하기
      </button>
    </main>);
}
export default HomePage;
