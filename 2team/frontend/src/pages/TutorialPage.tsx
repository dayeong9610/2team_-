import { useNavigate } from "react-router-dom";

function TutorialPage() {

  const navigate = useNavigate();

  return (
    <div>

      <h1>안녕! 나는 마냥이야 😺</h1>

      <p>
        다양한 상황에서
        어떻게 대처할지 연습해보자.
      </p>

      <button
        onClick={() => navigate("/episodes")}
      >
        계속하기
      </button>

    </div>
  );
}

export default TutorialPage;