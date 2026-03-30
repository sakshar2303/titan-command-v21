#!/bin/bash

# 1. Start the TITAN BACKEND (FastAPI)
echo "🚀 Starting TITAN BACKEND..."
# We stay in /app because main.py is right here
cd /app
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 2. Give the engine 3 seconds to warm up
sleep 3

# 3. Start the TITAN HUD (Streamlit)
echo "🛰️ Starting TITAN HUD..."
# app.py is also right here in /app
streamlit run app.py --server.port 7860 --server.address 0.0.0.0