const CONFIG = {
  temperature_air:   { bg: '#546e7a', label: '°C' },
  temperature_water: { bg: '#00838f', label: '°C' },
  humidity:          { bg: '#1565c0', label: '%' },
  ph:                { bg: '#b71c1c', label: '' },
  light:             { bg: '#f57f17', label: 'lux' },
  nutrient:          { bg: '#2e7d32', label: 'mg/L' },
}

export function SensorIcon({ sensor, ghWidth = 10, ghHeight = 8 }) {
  const cfg = CONFIG[sensor.type] ?? { bg: '#888', label: '' }
  const isAlert = sensor.is_alert

  const left = `${(sensor.position.x / ghWidth) * 100}%`
  const top  = `${(sensor.position.y / ghHeight) * 100}%`

  const displayVal =
    sensor.type === 'ph'
      ? sensor.current_value.toFixed(1)
      : sensor.type === 'light'
        ? Math.round(sensor.current_value / 1000) + 'k'
      : Math.round(sensor.current_value) + cfg.label

  return (
    <div
      title={`${sensor.type}\n${sensor.current_value} ${sensor.unit}`}
      style={{
        position:  'absolute',
        left,
        top,
        transform: 'translate(-50%, -50%)',
        width:  46,
        height: 46,
        borderRadius: '50%',
        background: cfg.bg,
        border: isAlert ? '3px solid #ff1744' : '2px solid rgba(255,255,255,0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#fff',
        fontSize: 11,
        fontWeight: 700,
        cursor: 'default',
        boxShadow: isAlert
          ? '0 0 0 4px rgba(255,23,68,0.35)'
          : '0 2px 6px rgba(0,0,0,0.3)',
        animation: isAlert ? 'pulse 1s infinite' : 'none',
        zIndex: 10,
        userSelect: 'none',
      }}
    >
      {displayVal}
    </div>
  )
}
