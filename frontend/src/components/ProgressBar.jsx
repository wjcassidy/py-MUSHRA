export default function ProgressBar({ current, total }) {
  const progress = total > 0 ? Math.round((current / total) * 100) : 0
  return (
    <div className="progress-bar">
      <span className="progress-bar__label">
        Page {current} of {total}
      </span>
      <div className="progress-bar__track">
        <div className="progress-bar__fill" style={{ width: `${progress}%` }} />
      </div>
    </div>
  )
}
