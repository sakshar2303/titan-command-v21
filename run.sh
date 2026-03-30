#!/bin/bash
echo "🚀 Starting TITAN BACKEND on Primary Port (7860)..."
# We move the API to 7860 so the Scaler bot hits it directly
uvicorn main:app --host 0.0.0.0 --port 7860 &

sleep 5

echo "🛰️ Starting TITAN HUD on Secondary Port (8000)..."
# Streamlit moves to 8000
streamlit run app.py --server.port 8000 --server.address 0.0.0.0