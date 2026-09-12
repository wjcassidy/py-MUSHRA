import { useRef } from 'react'

const BANDS = ['Excellent', 'Good', 'Fair', 'Poor', 'Bad']

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
      <div className="rating-slider__bands">
        {BANDS.map((label) => (
          <div key={label} className="rating-slider__band">
            {label}
          </div>
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
