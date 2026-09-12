export default function FamiliarisationPage({ stimuli, selected, playing, onSelect, onContinue }) {
  return (
    <div className="familiarisation-page">
      <h1 className="familiarisation-page__title">Familiarisation</h1>
      <div className="familiarisation-grid">
        {stimuli.map((filename) => (
          <button
            key={filename}
            type="button"
            title={filename}
            className={`familiarisation-button${
              selected === filename && playing ? ' familiarisation-button--active' : ''
            }`}
            onClick={() => onSelect(filename)}
          >
            {filename.replace(/\.wav$/i, '')}
          </button>
        ))}
      </div>
      <button type="button" className="primary-button" onClick={onContinue}>
        Start test
      </button>
    </div>
  )
}
