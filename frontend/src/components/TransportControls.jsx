import { useState } from 'react'

export default function TransportControls({ isPlaying, disabled, onToggle, nextDisabled, nextReasons, onNext }) {
  const [hoveringNext, setHoveringNext] = useState(false)

  return (
    <div className="side-controls">
      <button type="button" className="transport-button" disabled={disabled} onClick={onToggle}>
        {isPlaying ? 'Pause' : 'Play'}
      </button>
      <div
        className="next-button-wrap"
        onMouseEnter={() => setHoveringNext(true)}
        onMouseLeave={() => setHoveringNext(false)}
      >
        <button type="button" className="next-button" disabled={nextDisabled} onClick={onNext}>
          Next
        </button>
        {hoveringNext && nextDisabled && nextReasons?.length > 0 && (
          <div className="next-button-message">{nextReasons.join(' ')}</div>
        )}
      </div>
    </div>
  )
}
