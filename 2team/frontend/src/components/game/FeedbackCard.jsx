export default function FeedbackCard({ userAnswer, scoreType, }) {
    return (<div className="feedback-card">

      <span className="feedback-label">
        나의 답변
      </span>

      <p>{userAnswer}</p>

      <div className="evaluation-target">
        이번 단계 평가 영역
        <strong>{scoreType}</strong>
      </div>

    </div>);
}
