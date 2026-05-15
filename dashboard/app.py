import json
import os
from pathlib import Path

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def _safe_json(response):
    try:
        return response.json()
    except Exception:
        return {"error": f"Non-JSON response: {response.text[:200]}"}


def fetch_json(path: str):
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=30)
        return _safe_json(response)
    except Exception as exc:
        return {"error": str(exc)}


def run_simulation(n_tanks: int):
    return fetch_json(f"/api/simulate/?n_tanks={n_tanks}")


def run_analysis():
    return fetch_json("/api/analyze/")


def main():
    try:
        import streamlit as st
    except Exception:
        print("Streamlit is not installed. Install dashboard/requirements.txt first.")
        return

    from components.alerts import render_alerts
    from components.charts import plot_sensor_vs_ideal, plot_status_summary
    from components.tank_card import render_tank_card

    st.set_page_config(page_title="FermentIQ", layout="wide")
    st.title("🍺 FermentIQ — Fermentation Monitoring Dashboard")

    if "simulation_data" not in st.session_state:
        st.session_state.simulation_data = {}
    if "analysis_data" not in st.session_state:
        st.session_state.analysis_data = []

    sensor_options = {
        "Temperature": "temperature",
        "pH": "ph",
        "Dissolved Oxygen": "dissolved_oxygen",
    }

    with st.sidebar:
        st.header("Controls")
        n_tanks = st.slider("Number of tanks", 2, 10, 6)
        tolerance = st.slider("Tolerance %", 5, 20, 10)
        sensor_label = st.selectbox("Sensor selector", list(sensor_options.keys()))
        sensor_key = sensor_options[sensor_label]

        if st.button("▶ Run Simulation", use_container_width=True):
            sim_result = run_simulation(n_tanks)
            if sim_result.get("error"):
                st.error(sim_result["error"])
            else:
                st.session_state.simulation_data = sim_result
                st.success(f"Generated {sim_result.get('n_tanks', n_tanks)} tanks")

        if st.button("🔍 Analyze", use_container_width=True):
            analysis_result = run_analysis()
            if analysis_result.get("error"):
                st.error(analysis_result["error"])
            else:
                st.session_state.analysis_data = analysis_result.get("analysis", [])
                st.success("Analysis complete")

        if st.button("🔄 Refresh Results", use_container_width=True):
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()

    sim_data = st.session_state.simulation_data or {}
    analysis_rows = st.session_state.analysis_data or fetch_json("/api/results/")

    if isinstance(analysis_rows, dict) and analysis_rows.get("error"):
        st.error(analysis_rows["error"])
        analysis_rows = []

    if isinstance(sim_data, dict) and sim_data.get("error"):
        st.warning(sim_data["error"])
        sim_data = {}

    ideals = sim_data.get("ideals", {}) if isinstance(sim_data, dict) else {}
    tanks = sim_data.get("tanks", {}) if isinstance(sim_data, dict) else {}
    timestamps = sim_data.get("timestamps", []) if isinstance(sim_data, dict) else []

    tabs = st.tabs(["Live Tanks", "Sensor Charts", "Analysis Results", "System Docs"])

    with tabs[0]:
        render_alerts(analysis_rows if isinstance(analysis_rows, list) else [])
        tank_map = {}
        for row in analysis_rows if isinstance(analysis_rows, list) else []:
            tank_map.setdefault(row.get("tank_id", "unknown"), {})[row.get("sensor", "sensor")] = row

        if not tank_map and tanks:
            tank_map = {tank_id: {} for tank_id in tanks.keys()}

        if tank_map:
            rows = list(tank_map.items())
            for i in range(0, len(rows), 2):
                cols = st.columns(2)
                for col, (tank_id, sensor_rows) in zip(cols, rows[i:i + 2]):
                    with col:
                        render_tank_card(tank_id, sensor_rows)
        else:
            st.info("Run a simulation and analysis to populate tank cards.")

    with tabs[1]:
        if tanks and ideals:
            for tank_id, sensor_payload in tanks.items():
                readings = sensor_payload.get(sensor_key, []) or []
                ideal = ideals.get(sensor_key, []) or []
                if readings and ideal:
                    fig = plot_sensor_vs_ideal(tank_id, sensor_key, readings, ideal, timestamps, tolerance)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run a simulation first to view sensor charts.")

    with tabs[2]:
        import pandas as pd

        df = pd.DataFrame(analysis_rows if isinstance(analysis_rows, list) else [])
        if not df.empty:
            df = df.sort_values(by=["tank_id", "sensor"], ascending=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.plotly_chart(plot_status_summary(df.to_dict(orient="records")), use_container_width=True)
        else:
            st.info("No analysis records yet.")

    with tabs[3]:
        docs_path = Path(__file__).resolve().parent.parent / "docs" / "architecture.md"
        try:
            st.markdown(docs_path.read_text(encoding="utf-8"))
        except Exception as exc:
            st.error(f"Unable to load documentation: {exc}")


if __name__ == "__main__":
    main()
