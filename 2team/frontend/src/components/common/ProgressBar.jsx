export default function ProgressBar({ ...props }) {
    const isMetric = "label" in props;
    const progress = isMetric
        ? props.progress
        : (props.currentStage / props.totalStages) * 100;
    return (<div className="progress-wrapper">
      <div className="progress-info">
        <span>
          {isMetric
            ? props.label
            : `STEP ${props.currentStage} / ${props.totalStages}`}
        </span>

        <span>{Math.round(progress)}%</span>
      </div>

      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progress}%` }}/>
      </div>
    </div>);
}
