export default function IdlePrompt({ onDismiss }) {
  return (
    <div className="call-overlay" onClick={onDismiss}>
      <div className="call-panel">
        No interaction registered for one minute. Please tap anywhere to dismiss, otherwise the researcher will check on you
        soon.
      </div>
    </div>
  )
}
