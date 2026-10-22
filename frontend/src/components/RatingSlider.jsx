import { useRef } from 'react'

// 6 major ticks evenly spanning 0-100, with two minor ticks between each pair.
const MAJOR_TICKS = 5
const SUBDIVISIONS = 5
const STEPS = (MAJOR_TICKS - 1) * SUBDIVISIONS
const TICKS = Array.from({ length: STEPS + 1 }, (_, i) => ({
  position: (i / STEPS) * 100,
  major: i % SUBDIVISIONS === 0,
}))

// Labels evenly spaced from the maximum (top) to the minimum (bottom).
const LABELS = ['Sounds the same', 'Very similar', 'Similar', 'Somewhat similar', 'Not at all similar']
const INTERVAL = 100 / (LABELS.length - 1)

export default function RatingSlider({ value, touched, active, onChange, onActivate }) {
  const trackRef = useRef(null)
  const dragRef = useRef(null)

  function handlePointerDown(e) {
    const track = trackRef.current
    if (!track) return
    if (!active) onActivate()
    track.setPointerCapture(e.pointerId)
    // Drag is relative to the thumb's current position -- clicking the track
    // never jumps the value to the click point.
    dragRef.current = {
      startY: e.clientY,
      startValue: value,
      height: track.getBoundingClientRect().height,
    }
  }

  function handlePointerMove(e) {
    if (!dragRef.current) return
    const { startY, startValue, height } = dragRef.current
    const deltaValue = ((startY - e.clientY) / height) * 100
    const next = Math.min(100, Math.max(0, startValue + deltaValue))
    onChange(Math.round(next))
  }

  function endDrag(e) {
    if (dragRef.current && trackRef.current?.hasPointerCapture(e.pointerId)) {
      trackRef.current.releasePointerCapture(e.pointerId)
    }
    dragRef.current = null
  }

  return (
    <div className={`rating-slider${active ? ' rating-slider--active' : ''}`}>
      <div className="rating-slider__scale">
        {LABELS.map((label, i) => (
          <div
            key={label}
            className="rating-slider__label"
            style={{ bottom: `${100 - i * INTERVAL}%` }}
          >
            {label}
          </div>
        ))}
      </div>
      <div className="rating-slider__ticks" aria-hidden="true">
        {TICKS.map(({ position, major }) => (
          <div
            key={position}
            className={`rating-slider__tick${major ? ' rating-slider__tick--major' : ''}`}
            style={{ bottom: `${position}%` }}
          />
        ))}
      </div>
      <div
        ref={trackRef}
        className="rating-slider__track"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
      >
        <div className="rating-slider__fill" style={{ height: `${value}%` }} />
        <div
          className={`rating-slider__thumb${touched ? ' rating-slider__thumb--touched' : ''}`}
          style={{ bottom: `${value}%` }}
        />
      </div>
    </div>
  )
}
