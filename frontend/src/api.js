const BASE = '/api'

async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request to ${path} failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  getSession: () => request('/session'),
  select: (letter) => request('/select', { method: 'POST', body: JSON.stringify({ letter }) }),
  play: () => request('/play', { method: 'POST' }),
  pause: () => request('/pause', { method: 'POST' }),
  getDevices: () => request('/audio-devices'),
  setDevice: (index) => request('/audio-device', { method: 'POST', body: JSON.stringify({ index }) }),
  submitRatings: (ratings) => request('/ratings', { method: 'POST', body: JSON.stringify({ ratings }) }),
  getFamiliarisationStimuli: () => request('/familiarisation-stimuli'),
  selectFamiliarisation: (filename) =>
    request('/familiarisation-select', { method: 'POST', body: JSON.stringify({ filename }) }),
}
