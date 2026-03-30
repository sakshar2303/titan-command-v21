#!/bin/bash

# 1. Start the TITAN BACKEND (FastAPI) in the background
echo "🚀 Starting TITAN BACKEND..."
# Use absolute path to ensure it finds the main file
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 2. Wait a moment for the backend to initialize
sleep 3

# 3. Start the TITAN HUD (Streamlit)
echo "🛰️ Starting TITAN HUD..."
# Move to the frontend directory
cd /app/frontend
# Streamlit MUST run on port 7860 for Hugging Face to show it
streamlit run app.py --server.port 7860 --server.address 0.0.0.0