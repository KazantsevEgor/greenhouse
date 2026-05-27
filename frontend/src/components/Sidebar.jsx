import { useState } from 'react'
import { api } from '../api/greenhouse'

const LEGEND = [
  { color: '#546e7a', shape: 'circle', label: 'Датчик температуры воздуха' },
  { color: '#00838f', shape: 'circle', label: 'Датчик температуры воды' },
  { color: '#1565c0', shape: 'circle', label: 'Датчик влажности воздуха' },
  { color: '#b71c1c', shape: 'circle', label: 'Датчик кислотности (pH)' },
  { color: '#f57f17', shape: 'circle', label: 'Датчик освещенности' },
  { color: '#2e7d32', shape: 'circle', label: 'Датчик питательных веществ' },
  { color: '#e65100', shape: 'box',    label: 'Обогреватель' },
  { color: '#0277bd', shape: 'box',    label: 'Кондиционер' },
  { color: '#7b1fa2', shape: 'circle', label: 'Увлажнитель 💧' },
  { color: '#ffd600', shape: 'circle', label: 'Источник освещения ☀' },
  { color: '#f9a825', shape: 'circle', label: 'Дозатор удобрений ⚡' },
  { color: '#2e7d32', shape: 'circle', label: 'Дозатор питательного раствора' },
]

const SENSOR_OPTIONS = [
  ['temperature_air', 'Температура воздуха', 18, 32, 25, 2],
  ['temperature_water', 'Температура воды', 16, 28, 22, 2],
  ['humidity', 'Влажность', 80, 100, 90, 5],
  ['ph', 'pH', 4.5, 7.5, 6, 0.5],
  ['light', 'Освещенность', 0, 12000, 8000, 1500],
  ['nutrient', 'Питательные вещества', 500, 1300, 900, 150],
]

const DEVICE_OPTIONS = [
  ['heater', 'Обогреватель'],
  ['air_conditioner', 'Кондиционер'],
  ['humidifier', 'Увлажнитель'],
  ['fertilizer_dispenser', 'Дозатор удобрений'],
  ['nutrient_dispenser', 'Дозатор питательного раствора'],
  ['light_source', 'Источник освещения'],
]

function avg(sensors, type) {
  const filtered = sensors.filter(s => s.type === type)
  if (!filtered.length) return null
  return (filtered.reduce((s, x) => s + x.current_value, 0) / filtered.length).toFixed(1)
}

export function Sidebar({ ghState, connected, onAction }) {
  const plan    = ghState?.growth_plan
  const sensors = ghState?.sensors ?? []
  const running = ghState?.is_running ?? false
  const [sensorForm, setSensorForm] = useState({
    type: 'temperature_air',
    mode: 'passive',
    x: 5,
    y: 4,
  })
  const [deviceForm, setDeviceForm] = useState({
    type: 'heater',
    x: 5,
    y: 4,
  })
  const [planForm, setPlanForm] = useState({
    cropName: 'Тюльпаны',
    totalDays: 90,
    lightHours: 16,
    tempDayMin: 26,
    tempDayMax: 30,
    tempNightMin: 20,
    tempNightMax: 24,
    humidityMin: 85,
    humidityMax: 95,
    phMin: 5.5,
    phMax: 6.5,
    nutrientMin: 800,
    nutrientMax: 1200,
  })

  const avgTemp     = avg(sensors, 'temperature_air')
  const avgWater    = avg(sensors, 'temperature_water')
  const avgHumidity = avg(sensors, 'humidity')
  const avgPh       = avg(sensors, 'ph')
  const avgLight    = avg(sensors, 'light')
  const avgNutrient = avg(sensors, 'nutrient')

  const schedule = plan?.current_schedule

  async function handleStart() {
    try { await api.startCycle(); onAction() } catch (e) { alert(e.message) }
  }
  async function handleStop() {
    try { await api.stopCycle(); onAction() } catch (e) { alert(e.message) }
  }
  async function handleLoadTulips() {
    try { await api.loadTulipPreset(); onAction() } catch (e) { alert(e.message) }
  }
  async function handleAddSensor(e) {
    e.preventDefault()
    const selected = SENSOR_OPTIONS.find(([type]) => type === sensorForm.type)
    const [, , min, max, target, threshold] = selected
    try {
      await api.addSensor({
        type: sensorForm.type,
        mode: sensorForm.mode,
        position: { x: Number(sensorForm.x), y: Number(sensorForm.y) },
        min_range: min,
        max_range: max,
        target: sensorForm.mode === 'active' ? target : null,
        threshold: sensorForm.mode === 'active' ? threshold : null,
      })
      onAction()
    } catch (e) { alert(e.message) }
  }
  async function handleAddDevice(e) {
    e.preventDefault()
    try {
      await api.addDevice({
        type: deviceForm.type,
        position: { x: Number(deviceForm.x), y: Number(deviceForm.y) },
      })
      onAction()
    } catch (e) { alert(e.message) }
  }
  async function handleSavePlan(e) {
    e.preventDefault()
    const body = buildPlan(planForm)
    try {
      await api.setGrowthPlan(body)
      onAction()
    } catch (e) { alert(e.message) }
  }

  return (
    <aside style={{
      width: 260,
      flexShrink: 0,
      display: 'flex',
      flexDirection: 'column',
      gap: 14,
      fontSize: 13,
    }}>

      {/* connection */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '8px 12px',
        borderRadius: 8,
        background: connected ? '#e8f5e9' : '#fce4ec',
        border: `1px solid ${connected ? '#a5d6a7' : '#f48fb1'}`,
        fontWeight: 600,
      }}>
        <span style={{ fontSize: 10, color: connected ? '#2e7d32' : '#c62828' }}>●</span>
        {connected ? 'WebSocket подключён' : 'Нет соединения…'}
      </div>

      {/* controls */}
      <section style={card}>
        <h3 style={cardTitle}>Управление</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <button style={btn('#2e7d32')} onClick={handleStart} disabled={running}>
            ▶ Запустить цикл
          </button>
          <button style={btn('#c62828')} onClick={handleStop} disabled={!running}>
            ⏹ Остановить
          </button>
          <button style={btn('#6a1b9a')} onClick={handleLoadTulips}>
            🌷 Загрузить план тюльпанов
          </button>
        </div>
      </section>

      {/* growing plan */}
      {plan && (
        <section style={card}>
          <h3 style={cardTitle}>🌱 {plan.crop_name}</h3>
          <Row label="Начало"   value={new Date(plan.start_date).toLocaleDateString('ru')} />
          <Row label="Прошло"   value={`${plan.elapsed_days} сут. ${plan.elapsed_hours} ч.`} />
          <Row label="День"     value={`${plan.current_day}`} />
          <Row label="Режим"    value={running ? '🟢 Активен' : '⏸ Пауза'} />
          {schedule && (
            <>
              <div style={{ borderTop: '1px solid #e0e0e0', marginTop: 8, paddingTop: 8 }}>
                <b>Расписание дня:</b>
              </div>
              <Row label="Свет"      value={`${schedule.light_hours} ч.`} />
              <Row label="Фаза"      value={schedule.is_light_time ? '☀ День' : '🌙 Ночь'} />
              <Row label="t° цель"
                value={schedule.is_light_time
                  ? `${schedule.temperature_day.min_val}–${schedule.temperature_day.max_val} °C`
                  : `${schedule.temperature_night.min_val}–${schedule.temperature_night.max_val} °C`}
              />
              <Row label="Влажность" value={`${schedule.humidity.min_val}–${schedule.humidity.max_val} %`} />
              <Row label="pH цель"   value={`${schedule.ph.min_val}–${schedule.ph.max_val}`} />
            </>
          )}
        </section>
      )}

      {/* sensor averages */}
      <section style={card}>
        <h3 style={cardTitle}>Показания датчиков</h3>
        <SensorRow color="#546e7a" label="Температура воздуха" value={avgTemp} unit="°C" />
        <SensorRow color="#00838f" label="Температура воды"    value={avgWater} unit="°C" />
        <SensorRow color="#1565c0" label="Влажность"           value={avgHumidity} unit="%" />
        <SensorRow color="#b71c1c" label="Кислотность (pH)"    value={avgPh} unit="" />
        <SensorRow color="#f57f17" label="Освещенность"        value={avgLight} unit="lux" />
        <SensorRow color="#2e7d32" label="Питательные вещества" value={avgNutrient} unit="mg/L" />
      </section>

      <section style={card}>
        <h3 style={cardTitle}>Размещение</h3>
        <form onSubmit={handleAddSensor} style={formGrid}>
          <select
            style={input}
            value={sensorForm.type}
            onChange={e => setSensorForm({ ...sensorForm, type: e.target.value })}
          >
            {SENSOR_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          <select
            style={input}
            value={sensorForm.mode}
            onChange={e => setSensorForm({ ...sensorForm, mode: e.target.value })}
          >
            <option value="passive">Пассивный</option>
            <option value="active">Активный</option>
          </select>
          <NumberInput label="x" value={sensorForm.x} onChange={x => setSensorForm({ ...sensorForm, x })} />
          <NumberInput label="y" value={sensorForm.y} onChange={y => setSensorForm({ ...sensorForm, y })} />
          <button style={btn('#1565c0')} type="submit">Добавить датчик</button>
        </form>

        <form onSubmit={handleAddDevice} style={{ ...formGrid, marginTop: 10 }}>
          <select
            style={input}
            value={deviceForm.type}
            onChange={e => setDeviceForm({ ...deviceForm, type: e.target.value })}
          >
            {DEVICE_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          <NumberInput label="x" value={deviceForm.x} onChange={x => setDeviceForm({ ...deviceForm, x })} />
          <NumberInput label="y" value={deviceForm.y} onChange={y => setDeviceForm({ ...deviceForm, y })} />
          <button style={btn('#6a1b9a')} type="submit">Добавить устройство</button>
        </form>
      </section>

      <section style={card}>
        <h3 style={cardTitle}>Настройка плана</h3>
        <form onSubmit={handleSavePlan} style={formGrid}>
          <input
            style={input}
            value={planForm.cropName}
            onChange={e => setPlanForm({ ...planForm, cropName: e.target.value })}
          />
          <NumberInput label="дней" value={planForm.totalDays} onChange={totalDays => setPlanForm({ ...planForm, totalDays })} />
          <NumberInput label="свет, ч" value={planForm.lightHours} onChange={lightHours => setPlanForm({ ...planForm, lightHours })} />
          <RangeInputs label="день °C" minKey="tempDayMin" maxKey="tempDayMax" form={planForm} setForm={setPlanForm} />
          <RangeInputs label="ночь °C" minKey="tempNightMin" maxKey="tempNightMax" form={planForm} setForm={setPlanForm} />
          <RangeInputs label="влажн. %" minKey="humidityMin" maxKey="humidityMax" form={planForm} setForm={setPlanForm} />
          <RangeInputs label="pH" minKey="phMin" maxKey="phMax" form={planForm} setForm={setPlanForm} />
          <RangeInputs label="питание" minKey="nutrientMin" maxKey="nutrientMax" form={planForm} setForm={setPlanForm} />
          <button style={btn('#2e7d32')} type="submit">Сохранить план</button>
        </form>
      </section>

      {/* legend */}
      <section style={card}>
        <h3 style={cardTitle}>Обозначения</h3>
        {LEGEND.map(l => (
          <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
            <LegendMark color={l.color} shape={l.shape} />
            <span>{l.label}</span>
          </div>
        ))}
      </section>
    </aside>
  )
}

/* ── small helpers ───────────────────────────────────────────────── */

function Row({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
      <span style={{ color: '#666' }}>{label}</span>
      <span style={{ fontWeight: 600 }}>{value}</span>
    </div>
  )
}

function SensorRow({ color, label, value, unit }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
      <span style={{
        width: 10, height: 10, borderRadius: '50%',
        background: color, flexShrink: 0,
      }} />
      <span style={{ flex: 1, color: '#555' }}>{label}</span>
      <span style={{ fontWeight: 700 }}>
        {value != null ? `${value} ${unit}` : '—'}
      </span>
    </div>
  )
}

function NumberInput({ label, value, onChange }) {
  return (
    <label style={fieldLabel}>
      {label}
      <input
        style={input}
        type="number"
        step="0.1"
        value={value}
        onChange={e => onChange(e.target.value)}
      />
    </label>
  )
}

function RangeInputs({ label, minKey, maxKey, form, setForm }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 70px 70px', gap: 6, alignItems: 'center' }}>
      <span style={{ color: '#666' }}>{label}</span>
      <input
        style={input}
        type="number"
        step="0.1"
        value={form[minKey]}
        onChange={e => setForm({ ...form, [minKey]: e.target.value })}
      />
      <input
        style={input}
        type="number"
        step="0.1"
        value={form[maxKey]}
        onChange={e => setForm({ ...form, [maxKey]: e.target.value })}
      />
    </div>
  )
}

function buildPlan(form) {
  const range = (min, max) => ({
    min_val: Number(min),
    max_val: Number(max),
    target: (Number(min) + Number(max)) / 2,
  })
  const schedule = {
    day: 1,
    temperature_day: range(form.tempDayMin, form.tempDayMax),
    temperature_night: range(form.tempNightMin, form.tempNightMax),
    light_hours: Number(form.lightHours),
    humidity: range(form.humidityMin, form.humidityMax),
    ph: range(form.phMin, form.phMax),
    nutrient: range(form.nutrientMin, form.nutrientMax),
  }

  return {
    crop_name: form.cropName,
    start_date: new Date().toISOString(),
    total_days: Number(form.totalDays),
    schedule: [schedule],
  }
}

function LegendMark({ color, shape }) {
  return (
    <span style={{
      width: 14, height: 14, flexShrink: 0,
      borderRadius: shape === 'circle' ? '50%' : 3,
      background: color,
      display: 'inline-block',
    }} />
  )
}

function btn(color) {
  return {
    padding: '8px 12px',
    borderRadius: 6,
    border: 'none',
    background: color,
    color: '#fff',
    fontWeight: 600,
    cursor: 'pointer',
    fontSize: 13,
    opacity: 1,
  }
}

const card = {
  background: '#fff',
  border: '1px solid #e0e0e0',
  borderRadius: 10,
  padding: '12px 14px',
}

const cardTitle = {
  margin: '0 0 10px',
  fontSize: 13,
  fontWeight: 700,
  color: '#2e7d32',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
}

const formGrid = {
  display: 'grid',
  gap: 6,
}

const input = {
  width: '100%',
  boxSizing: 'border-box',
  border: '1px solid #cfd8dc',
  borderRadius: 6,
  padding: '6px 8px',
  fontSize: 12,
}

const fieldLabel = {
  display: 'grid',
  gridTemplateColumns: '42px 1fr',
  gap: 6,
  alignItems: 'center',
  color: '#666',
}
