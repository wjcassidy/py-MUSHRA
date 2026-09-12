export default function WelcomePage({ onStart }) {
  return (
    <div className="status-screen">
      <h1>Welcome</h1>
      <p>You are about to begin a listening test.</p>
      <button type="button" className="primary-button" onClick={onStart}>
        Start
      </button>
    </div>
  )
}
