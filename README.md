# FermentIQ

FermentIQ is a two-service fermentation monitoring demo built with Python. The backend generates synthetic sensor readings, stores them in SQLite, and runs anomaly detection against an ideal fermentation signature. The frontend is a Streamlit dashboard that fetches the backend data and turns it into charts, tank status cards, alerts, and analysis tables.

## What this project includes

- Synthetic fermentation data generation for temperature, pH, and dissolved oxygen
- Rule-based anomaly detection with tolerance bands
- Django REST API for simulation, analysis, results, and health checks
- Streamlit dashboard for visualization and operator-style review
- SQLite storage for generated readings and analysis output

## Tech Stack

- Python 3.14.2
- Django 4.2 + Django REST Framework
- Streamlit 1.52.2
- Plotly
- SQLite
- Requests

## How It Works

1. The backend creates ideal fermentation curves.
2. It generates synthetic tank readings by adding noise and optional fault patterns.
3. The anomaly engine compares each tank reading against the ideal curve.
4. The dashboard calls the backend API and displays the result in the browser.

## Local Run

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

By default, the dashboard expects the backend at `http://localhost:8000`. You can override this with the `BACKEND_URL` environment variable.

## Production Deployment

The backend and dashboard are split into two deployable services and can run on any host that supports Python apps.

Backend service:

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn fermentiq_backend.wsgi:application --bind 0.0.0.0:$PORT
```

Dashboard service:

```bash
cd dashboard
python -m pip install -r requirements.txt
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

Set `BACKEND_URL` on the dashboard service to the backend's public URL. For the backend, set `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` for your deployed domains.



## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health/ | Health check |
| GET | /api/simulate/ | Generate and store tank data |
| GET | /api/analyze/ | Run anomaly detection |
| GET | /api/results/ | Fetch all results |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | dev-secret-key | Django secret key |
| DEBUG | True | Debug mode |
| BACKEND_URL | http://localhost:8000 | API base URL for the dashboard |
| ALLOWED_HOSTS | localhost,127.0.0.1 | Allowed host names for Django |
| CORS_ALLOWED_ORIGINS | http://localhost:8501 | Comma-separated trusted dashboard origins |
| CSRF_TRUSTED_ORIGINS | http://localhost:8501 | Comma-separated trusted HTTPS origins |

## Notes

- The project can run locally without a virtual environment if you prefer using the system Python directly.
- The dashboard depends on the backend for simulation and analysis data.
- If you change requirements, reinstall them with `python -m pip install -r ...`.



Made with ❤️ by Ruturaj Rajwade
