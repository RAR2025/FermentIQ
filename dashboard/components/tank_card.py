from typing import Dict, Any


def render_tank_card(tank_id: str, results_dict: Dict[str, Dict[str, Any]]) -> None:
    """Render a tank card with status summary and a color swatch."""
    try:
        import streamlit as st
    except Exception:
        return

    sensor_rows = list(results_dict.values())
    scores = [float(row.get('similarity_score', 0) or 0) for row in sensor_rows]
    avg_score = round(sum(scores) / max(1, len(scores)), 2)

    priority = {'perfect': 0, 'acceptable': 1, 'concerning': 2, 'failed': 3}
    worst = 'perfect'
    worst_priority = -1
    for row in sensor_rows:
        status = str(row.get('status', 'perfect')).lower()
        score = priority.get(status, 0)
        if score > worst_priority:
            worst_priority = score
            worst = status

    swatch = {'perfect': '#16a34a', 'acceptable': '#2563eb', 'concerning': '#f59e0b', 'failed': '#dc2626'}.get(worst, '#6b7280')
    emoji = {'perfect': '✅', 'acceptable': '🟢', 'concerning': '🟡', 'failed': '🔴'}.get(worst, '•')

    st.markdown(
        f"""
        <div style="border:1px solid rgba(148,163,184,0.35); border-radius:16px; padding:16px; background:rgba(255,255,255,0.72); box-shadow:0 10px 30px rgba(15,23,42,0.06);">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
            <div>
              <div style="font-size:0.85rem; letter-spacing:0.08em; color:#64748b; text-transform:uppercase;">Tank</div>
              <div style="font-size:1.2rem; font-weight:700; color:#0f172a;">{tank_id}</div>
            </div>
            <div style="width:18px; height:18px; border-radius:999px; background:{swatch}; box-shadow:0 0 0 4px rgba(0,0,0,0.03);"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.metric("Average similarity", f"{avg_score}%")
    with right:
        st.markdown(f"**{emoji} {worst.capitalize()}**")
