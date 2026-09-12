export default function TransportControls({ isPlaying, disabled, onToggle, nextDisabled, onNext }) {
  return (
    <div className="side-controls">
      <button type="button" className="transport-button" disabled={disabled} onClick={onToggle}>
        {isPlaying ? 'Pause' : 'Play'}
      </button>
      <button type="button" className="next-button" disabled={nextDisabled} onClick={onNext}>
        Next
      </button>
    </div>
  )
}
