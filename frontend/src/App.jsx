import { useEffect, useState } from 'react'
import { api } from './api'
import StimulusButton from './components/StimulusButton'
import RatingSlider from './components/RatingSlider'
import TransportControls from './components/TransportControls'
import ProgressBar from './components/ProgressBar'
import DeviceSelector from './components/DeviceSelector'
import ReorderButton from './components/ReorderButton'
import './App.css'

export default function App() {
  const [page, setPage] = useState(null)
  const [completed, setCompleted] = useState(null)
  const [error, setError] = useState(null)

  const [selectedLetter, setSelectedLetter] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [ratings, setRatings] = useState({})
  const [touched, setTouched] = useState({})
  const [letterOrder, setLetterOrder] = useState(null)

  const [devices, setDevices] = useState([])
  const [deviceIndex, setDeviceIndex] = useState(null)

  useEffect(() => {
    api
      .getSession()
      .then((data) => {
        if (data.done) {
          setCompleted({ csvFilename: null })
        } else {
          setPage(data)
        }
      })
      .catch((err) => setError(err.message))

    api
      .getDevices()
      .then((data) => setDevices(data.devices))
      .catch((err) => setError(err.message))
  }, [])

  function resetPageState() {
    setSelectedLetter(null)
    setIsPlaying(false)
    setRatings({})
    setTouched({})
    setLetterOrder(null)
  }

  function handleSelect(letter) {
    if (letter === selectedLetter) {
      handleToggle()
      return
    }
    api
      .select(letter)
      .then(() => {
        setSelectedLetter(letter)
        setIsPlaying(true)
      })
      .catch((err) => setError(err.message))
  }

  function handleToggle() {
    const action = isPlaying ? api.pause() : api.play()
    action.then(() => setIsPlaying(!isPlaying)).catch((err) => setError(err.message))
  }

  function handleSliderChange(letter, value) {
    setRatings((r) => ({ ...r, [letter]: value }))
    setTouched((t) => ({ ...t, [letter]: true }))
  }

  function handleReorder() {
    setLetterOrder([...evalLetters].sort((a, b) => (ratings[a] ?? 50) - (ratings[b] ?? 50)))
  }

  function handleNext() {
    api
      .pause()
      .then(() => api.submitRatings(ratings))
      .then((resp) => {
        if (resp.done) {
          setCompleted({ csvFilename: resp.csv_filename })
          setPage(null)
        } else {
          setPage(resp.page)
          resetPageState()
        }
      })
      .catch((err) => setError(err.message))
  }

  function handleDeviceChange(index) {
    api
      .setDevice(index)
      .then(() => setDeviceIndex(index))
      .catch((err) => setError(err.message))
  }

  if (error) {
    return <div className="status-screen status-screen--error">Error: {error}</div>
  }

  if (completed) {
    return (
      <div className="status-screen">
        <h1>Test complete</h1>
        {completed.csvFilename ? (
          <p>Results saved to results/{completed.csvFilename}</p>
        ) : (
          <p>This test session has already been completed.</p>
        )}
      </div>
    )
  }

  if (!page) {
    return <div className="status-screen">Loading…</div>
  }

  const evalLetters = page.letters.filter((l) => l !== page.reference_letter)
  const displayLetters = letterOrder ?? evalLetters
  const allTouched = evalLetters.length > 0 && evalLetters.every((l) => touched[l])

  return (
    <div className="app">
      <header className="top-bar">
        <DeviceSelector devices={devices} selectedIndex={deviceIndex} onChange={handleDeviceChange} />
      </header>
      <main className="test-area">
        <h1 className="test-area__heading">Rate the similarity of each stimulus to the reference</h1>
        <div className="test-area__content">
          <div className="test-area__reference stimulus-column stimulus-column--reference">
            <StimulusButton
              letter={page.reference_letter}
              label="Reference"
              active={selectedLetter === page.reference_letter && isPlaying}
              onClick={handleSelect}
            />
          </div>
          <div className="stimuli-row">
            {displayLetters.map((letter) => (
              <div key={letter} className="stimulus-column">
                <StimulusButton
                  letter={letter}
                  active={selectedLetter === letter && isPlaying}
                  onClick={handleSelect}
                />
                <RatingSlider
                  value={ratings[letter] ?? 50}
                  touched={!!touched[letter]}
                  active={selectedLetter === letter}
                  onChange={(value) => handleSliderChange(letter, value)}
                  onActivate={() => handleSelect(letter)}
                />
              </div>
            ))}
          </div>
          <div className="test-area__right">
            <ReorderButton onClick={handleReorder} disabled={evalLetters.length < 2} />
            <TransportControls
              isPlaying={isPlaying}
              disabled={!selectedLetter}
              onToggle={handleToggle}
              nextDisabled={!allTouched}
              onNext={handleNext}
            />
          </div>
        </div>
      </main>
      <footer className="bottom-bar">
        <ProgressBar current={page.page_index + 1} total={page.total_pages} />
      </footer>
    </div>
  )
}
