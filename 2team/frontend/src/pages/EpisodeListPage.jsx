function EpisodeListPage() {
    const handleEpisodeClick = () => {
        window.location.href = "/play/EP01";
    };
    return (<div>

      <h1>오늘은 어떤 상황을 연습해볼까?</h1>

      <button onClick={handleEpisodeClick}>
        Episode 01
        시험기간 스터디 그룹
      </button>

      <button disabled>
        Episode 02
      </button>

      <button disabled>
        Episode 03
      </button>

    </div>);
}
export default EpisodeListPage;
