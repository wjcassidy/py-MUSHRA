export default function TransportControls({ isPlaying, disabled, onToggle, nextDisabled, nextReasons, onNext }) {
  return (
    <div className="side-controls">
      <button type="button" className="transport-button" disabled={disabled} onClick={onToggle}>
        {isPlaying ? 'Pause' : 'Play'}
      </button>
      <div className="next-button-wrap">
        <button type="button" className="next-button" disabled={nextDisabled} onClick={onNext}>
          Next
        </button>
        {nextDisabled && nextReasons?.length > 0 && (
          <div className="next-button-message">{nextReasons.join(' ')}</div>
        )}
      </div>
    </div>
  )
}
