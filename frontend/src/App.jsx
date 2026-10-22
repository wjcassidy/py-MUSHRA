import { useEffect, useRef, useState } from 'react'
import { api } from './api'
import StimulusButton from './components/StimulusButton'
import RatingSlider from './components/RatingSlider'
import TransportControls from './components/TransportControls'
import ProgressBar from './components/ProgressBar'
import DeviceSelector from './components/DeviceSelector'
import VolumeControl from './components/VolumeControl'
import ReorderButton from './components/ReorderButton'
import WelcomePage from './components/WelcomePage'
import FamiliarisationPage from './components/FamiliarisationPage'
import CallResearcher from './components/CallResearcher'
import IdlePrompt from './components/IdlePrompt'
import './App.css'

const IDLE_TIMEOUT_MS = 60_000

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
  const [channelStatus, setChannelStatus] = useState(null)
  const deviceRequestId = useRef(0)

  const [volume, setVolume] = useState(null)
  const volumeRequestId = useRef(0)

  const [familiarisationStimuli, setFamiliarisationStimuli] = useState([])
  const [familiarisationSelected, setFamiliarisationSelected] = useState(null)
  const [familiarisationPlaying, setFamiliarisationPlaying] = useState(false)
  const [familiarisationPlayed, setFamiliarisationPlayed] = useState(() => new Set())

  const [callActive, setCallActive] = useState(false)
  const [callAcknowledged, setCallAcknowledged] = useState(false)

  const [idle, setIdle] = useState(false)

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
      .then((data) => {
        setDevices(data.devices)
        setChannelStatus(data)
      })
      .catch((err) => setError(err.message))

    api
      .getVolume()
      .then(setVolume)
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
    const requestId = ++deviceRequestId.current
    api
      .setDevice(index)
      .then((data) => {
        if (requestId !== deviceRequestId.current) return // superseded by a later device change
        setChannelStatus(data)
        if (!data.error) {
          setDeviceIndex(index)
        }
      })
      .catch((err) => {
        if (requestId !== deviceRequestId.current) return
        setError(err.message)
      })
  }

  function handleVolumeChange(volumeDb) {
    const requestId = ++volumeRequestId.current
    setVolume((v) => ({ ...v, volume_db: volumeDb }))
    api
      .setVolume(volumeDb)
      .then((data) => {
        if (requestId !== volumeRequestId.current) return // superseded by a later volume change
        setVolume(data)
      })
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
      .then(() => api.finishFamiliarisation())
      .then(() => {
        setFamiliarisationPlaying(false)
        setVolume((v) => v && { ...v, locked: true })
        setStage('test')
      })
      .catch((err) => setError(err.message))
  }

  // Poll for the researcher pressing Enter in the backend terminal.
  useEffect(() => {
    if (!callActive || callAcknowledged) return
    const id = setInterval(() => {
      api
        .getResearcherCall()
        .then((data) => {
          if (data.active && data.acknowledged) setCallAcknowledged(true)
        })
        .catch((err) => setError(err.message))
    }, 1000)
    return () => clearInterval(id)
  }, [callActive, callAcknowledged])

  // Enter in the browser acknowledges the call, as Enter in the backend terminal does.
  useEffect(() => {
    if (!callActive || callAcknowledged) return
    function handleKeyDown(event) {
      if (event.key !== 'Enter') return
      event.preventDefault() // don't also "click" the focused Call researcher button
      api
        .acknowledgeResearcherCall()
        .then((data) => {
          if (data.active && data.acknowledged) setCallAcknowledged(true)
        })
        .catch((err) => setError(err.message))
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [callActive, callAcknowledged])

  // Show the idle prompt after a minute without any input. Listeners use the
  // capture phase so components that stop propagation still count as activity.
  // Only timed between passing the familiarisation page and completing the test,
  // and not while a researcher call is active, as the participant is already waiting.
  useEffect(() => {
    if (stage !== 'test' || completed || callActive) return
    const events = ['pointerdown', 'keydown', 'wheel']
    function goIdle() {
      setIdle(true)
      api.sendIdleAlert().catch((err) => setError(err.message))
    }
    let timer = setTimeout(goIdle, IDLE_TIMEOUT_MS)
    function restartTimer() {
      clearTimeout(timer)
      timer = setTimeout(goIdle, IDLE_TIMEOUT_MS)
    }
    events.forEach((type) => window.addEventListener(type, restartTimer, true))
    return () => {
      clearTimeout(timer)
      events.forEach((type) => window.removeEventListener(type, restartTimer, true))
    }
  }, [stage, completed, callActive])

  function handleCallToggle() {
    const active = !callActive
    setCallActive(active)
    setCallAcknowledged(false)
    if (active) {
      setIsPlaying(false)
      setFamiliarisationPlaying(false)
      api.pause().catch((err) => setError(err.message))
    }
    api.setResearcherCall(active).catch((err) => setError(err.message))
  }

  const deviceSelectorBar = (
    <header className="top-bar">
      <DeviceSelector
        devices={devices}
        selectedIndex={deviceIndex}
        onChange={handleDeviceChange}
        channelStatus={channelStatus}
        locked={stage !== 'welcome'}
      />
      <VolumeControl volume={volume} onChange={handleVolumeChange} />
      <CallResearcher active={callActive} acknowledged={callAcknowledged} onToggle={handleCallToggle} />
    </header>
  )

  const appShell = (children) => (
    <div className={`app${callActive ? ' app--call' : ''}`}>
      {deviceSelectorBar}
      {idle && !callActive && !completed && <IdlePrompt onDismiss={() => setIdle(false)} />}
      {children}
    </div>
  )

  if (error) {
    return appShell(
      <div className="status-screen status-screen--error">Error: {error}</div>
    )
  }

  if (stage === 'welcome') {
    return appShell(
      <WelcomePage onStart={() => setStage('familiarisation')} />
    )
  }

  if (stage === 'familiarisation') {
    return appShell(
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
    return appShell(
      <div className="status-screen">
        <h1>Test complete!</h1>
        <h2>Thank you for participating.</h2>
        {completed.csvFilename ? (
          <p>The researcher will enter shortly. You may lower the chair lift, but please do not jump down.</p>
        ) : (
          <p>This test session has already been completed.</p>
        )}
      </div>
    )
  }

  if (!page) {
    return appShell(
      <div className="status-screen">Loading…</div>
    )
  }

  const evalLetters = page.letters.filter((l) => l !== page.reference_letter)
  const displayLetters = letterOrder ?? evalLetters
  const allTouched = evalLetters.length > 0 && evalLetters.every((l) => touched[l])
  const hasTopRating = evalLetters.some((l) => ratings[l] === 100)
  const nextDisabled = !allTouched || !hasTopRating
  const nextReasons = []
  if (!allTouched) nextReasons.push('Please adjust every slider.\n')
  if (!hasTopRating) nextReasons.push('Rate at least one excerpt at the maximum.')

  return appShell(
    <>
      <main className="test-area">
        <h1 className="test-area__heading">Rate the similarity of the room in each excerpt to the reference room</h1>
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
    </>
  )
}
