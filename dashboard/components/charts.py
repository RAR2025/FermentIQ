from typing import List, Dict, Any


def plot_sensor_vs_ideal(tank_id: str, sensor: str, readings: List[float], ideal: List[float], timestamps: List[str], tolerance_pct: float = 10) -> Any:
    """Return a Plotly figure comparing readings to ideal with a tolerance band."""
    import plotly.graph_objects as go

    if not ideal:
        return go.Figure()

    S = min(len(ideal), len(timestamps) or len(ideal), len(readings) or len(ideal))
    ideal = ideal[:S]
    readings = readings[:S]
    timestamps = timestamps[:S] if timestamps else list(range(S))

    margin = [max(abs(ideal[i]) * (tolerance_pct / 100.0), 0.01) for i in range(S)]
    lower = [ideal[i] - margin[i] for i in range(S)]
    upper = [ideal[i] + margin[i] for i in range(S)]

    first_dev = None
    for i in range(min(S, len(readings))):
        if not (lower[i] <= readings[i] <= upper[i]):
            first_dev = i
            break

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=upper, mode='lines', line=dict(color='rgba(100,100,100,0.15)'), name='Upper', showlegend=False))
    fig.add_trace(go.Scatter(x=timestamps, y=lower, mode='lines', line=dict(color='rgba(100,100,100,0.15)'), fill='tonexty', fillcolor='rgba(160,160,160,0.18)', name='Tolerance Band', showlegend=True))
    fig.add_trace(go.Scatter(x=timestamps, y=ideal, mode='lines', name='Ideal', line=dict(color='#111827', dash='dash', width=2)))
    fig.add_trace(go.Scatter(x=timestamps, y=readings, mode='lines+markers', name='Actual', line=dict(color='#2563eb', width=2), marker=dict(size=5)))

    if first_dev is not None and first_dev < len(timestamps):
        fig.add_vline(x=timestamps[first_dev], line=dict(color='#dc2626', dash='dot', width=2))

    fig.update_layout(
        title=f"{tank_id} — {sensor}",
        xaxis_title='Time',
        yaxis_title=sensor.replace('_', ' ').title(),
        height=360,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation='h')
    )
    return fig


def plot_status_summary(results_list: List[Dict[str, Any]]) -> Any:
    """Return a horizontal bar chart of tanks colored by status."""
    import plotly.graph_objects as go

    grouped: Dict[str, Dict[str, Any]] = {}
    priority = {'perfect': 0, 'acceptable': 1, 'concerning': 2, 'failed': 3}
    palette = {'perfect': '#16a34a', 'acceptable': '#2563eb', 'concerning': '#f59e0b', 'failed': '#dc2626'}

    for row in results_list:
        tank_id = row.get('tank_id', 'unknown')
        bucket = grouped.setdefault(tank_id, {'scores': [], 'worst': 'perfect'})
        bucket['scores'].append(float(row.get('similarity_score', 0) or 0))
        status = str(row.get('status', 'perfect')).lower()
        if priority.get(status, 0) > priority.get(bucket['worst'], 0):
            bucket['worst'] = status

    tank_ids = list(grouped.keys())
    scores = [round(sum(grouped[t]['scores']) / max(1, len(grouped[t]['scores'])), 2) for t in tank_ids]
    colors = [palette.get(grouped[t]['worst'], '#6b7280') for t in tank_ids]

    fig = go.Figure(go.Bar(x=scores, y=tank_ids, orientation='h', marker_color=colors))
    fig.update_layout(
        title='Tank Similarity Summary',
        xaxis_title='Average Similarity %',
        yaxis_title='Tank',
        height=max(320, 60 * len(tank_ids) + 80),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig
