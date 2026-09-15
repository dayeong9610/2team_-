import { mockResult } from "../../data/mockResult";

export default function FeedbackCard({ scoreType }) {
  return (
    <div className="feedback-card">
      <div className="evaluation-target">
        <div className="evaluation-target-label">
          <span className="evaluation-target-title">이번 단계 평가 영역</span>
          <strong className="evaluation-target-value">{scoreType}</strong>
        </div>

        <div className="evaluation-axes">
          <div className="mini-stat">
            <span className="mini-stat-label">위험 인지</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${mockResult.riskAwareness}%` }}
              />
            </div>
            <span className="mini-stat-value">
              {mockResult.riskAwareness}%
            </span>
          </div>

          <div className="mini-stat">
            <span className="mini-stat-label">거절 대응</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${mockResult.refusal}%` }}
              />
            </div>
            <span className="mini-stat-value">{mockResult.refusal}%</span>
          </div>

          <div className="mini-stat">
            <span className="mini-stat-label">도움 요청</span>
            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{ width: `${mockResult.helpRequest}%` }}
              />
            </div>
            <span className="mini-stat-value">{mockResult.helpRequest}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
