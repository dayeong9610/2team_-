import ProgressBar from '../components/common/ProgressBar';

const mockResult = {
  riskAwareness: 80,
  refusal: 90,
  helpRequest: 70,
};

function ResultPage() {
  return (
    <div>
      <h1>Episode Complete!</h1>

      <p>거절 단호함: {mockResult.refusal}</p>
      <p>위험 인지: {mockResult.riskAwareness}</p>
      <p>도움 요청: {mockResult.helpRequest}</p>

      <ProgressBar
        label="위험 인지"
        progress={mockResult.riskAwareness}
      />

      <ProgressBar
        label="거절 대응"
        progress={mockResult.refusal}
      />

      <ProgressBar
        label="도움 요청"
        progress={mockResult.helpRequest}
      />
    </div>
  );
}

export default ResultPage;