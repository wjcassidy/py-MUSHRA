import { useLayoutEffect, useRef, useState } from 'react'

const MAX_SIZE = 88
const MIN_SIZE = 32
const GAP_RATIO = 20 / 88 // gap between buttons relative to button size
const PREFERRED_COLUMNS = 5
const PAGE_GAP = 40 // matches .familiarisation-page gap
const BOTTOM_MARGIN = 48 // room for the message under the Start test button
const SIDE_MARGIN = 48

// Picks the column count and button size that fit `count` square buttons into the
// available area at the largest size (capped at MAX_SIZE), preferring 5 columns on ties.
function fitGrid(count, width, height) {
  let best = { columns: Math.min(count, PREFERRED_COLUMNS), size: MIN_SIZE }
  for (let columns = 1; columns <= count; columns++) {
    const rows = Math.ceil(count / columns)
    const size = Math.min(
      MAX_SIZE,
      width / (columns + (columns - 1) * GAP_RATIO),
      height / (rows + (rows - 1) * GAP_RATIO),
    )
    const better =
      size > best.size + 0.5 ||
      (Math.abs(size - best.size) <= 0.5 &&
        Math.abs(columns - PREFERRED_COLUMNS) < Math.abs(best.columns - PREFERRED_COLUMNS))
    if (better) best = { columns, size }
  }
  return { columns: best.columns, size: Math.max(MIN_SIZE, Math.floor(best.size)) }
}

export default function FamiliarisationPage({ stimuli, selected, playing, played, onSelect, onContinue }) {
  const allPlayed = stimuli.length > 0 && stimuli.every((filename) => played.has(filename))

  const pageRef = useRef(null)
  const textRef = useRef(null)
  const buttonWrapRef = useRef(null)
  const [layout, setLayout] = useState({ columns: PREFERRED_COLUMNS, size: MAX_SIZE })

  useLayoutEffect(() => {
    function update() {
      const page = pageRef.current
      if (!page || stimuli.length === 0) return
      const width = page.clientWidth - 2 * SIDE_MARGIN
      const height =
        window.innerHeight -
        page.getBoundingClientRect().top -
        textRef.current.offsetHeight -
        buttonWrapRef.current.offsetHeight -
        2 * PAGE_GAP -
        BOTTOM_MARGIN
      setLayout(fitGrid(stimuli.length, width, height))
    }
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [stimuli.length])

  return (
    <div className="familiarisation-page" ref={pageRef}>
        <div className="familiarisation-text" ref={textRef}>
            <h1 className="familiarisation-page__title">Familiarisation</h1>
            <p className="familiarisation-page__subtitle">Please listen to each of the below examples.</p>
        </div>
      <div
        className="familiarisation-grid"
        style={{
          gridTemplateColumns: `repeat(${layout.columns}, ${layout.size}px)`,
          gap: `${Math.round(layout.size * GAP_RATIO)}px`,
          '--familiarisation-button-size': `${layout.size}px`,
        }}
      >
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
      <div className="primary-button-wrap" ref={buttonWrapRef}>
        <button type="button" className="primary-button" disabled={!allPlayed} onClick={onContinue}>
          Start test
        </button>
        {!allPlayed && (
          <div className="primary-button-message">Please listen to all examples before proceeding.</div>
        )}
      </div>
    </div>
  )
}
