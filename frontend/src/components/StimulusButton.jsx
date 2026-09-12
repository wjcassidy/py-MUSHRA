export default function StimulusButton({ letter, active, onClick }) {
  return (
    <button
      type="button"
      className={`stimulus-button${active ? ' stimulus-button--active' : ''}`}
      onClick={() => onClick(letter)}
    >
      {letter}
    </button>
  )
}
