export default function WelcomePage({ onStart }) {
  return (
    <div className="status-screen">
      <h1>Active Acoustics Listening Test</h1>
      <button type="button" className="primary-button" onClick={onStart}>
        Begin
      </button>
    </div>
  )
}
