import { api } from '../api/greenhouse'

/* ── visual configs ────────────────────────────────────────────── */
const BOX_TYPES = new Set(['heater', 'air_conditioner'])

const COLORS = {
  heater:               { off: '#fff3e0', on: '#e65100', border: '#ff6d00', text: '#bf360c' },
  air_conditioner:      { off: '#e3f2fd', on: '#0277bd', border: '#039be5', text: '#01579b' },
  humidifier:           { off: '#f3e5f5', on: '#7b1fa2', border: '#ab47bc', text: '#4a148c' },
  fertilizer_dispenser: { off: '#fffde7', on: '#f9a825', border: '#fdd835', text: '#f57f17' },
  nutrient_dispenser:   { off: '#e8f5e9', on: '#2e7d32', border: '#66bb6a', text: '#1b5e20' },
  light_source:         { off: '#f5f5f5', on: '#ffd600', border: '#ffca28', text: '#e65100' },
}

const ICONS = {
  heater:               { off: '🔲', on: '🔥' },
  air_conditioner:      { off: '❄', on: '❄' },
  humidifier:           { off: '💧', on: '💧' },
  fertilizer_dispenser: { off: '⚡', on: '⚡' },
  nutrient_dispenser:   { off: 'N', on: 'N' },
  light_source:         { off: '☀', on: '☀' },
}

/* ── component ─────────────────────────────────────────────────── */
export function DeviceIcon({ device, ghWidth = 10, ghHeight = 8, onToggle }) {
  const cfg    = COLORS[device.type] ?? COLORS.heater
  const icon   = ICONS[device.type]
  const isOn   = device.is_on
  const isBox  = BOX_TYPES.has(device.type)

  const left = `${(device.position.x / ghWidth) * 100}%`
  const top  = `${(device.position.y / ghHeight) * 100}%`

  const sharedStyle = {
    position:  'absolute',
    left,
    top,
    transform: 'translate(-50%, -50%)',
    cursor:    'pointer',
    zIndex:    8,
    userSelect:'none',
    transition:'all .2s',
  }

  async function handleClick() {
    try {
      await api.toggleDevice(device.id)
      onToggle?.()
    } catch (e) {
      console.error(e)
    }
  }

  /* rectangular label boxes (heaters, ACs) */
  if (isBox) {
    const isAC = device.type === 'air_conditioner'
    return (
      <div
        title={`${device.name} — ${isOn ? 'вкл' : 'выкл'}\nНажмите для переключения`}
        onClick={handleClick}
        style={{
          ...sharedStyle,
          background:   isOn ? cfg.on : cfg.off,
          border:       `2px solid ${cfg.border}`,
          borderRadius: 6,
          padding:      isAC ? '18px 4px' : '4px 10px',
          fontSize:     11,
          fontWeight:   700,
          color:        isOn ? '#fff' : cfg.text,
          writingMode:  isAC ? 'vertical-rl' : 'horizontal-tb',
          boxShadow:    isOn ? `0 0 10px ${cfg.border}88` : '0 2px 4px rgba(0,0,0,.2)',
        }}
      >
        {device.name}
      </div>
    )
  }

  /* icon-based devices */
  const size = device.type === 'light_source' ? 36 : 32
  return (
    <div
      title={`${device.name} — ${isOn ? 'вкл' : 'выкл'}\nНажмите для переключения`}
      onClick={handleClick}
      style={{
        ...sharedStyle,
        width:      size,
        height:     size,
        fontSize:   size - 4,
        lineHeight: `${size}px`,
        textAlign:  'center',
        filter:     isOn ? 'none' : 'grayscale(80%) opacity(0.55)',
        drop: 'shadow',
        textShadow: isOn ? `0 0 8px ${cfg.border}` : 'none',
      }}
    >
      {isOn ? icon.on : icon.off}
    </div>
  )
}
