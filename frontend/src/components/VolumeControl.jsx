import { useEffect, useState } from 'react'

export default function VolumeControl({ volume, onChange }) {
  const [draft, setDraft] = useState('')

  useEffect(() => {
    if (volume) setDraft(String(volume.volume_db))
  }, [volume?.volume_db])

  if (!volume) return null
  const { volume_db, min_db, max_db, locked } = volume

  function commitDraft() {
    const value = Number(draft)
    if (draft.trim() === '' || Number.isNaN(value)) {
      setDraft(String(volume_db))
      return
    }
    const clamped = Math.min(max_db, Math.max(min_db, value))
    setDraft(String(clamped))
    if (clamped !== volume_db) onChange(clamped)
  }

  return (
    <div
      className={`volume-control${locked ? ' volume-control--locked' : ''}`}
      title={locked ? 'Volume is locked for the test' : undefined}
    >
      <label htmlFor="volume-slider">Volume</label>
      <input
        id="volume-slider"
        type="range"
        min={min_db}
        max={max_db}
        step={0.5}
        value={volume_db}
        disabled={locked}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <input
        className="volume-control__input"
        type="number"
        min={min_db}
        max={max_db}
        step={0.5}
        value={draft}
        disabled={locked}
        aria-label="Volume (dB)"
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commitDraft}
        onKeyDown={(e) => {
          if (e.key === 'Enter') e.currentTarget.blur()
        }}
      />
      <span>dB</span>
      {locked && <span className="volume-control__lock">(locked)</span>}
    </div>
  )
}
