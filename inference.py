"""
Main entrypoint for inference, expected by the Hackathon OpenEnv evaluator.
Wrapped in try/except blocks as requested by the validation log.
"""
import sys
import traceback

def main():
    try:
        from backend.inference import run_episode
    except ImportError as e:
        print(f"Error importing backend/inference.py. Did you move the folder? Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Run inference using the backend logic
        result = run_episode()
        print("=== Episode Complete ===")
        for k, v in result.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"Inference encountered an unhandled exception: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
