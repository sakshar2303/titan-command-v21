"""
OpenEnv multi-mode server entry point.
Wraps the FastAPI app from main.py and provides a callable main().
"""
import uvicorn
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # noqa: E402


def main():
    """Entry point for `openenv-server` CLI command."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
