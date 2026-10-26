// Session-time window (minutes) whose expected progress is highlighted on the bar.
const EXPECTED_WINDOW_MINUTES = [12.5, 17.5]
// Shifts the estimate right of a straight time-proportional estimate, as
// participants tend to speed up once warmed up to the task.
const WARM_UP_SKEW = 0.95

export default function ProgressBar({ current, total, expectedCompletionTime }) {
  const progress = total > 0 ? Math.round((current / total) * 100) : 0

  let expected = null
  if (expectedCompletionTime > 0) {
    const [start, end] = EXPECTED_WINDOW_MINUTES.map((m) => Math.min(100, (m / expectedCompletionTime) * WARM_UP_SKEW * 100))
    if (start < 100) expected = { start, end }
  }

  return (
    <div className="progress-bar">
      <span className="progress-bar__label">
        Page {current} of {total}
      </span>
      <div className="progress-bar__track-wrap">
        <div className="progress-bar__track">
          <div className="progress-bar__fill" style={{ width: `${progress}%` }} />
        </div>
        {expected && (
          <>
            <div
              className="progress-bar__expected"
              style={{ left: `${expected.start}%`, width: `${expected.end - expected.start}%` }}
            />
            <span
              className="progress-bar__expected-label"
              style={{ left: `${(expected.start + expected.end) / 2}%` }}
            >
              15 min. estimate
            </span>
          </>
        )}
      </div>
    </div>
  )
}
