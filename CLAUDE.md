# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Educational prototype of an automated hydroponics greenhouse management system. FastAPI backend + React/Vite frontend, communicating via REST and WebSocket.

## Running the project

**Backend** (from repo root):
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
Swagger UI: `http://localhost:8000/docs`

**Frontend** (from `frontend/`):
```bash
npm install   # first time only
npm run dev
```
UI: `http://localhost:5173` — Vite proxies `/api` and `/ws` to `localhost:8000`.

## Validation

```bash
python -m compileall app          # syntax check
cd frontend && npm run lint       # ESLint
cd frontend && npm run build      # production build check
```

No automated test suite exists.

## Architecture

### Backend (`app/`)

Uses **uv** for dependency management (`pyproject.toml`). Requires Python ≥ 3.14.2.

**Layer structure:**
- `domain/` — pure Python business logic, no FastAPI imports
  - `greenhouse.py` — `Greenhouse` aggregate holding sensors and devices
  - `sensors.py` — `PassiveSensor` (random poll) and `ActiveSensor` (observer pattern with alert threshold)
  - `devices.py` — device classes (`Heater`, `AirConditioner`, `Humidifier`, `LightSource`, `FertilizerDispenser`, `NutrientDispenser`)
  - `growth_plan.py` — `GrowthPlan` with per-day `DaySchedule` and `ParameterRange`
  - `controller.py` — `GreenhouseController.tick()` reads sensor averages and switches devices based on the current schedule
- `schemas/` — Pydantic response models (separate from domain objects)
- `routers/` — FastAPI routers; each router accesses the greenhouse via `request.app.state.greenhouse`
- `state.py` — module-level singletons (`greenhouse`, `controller`); initialized via FastAPI lifespan; also contains the default greenhouse layout and the built-in tulip growing plan
- `main.py` — app entry point; runs a background `_control_loop` every 2 s that calls `controller.tick()` and broadcasts a JSON snapshot over WebSocket to all connected clients

**WebSocket flow:** The single `/ws` endpoint broadcasts the full greenhouse snapshot every 2 s. Clients send pings to keep the connection alive; no client-to-server commands over WS.

**State is in-memory only** — restarting the server resets everything to the default layout and tulip plan.

### Frontend (`frontend/`)

React 19 + Vite 8, no router, no state management library.

- `hooks/useGreenhouseWS.js` — connects to `/ws`, parses JSON snapshots into `state`
- `components/GreenhouseCanvas.jsx` — SVG canvas rendering sensors and devices at their `(x, y)` positions on a 10×8 m grid
- `components/Sidebar.jsx` — controls (start/stop cycle, add sensor/device, growth plan editor) that call REST endpoints via `api/greenhouse.js`
- `api/greenhouse.js` — thin wrappers over `fetch` for all REST calls

UI state is driven entirely by WebSocket pushes; REST calls don't need to trigger a re-render because the next WS snapshot arrives within 2 s.
