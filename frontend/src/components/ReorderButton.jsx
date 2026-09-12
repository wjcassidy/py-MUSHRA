import { useState } from 'react'

export default function ReorderButton({ onClick, disabled }) {
  const [hovering, setHovering] = useState(false)

  return (
    <div
      className="reorder-button-wrap"
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      <button
        type="button"
        className="reorder-button"
        onClick={onClick}
        disabled={disabled}
        aria-label="Reorder stimuli"
      >
        <svg className="reorder-button__icon" viewBox="0 0 74 24" width="60" height="20" aria-hidden="true">
          <rect x="2" y="10" width="6" height="14" rx="1" fill="#fff" />
          <rect x="10" y="4" width="6" height="20" rx="1" fill="#fff" />
          <rect x="18" y="16" width="6" height="8" rx="1" fill="#fff" />

          <path
            d="M28 12 H44 M39 7 L44 12 L39 17"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          <rect x="50" y="16" width="6" height="8" rx="1" fill="#fff" />
          <rect x="58" y="10" width="6" height="14" rx="1" fill="#fff" />
          <rect x="66" y="4" width="6" height="20" rx="1" fill="#fff" />
        </svg>
      </button>
      {hovering && <div className="reorder-button-message">Reorder stimuli</div>}
    </div>
  )
}
