const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(BASE + path, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? res.statusText)
  }
  return res.json()
}

function post(path, body) {
  return request(BASE ? path : path, {
    method: 'POST',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
}

function put(path, body) {
  return request(path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export const api = {
  startCycle:      () => post('/greenhouse/start'),
  stopCycle:       () => post('/greenhouse/stop'),
  toggleDevice:    (id) => post(`/devices/${id}/toggle`),
  loadTulipPreset: () => post('/growth-plan/presets/tulips'),
  addSensor:       (body) => post('/sensors/', body),
  addDevice:       (body) => post('/devices/', body),
  setGrowthPlan:   (body) => post('/growth-plan/', body),
  updateSchedule:  (day, body) => put(`/growth-plan/schedule/${day}`, body),
}
