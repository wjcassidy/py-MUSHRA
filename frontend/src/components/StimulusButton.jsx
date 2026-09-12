export default function StimulusButton({ letter, label, active, onClick }) {
  return (
    <button
      type="button"
      className={`stimulus-button${active ? ' stimulus-button--active' : ''}`}
      onClick={() => onClick(letter)}
    >
      {label ?? letter}
    </button>
  )
}
