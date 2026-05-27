import { SensorIcon } from './SensorIcon'
import { DeviceIcon } from './DeviceIcon'

const GH_W = 10
const GH_H = 8

export function GreenhouseCanvas({ ghState, onToggle }) {
  const sensors = ghState?.sensors ?? []
  const devices = ghState?.devices ?? []

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <div
        style={{
          position:     'relative',
          width:        '100%',
          aspectRatio:  `${GH_W} / ${GH_H}`,
          background:   'linear-gradient(160deg, #f1f8e9 0%, #e8f5e9 100%)',
          border:       '3px solid #388e3c',
          borderRadius: 10,
          overflow:     'hidden',
          boxShadow:    '0 4px 24px rgba(56,142,60,0.15)',
        }}
      >
        {/* grid overlay */}
        <svg
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', opacity: 0.12 }}
          xmlns="http://www.w3.org/2000/svg"
        >
          {Array.from({ length: GH_W - 1 }, (_, i) => (
            <line
              key={`v${i}`}
              x1={`${((i + 1) / GH_W) * 100}%`} y1="0"
              x2={`${((i + 1) / GH_W) * 100}%`} y2="100%"
              stroke="#2e7d32" strokeWidth="1"
            />
          ))}
          {Array.from({ length: GH_H - 1 }, (_, i) => (
            <line
              key={`h${i}`}
              x1="0" y1={`${((i + 1) / GH_H) * 100}%`}
              x2="100%" y2={`${((i + 1) / GH_H) * 100}%`}
              stroke="#2e7d32" strokeWidth="1"
            />
          ))}
        </svg>

        {devices.map(d => (
          <DeviceIcon
            key={d.id}
            device={d}
            ghWidth={GH_W}
            ghHeight={GH_H}
            onToggle={onToggle}
          />
        ))}

        {sensors.map(s => (
          <SensorIcon
            key={s.id}
            sensor={s}
            ghWidth={GH_W}
            ghHeight={GH_H}
          />
        ))}
      </div>
    </div>
  )
}
