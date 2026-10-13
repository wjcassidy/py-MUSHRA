export default function CallResearcher({ active, acknowledged, onToggle }) {
  return (
    <>
      {active && (
        <div className="call-overlay">
          <div className="call-panel">
            {acknowledged && <div className="call-acknowledged">Researcher has acknowledged and is on their way</div>}
            Test paused - please wait for the researcher (toggle again to cancel)
          </div>
        </div>
      )}
      <button
        type="button"
        className={`call-button${active ? ' call-button--active' : ''}`}
        aria-pressed={active}
        onClick={onToggle}
      >
        Call researcher
      </button>
    </>
  )
}
