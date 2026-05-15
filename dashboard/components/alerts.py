from typing import List, Dict


def render_alerts(results_list: List[Dict]) -> None:
    try:
        import streamlit as st
    except Exception:
        return

    for row in results_list:
        status = str(row.get('status', '')).lower()
        tank_id = row.get('tank_id', 'unknown')
        sensor = row.get('sensor', 'sensor')
        ts = row.get('first_deviation_timestamp') or 'unknown time'

        if status == 'concerning':
            st.warning(f"{tank_id} / {sensor} is concerning. First deviation: {ts}")
        elif status == 'failed':
            st.error(f"{tank_id} / {sensor} has failed. First deviation: {ts}")
