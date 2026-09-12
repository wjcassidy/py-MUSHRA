import { useEffect, useState } from 'react'
import { api } from './api'
import StimulusButton from './components/StimulusButton'
import RatingSlider from './components/RatingSlider'
import TransportControls from './components/TransportControls'
import ProgressBar from './components/ProgressBar'
import DeviceSelector from './components/DeviceSelector'
import ReorderButton from './components/ReorderButton'
import WelcomePage from './components/WelcomePage'
import FamiliarisationPage from './components/FamiliarisationPage'
import './App.css'

export default function App() {
  const [stage, setStage] = useState('welcome')

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

  const [familiarisationStimuli, setFamiliarisationStimuli] = useState([])
  const [familiarisationSelected, setFamiliarisationSelected] = useState(null)
  const [familiarisationPlaying, setFamiliarisationPlaying] = useState(false)
  const [familiarisationPlayed, setFamiliarisationPlayed] = useState(() => new Set())

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

    api
      .getFamiliarisationStimuli()
      .then((data) => setFamiliarisationStimuli(data.stimuli))
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

  function handleFamiliarisationSelect(filename) {
    if (filename === familiarisationSelected && familiarisationPlaying) {
      api
        .pause()
        .then(() => setFamiliarisationPlaying(false))
        .catch((err) => setError(err.message))
      return
    }
    api
      .selectFamiliarisation(filename)
      .then(() => {
        setFamiliarisationSelected(filename)
        setFamiliarisationPlaying(true)
        setFamiliarisationPlayed((played) => new Set(played).add(filename))
      })
      .catch((err) => setError(err.message))
  }

  function handleFamiliarisationContinue() {
    api
      .pause()
      .then(() => {
        setFamiliarisationPlaying(false)
        setStage('test')
      })
      .catch((err) => setError(err.message))
  }

  if (error) {
    return <div className="status-screen status-screen--error">Error: {error}</div>
  }

  if (stage === 'welcome') {
    return <WelcomePage onStart={() => setStage('familiarisation')} />
  }

  if (stage === 'familiarisation') {
    return (
      <FamiliarisationPage
        stimuli={familiarisationStimuli}
        selected={familiarisationSelected}
        playing={familiarisationPlaying}
        played={familiarisationPlayed}
        onSelect={handleFamiliarisationSelect}
        onContinue={handleFamiliarisationContinue}
      />
    )
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
  const hasTopRating = evalLetters.some((l) => ratings[l] === 100)
  const nextDisabled = !allTouched || !hasTopRating
  const nextReasons = []
  if (!allTouched) nextReasons.push('Please adjust every slider.\n')
  if (!hasTopRating) nextReasons.push('Rate at least one stimulus at 100.')

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
              nextDisabled={nextDisabled}
              nextReasons={nextReasons}
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
