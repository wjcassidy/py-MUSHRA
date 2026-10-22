import { useEffect, useState } from 'react'

export default function SessionClock({ startTime, running }) {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    if (!running) return
    setNow(Date.now())
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [running])

  const minutes = Math.max(0, Math.floor((now - startTime) / 60_000))
  return (
    <div className="session-clock">
      Session time: {minutes} {minutes === 1 ? 'minute' : 'minutes'}
    </div>
  )
}
