---
title: Titan Command v21
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# 🛰️ TITAN COMMAND v21.0
### OpenEnv Emergency Response Simulation

A high-fidelity emergency triage simulation for AI agents and human commanders to manage urban crisis response.

## 🚀 Architecture
1. **Backend** (FastAPI) runs on port `7860` — publicly exposed on HF Spaces.
2. **Frontend** (Streamlit HUD) runs on port `8000` — internal dashboard.

## 📡 API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/reset` | Reset the environment, returns initial observation |
| `GET`  | `/status` | Get current simulation state |
| `POST` | `/dispatch` | Dispatch a unit to an incident |