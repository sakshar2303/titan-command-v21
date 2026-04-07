#!/bin/bash
set -e

echo "=== TITAN COMMAND v21 — Restoring Tactical HUD ==="

# 1. Start FastAPI on port 7860 (Public API port for Hackathon Space Evaluator)
echo "[1/2] Starting FastAPI backend on port 7860..."
uvicorn backend.main:app --host 0.0.0.0 --port 7860 &
FASTAPI_PID=$!

# 2. Wait until FastAPI is confirmed ready
echo "[1/2] Waiting for Neural Link (FastAPI) health check..."
for i in $(seq 1 30); do
  # Check port 7860
  if curl -sf http://localhost:7860/ > /dev/null 2>&1; then
    echo "[1/2] ✅ FastAPI is ready on public port 7860"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "[1/2] ❌ FastAPI failed to start!"
    kill $FASTAPI_PID
    exit 1
  fi
  sleep 1
done

# 3. Start Streamlit dashboard on port 8000 (Internal/Dev Port)
echo "[2/2] Starting Streamlit dashboard on internal port 8000..."
streamlit run frontend/app.py \
  --server.port 8000 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false &
STREAMLIT_PID=$!

echo "=== System Online: Commander, the fleet is ready ==="

# Keep container alive by waiting on both processes
# If either fails, the container should restart
wait -n $FASTAPI_PID $STREAMLIT_PID