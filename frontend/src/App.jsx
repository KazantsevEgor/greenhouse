import { useCallback } from 'react'
import { useGreenhouseWS } from './hooks/useGreenhouseWS'
import { GreenhouseCanvas } from './components/GreenhouseCanvas'
import { Sidebar } from './components/Sidebar'

export default function App() {
  const { state, connected } = useGreenhouseWS()

  // Sidebar actions don't need a forced reload —
  // the WebSocket will push an updated snapshot within 2 s.
  const handleAction = useCallback(() => {}, [])

  const plan = state?.growth_plan

  return (
    <div style={{
      minHeight: '100vh',
      background: '#f0f4f0',
      fontFamily: "'Segoe UI', system-ui, sans-serif",
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* ── header ── */}
      <header style={{
        background: 'linear-gradient(90deg, #1b5e20 0%, #2e7d32 100%)',
        color: '#fff',
        padding: '14px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>
            🌿 Автоматизированная система управления теплицей
          </h1>
          {plan && (
            <p style={{ margin: '4px 0 0', fontSize: 13, opacity: 0.85 }}>
              {plan.crop_name} · Начало цикла:{' '}
              {new Date(plan.start_date).toLocaleDateString('ru')} · Прошло:{' '}
              {plan.elapsed_days} сут. {plan.elapsed_hours} ч.
            </p>
          )}
        </div>
        <div style={{
          background: state?.is_running ? '#43a047' : '#757575',
          borderRadius: 20,
          padding: '4px 14px',
          fontSize: 13,
          fontWeight: 600,
        }}>
          {state?.is_running ? '🟢 Цикл активен' : '⏸ Остановлено'}
        </div>
      </header>

      {/* ── body ── */}
      <div style={{
        flex: 1,
        display: 'flex',
        gap: 20,
        padding: 20,
        alignItems: 'flex-start',
      }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <GreenhouseCanvas ghState={state} onToggle={handleAction} />
        </div>

        <Sidebar ghState={state} connected={connected} onAction={handleAction} />
      </div>
    </div>
  )
}
