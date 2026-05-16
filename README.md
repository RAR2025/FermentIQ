<div align="center">

# 🧪 FermentIQ

**Intelligent fermentation monitoring — synthetic data, real insights.**

[![Python](https://img.shields.io/badge/Python-3.14.2-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52.2-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-embedded-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#)

[**Live Dashboard →**](https://rar-fermentiq.streamlit.app/) &nbsp;|&nbsp; [**Backend API →**](https://fermentiq.onrender.com)

</div>

---

## What is FermentIQ?

FermentIQ is a two-service fermentation monitoring demo. The **backend** generates synthetic sensor readings, stores them in SQLite, and runs anomaly detection against an ideal fermentation signature. The **frontend** is a Streamlit dashboard that fetches the backend data and renders it as charts, tank status cards, alerts, and analysis tables.

---

## ✨ Features

- 📈 **Synthetic data generation** — realistic temperature, pH, and dissolved oxygen curves with configurable noise and fault patterns
- 🔍 **Anomaly detection** — rule-based engine with tolerance bands compared against ideal fermentation signatures
- 🌐 **REST API** — Django REST Framework endpoints for simulation, analysis, and results
- 📊 **Live dashboard** — Streamlit + Plotly for operator-style visualization and review
- 🗄️ **Persistent storage** — SQLite for generated readings and analysis output

---

## 🏗️ Architecture

```
┌──────────────────────────────┐        ┌──────────────────────────────┐
│       Streamlit Dashboard    │        │        Django Backend        │
│                              │        │                              │
│  • Tank status cards         │◄──────►│  • Ideal curve generation    │
│  • Plotly charts             │  HTTP  │  • Synthetic data injection  │
│  • Alert feed                │        │  • Anomaly detection engine  │
│  • Analysis tables           │        │  • SQLite persistence        │
└──────────────────────────────┘        └──────────────────────────────┘
        https://rar-fermentiq.streamlit.app      https://fermentiq.onrender.com
```

---

## ⚙️ How It Works

1. **Generate ideal curves** — the backend constructs the expected fermentation profile for temperature, pH, and DO.
2. **Inject synthetic readings** — noise and optional fault patterns are layered onto the ideal curve to simulate real tank behavior.
3. **Run anomaly detection** — each reading is compared against the ideal curve; deviations outside tolerance bands are flagged.
4. **Visualize on the dashboard** — the Streamlit app calls the API and renders tank status, trends, and alerts in the browser.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- No virtual environment required (system Python works fine)

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Dashboard

```bash
cd dashboard
python -m pip install -r requirements.txt
streamlit run app.py
```

> By default, the dashboard connects to `http://localhost:8000`. Override with the `BACKEND_URL` environment variable.

---

## 🌍 Production Deployment

FermentIQ runs as two independent services.

### Backend (Render)

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn fermentiq_backend.wsgi:application --bind 0.0.0.0:$PORT
```

### Dashboard (Streamlit Cloud)

```bash
cd dashboard
python -m pip install -r requirements.txt
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

### Recommended Environment Variables

| Variable | Recommended Value | Description |
|---|---|---|
| `BACKEND_URL` | `https://fermentiq.onrender.com` | API base URL for the dashboard |
| `ALLOWED_HOSTS` | `fermentiq.onrender.com,localhost,127.0.0.1` | Django allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `https://rar-fermentiq.streamlit.app` | Trusted dashboard origin |
| `CSRF_TRUSTED_ORIGINS` | `https://rar-fermentiq.streamlit.app` | Trusted HTTPS origin |
| `SECRET_KEY` | *(your secret)* | Django secret key |
| `DEBUG` | `False` | Disable in production |

---

## 📡 API Reference

Base URL: `https://fermentiq.onrender.com`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health/` | Health check |
| `GET` | `/api/simulate/` | Generate and store synthetic tank data |
| `GET` | `/api/analyze/` | Run anomaly detection |
| `GET` | `/api/results/` | Fetch all stored results |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14.2 |
| Backend framework | Django 4.2 + Django REST Framework |
| Frontend | Streamlit 1.52.2 |
| Charting | Plotly |
| Database | SQLite |
| HTTP client | Requests |

---

## 📁 Project Structure

```
FermentIQ/
├── backend/
│   ├── fermentiq_backend/   # Django project settings and WSGI config
│   ├── monitor/             # Models, API views, serializers, anomaly engine
│   ├── db.sqlite3
│   ├── manage.py
│   └── requirements.txt
├── dashboard/
│   ├── app.py               # Streamlit entrypoint
│   ├── components/          # Charts, alerts, and tank cards
│   └── requirements.txt
├── docs/                    # Architecture notes and diagrams
└── scripts/                 # Utility scripts such as data seeding
```

---

## 🔧 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key` | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `BACKEND_URL` | `http://localhost:8000` | API base URL for the dashboard |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed host names for Django |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:8501` | Comma-separated trusted dashboard origins |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8501` | Comma-separated trusted HTTPS origins |

---

<div align="center">

Made with ❤️ by [Ruturaj Rajwade](https://github.com/ruturajrajwade)

</div>
