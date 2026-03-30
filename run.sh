#!/bin/bash
# Move FastAPI to the public port (7860) so the bot finds /reset instantly
uvicorn main:app --host 0.0.0.0 --port 7860 &

sleep 5

# Move Streamlit to the background port
streamlit run app.py --server.port 8000 --server.address 0.0.0.0