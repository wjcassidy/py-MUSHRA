const BANDS = ['Excellent', 'Good', 'Fair', 'Poor', 'Bad']

export default function RatingSlider({ value, touched, onChange }) {
  return (
    <div className="rating-slider">
      <div className="rating-slider__bands">
        {BANDS.map((label) => (
          <div key={label} className="rating-slider__band">
            {label}
          </div>
        ))}
      </div>
      <div className="rating-slider__track">
        <input
          type="range"
          min={0}
          max={100}
          value={value}
          className={`rating-slider__input${touched ? ' rating-slider__input--touched' : ''}`}
          onInput={(e) => onChange(Number(e.target.value))}
        />
      </div>
    </div>
  )
}
