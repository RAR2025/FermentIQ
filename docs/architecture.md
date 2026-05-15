
# FermentIQ — Architecture and Runbook

FermentIQ is a compact, self-contained project that provides real-time anomaly detection for fermentation processes. The system is composed of a Django REST backend that simulates fermentation sensor data, a pure-Python anomaly detection engine, and a Streamlit dashboard for visualization and operator interaction. The design prioritizes safety (no third-party AI APIs), transparency (pure Python logic), and ease of local deployment using SQLite.

Tech stack and rationale
- Python: single-language stack for backend and analysis code.
- Django + Django REST Framework: robust, well-supported API framework for data storage, endpoints, and admin utilities.
- Streamlit: fast dashboarding for operators and demonstrations.
- Plotly + pandas: visualization and tabular display in the dashboard.
- SQLite: lightweight, file-based database suitable for prototypes and demos.

Module descriptions
- `AnomalyEngine` (backend/monitor/anomaly_engine.py): a pure-Python comparison engine that evaluates tank sensor time series against an ideal signature using tolerance-band matching. Produces a similarity percentage, first deviation point, and per-point deviation details.
- `FermentationSimulator` (backend/monitor/simulator.py): generates realistic time series for temperature, pH, and dissolved oxygen for multiple tanks. Supports fault injection (spike, drift, stuck, random) for testing.
- `Django API` (backend/): exposes four endpoints — `/api/simulate/`, `/api/analyze/`, `/api/results/`, `/api/health/`. Simulation writes IdealSignature and TankReading records; analysis consumes them and stores AnalysisResult records.
- `Streamlit Dashboard` (dashboard/app.py + components): operator UI to run simulations, trigger analysis, view tank cards, sensor charts, alert banners, and read documentation.

How to run locally
1. Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
2. Dashboard (in a separate terminal)
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

API endpoints
- `GET /api/health/` — returns a simple JSON health object.
- `GET /api/simulate/` — runs the simulator, saves IdealSignature and TankReading rows, and returns the generated data.
- `GET /api/analyze/` — runs the anomaly engine against the latest readings, saves AnalysisResult rows, and returns analysis.
- `GET /api/results/` — returns stored AnalysisResult records.

Environment variables
- `SECRET_KEY` — Django secret key. Provide a secure value in production.
- `DEBUG` — `True` or `False`.
- `BACKEND_URL` — URL used by the Streamlit dashboard to contact the backend (default `http://localhost:8000`).

Embedded diagrams


System architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║                    FERMENTIQ SYSTEM ARCHITECTURE                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   ┌─────────────────┐         ┌──────────────────────────────────┐  ║
║   │   STREAMLIT     │  HTTP   │         DJANGO REST API          │  ║
║   │   DASHBOARD     │◄───────►│                                  │  ║
║   │  (Port 8501)    │  JSON   │  /api/simulate/  (GET)           │  ║
║   │                 │         │  /api/analyze/   (GET)           │  ║
║   │  - Tank Cards   │         │  /api/results/   (GET)           │  ║
║   │  - Plotly Charts│         │  /api/health/    (GET)           │  ║
║   │  - Alert Banners│         │                                  │  ║
║   └─────────────────┘         └──────────┬───────────────────────┘  ║
║                                          │                           ║
║                          ┌───────────────▼──────────────────────┐   ║
║                          │           CORE SERVICES              │   ║
║                          │                                      │   ║
║                          │  ┌─────────────────────────────────┐ │   ║
║                          │  │  FermentationSimulator          │ │   ║
║                          │  │  - Generates ideal signatures   │ │   ║
║                          │  │  - Injects fault types          │ │   ║
║                          │  │  - 3 sensors × N tanks          │ │   ║
║                          │  └────────────────┬────────────────┘ │   ║
║                          │                   │                   │   ║
║                          │  ┌────────────────▼────────────────┐ │   ║
║                          │  │  FermentationAnomalyEngine      │ │   ║
║                          │  │  - Tolerance band matching      │ │   ║
║                          │  │  - Similarity score (0–100%)    │ │   ║
║                          │  │  - First deviation detection    │ │   ║
║                          │  │  - Status classification        │ │   ║
║                          │  └────────────────┬────────────────┘ │   ║
║                          └───────────────────┼──────────────────┘   ║
║                                              │                       ║
║                          ┌───────────────────▼──────────────────┐   ║
║                          │           SQLITE DATABASE            │   ║
║                          │  IdealSignature | TankReading        │   ║
║                          │  AnalysisResult                      │   ║
║                          └──────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════╝
```

Data flow

```
DATA FLOW DIAGRAM — FERMENTIQ

USER CLICKS "Run Simulation"
	  │
	  ▼
Streamlit → GET /api/simulate/
	  │
	  ▼
Django: FermentationSimulator.get_ideal_signatures()
	  │  generates 3 × 72-point ideal curves
	  ▼
Django: FermentationSimulator.generate_all_tanks(N)
	  │  generates N × 3 × 72 readings with injected faults
	  ▼
Django: Saves to DB (IdealSignature, TankReading tables)
	  │
	  ▼
Returns JSON → Streamlit renders raw data

USER CLICKS "Analyze"
	  │
	  ▼
Streamlit → GET /api/analyze/
	  │
	  ▼
Django: Loads IdealSignature + TankReading from DB
	  │
	  ▼
Django: For each (tank × sensor):
	 FermentationAnomalyEngine.analyze_tank()
	 → tolerance band comparison
	 → similarity_score (%)
	 → first_deviation_index
	 → status: perfect/acceptable/concerning/failed
	  │
	  ▼
Django: Saves AnalysisResult to DB
	  │
	  ▼
Returns JSON → Streamlit renders:
	 - Tank cards with status badges
	 - Sensor charts (ideal vs actual + band)
	 - Alert banners for failing tanks
	 - Results table
```

Anomaly logic

```
ANOMALY DETECTION DECISION TREE

For each reading point i (i = 0 to S-1):
	  │
	  ▼
  ideal[i] = reference value
  margin  = |ideal[i]| × (tolerance% / 100)
  lower   = ideal[i] - margin
  upper   = ideal[i] + margin
	  │
	  ▼
  Is lower ≤ reading[i] ≤ upper?
	/         \
     YES          NO
      │            │
  in_band[i]=True  in_band[i]=False
		     │
		     ▼
	  First occurrence?
		/       \
	     YES        NO
	      │          │
     Record as        Add to
     first_deviation   deviation_details

After all S points:
	  │
	  ▼
  similarity_score = (sum(in_band) / S) × 100

	  │
	  ▼
  ┌──────────────────────────────────────┐
  │  Score ≥ 95%  → STATUS: PERFECT  ✅  │
  │  Score ≥ 80%  → STATUS: ACCEPTABLE 🟢│
  │  Score ≥ 60%  → STATUS: CONCERNING 🟡│
  │  Score < 60%  → STATUS: FAILED    🔴 │
  └──────────────────────────────────────┘
```

Notes
This project uses pure-Python implementations for simulation and anomaly detection to avoid binary-dependency issues on different platforms. Where possible, UI imports are done lazily so the codebase can be inspected and unit-tested without installing heavy visualization packages.

