# FermentIQ Phase Notes

## Phase 0 — Project Scaffold
Created the repository layout for the Django backend, dashboard, docs, scripts, and deployment artifacts. The scaffold was intentionally minimal so later phases could be implemented and validated in small, testable slices.

## Phase 1 — Anomaly Engine
Implemented the fermentation anomaly engine as a pure Python tolerance-band comparator. It returns a similarity score, first deviation metadata, and detailed deviations for any out-of-band readings.

## Phase 2 — Simulator
Implemented the simulator to generate realistic temperature, pH, and dissolved oxygen profiles with fault injection modes such as drift, spike, stuck, and random noise. Inline self-tests were added and verified.

## Phase 3 — Django Backend
Added Django settings, models, serializers, URL routing, and API views for simulation, analysis, results, and health. The backend persists data in SQLite and serializes all responses as JSON.

## Phase 4 — Streamlit Dashboard
Built the dashboard entrypoint and reusable components for tank cards, sensor charts, and alert banners. The dashboard uses lazy imports so it can fail gracefully if optional visualization packages are missing.

## Phase 5 — Documentation
Wrote the architecture documentation and embedded the three ASCII diagrams. The docs explain the system layout, runtime flow, API surface, and environment variables.

## Phase 6 — Deployment Prep

Added environment and runtime guidance for generic Python deployment hosts. The setup stays provider-neutral so the backend and dashboard can be deployed independently.

