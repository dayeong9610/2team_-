import { useNavigate } from "react-router-dom";

function EpisodeListPage() {

  const navigate = useNavigate();

  return (
    <div>

      <h1>오늘은 어떤 상황을 연습해볼까?</h1>

      <button
        onClick={() => navigate("/play/EP01")}
      >
        Episode 01
        시험기간 스터디 그룹
      </button>

      <button disabled>
        Episode 02
      </button>

      <button disabled>
        Episode 03
      </button>

    </div>
  );
}

export default EpisodeListPage;