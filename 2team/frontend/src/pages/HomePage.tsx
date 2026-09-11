import { useNavigate } from "react-router-dom";

function HomePage() {

  const navigate = useNavigate();

  return (
    <div>

      <h1>마냥이</h1>

      <p>
        위험한 상황에서
        나를 지키는 방법을 연습해봐!
      </p>

      <button
        onClick={() => navigate("/tutorial")}
      >
        시작하기
      </button>

    </div>
  );
}

export default HomePage;