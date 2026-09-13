import { useState } from 'react'

export default function FamiliarisationPage({ stimuli, selected, playing, played, onSelect, onContinue }) {
  const [hoveringContinue, setHoveringContinue] = useState(false)
  const allPlayed = stimuli.length > 0 && stimuli.every((filename) => played.has(filename))

  return (
    <div className="familiarisation-page">
        <div className="familiarisation-text">
            <h1 className="familiarisation-page__title">Familiarisation</h1>
            <p className="familiarisation-page__subtitle">Please listen to each of the below examples.</p>
        </div>
      <div className="familiarisation-grid">
        {stimuli.map((filename) => (
          <button
            key={filename}
            type="button"
            aria-label={filename}
            className={`familiarisation-button${
              selected === filename && playing ? ' familiarisation-button--active' : ''
            }${played.has(filename) ? ' familiarisation-button--played' : ''}`}
            onClick={() => onSelect(filename)}
          />
        ))}
      </div>
      <div
        className="primary-button-wrap"
        onMouseEnter={() => setHoveringContinue(true)}
        onMouseLeave={() => setHoveringContinue(false)}
      >
        <button type="button" className="primary-button" disabled={!allPlayed} onClick={onContinue}>
          Start test
        </button>
        {hoveringContinue && !allPlayed && (
          <div className="primary-button-message">Please listen to all examples before proceeding.</div>
        )}
      </div>
    </div>
  )
}
