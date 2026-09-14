interface ProgressBarProps {
  currentStage: number;
  totalStages: number;
}

export default function ProgressBar({
  currentStage,
  totalStages,
}: ProgressBarProps) {
  const progress = (currentStage / totalStages) * 100;

  return (
    <div className="progress-wrapper">
      <div className="progress-info">
        <span>
          STEP {currentStage} / {totalStages}
        </span>

        <span>{Math.round(progress)}%</span>
      </div>

      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}