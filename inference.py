"""
Main entrypoint for inference, expected by the Hackathon OpenEnv evaluator.
CRITICAL: Must print task scores as JSON so the evaluator can parse them.
"""
import os
import sys
import json
import traceback

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from backend.my_env import (
        EmergencyEnv, Action,
        grade_budget, grade_integrity, grade_lives_saved, grade_efficiency
    )
except ImportError as e:
    print(f"Error importing backend/my_env.py: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    try:
        # Hackathon environment injection
        api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        model_name   = os.getenv("MODEL_NAME", "gpt-4o-mini")
        hf_token     = os.getenv("HF_TOKEN")

        client = None
        if OpenAI is not None:
            client = OpenAI(
                base_url=api_base_url,
                api_key=hf_token or "dummy_token_to_prevent_crash",
            )

        env = EmergencyEnv()
        obs = env.reset()

        print("[START]")

        for step in range(100):
            if env.steps_taken >= 100 or env.sector_integrity <= 0:
                break

            action_data = None

            # Try LLM action; silently fall back to passive pulse on any failure
            if client is not None:
                try:
                    prompt = (
                        f"You are commander. Current observation: {json.dumps(obs)}. "
                        f"Available units: {env.unit_ready}. "
                        "Respond with JSON formatted exactly as: "
                        '{"incident_id": <int_id>, "unit_type": "ambulance" | "fire_truck" | "helicopter"}. '
                        'If no action is viable, return {"incident_id": -1, "unit_type": "none"}.'
                    )
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "You are a crisis management AI. Always output valid JSON."},
                            {"role": "user",   "content": prompt}
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=64
                    )
                    action_data = json.loads(response.choices[0].message.content)
                except Exception:
                    pass

            action_obj = None
            if (action_data
                    and action_data.get("incident_id", -1) != -1
                    and action_data.get("unit_type", "none") != "none"):
                action_obj = Action(
                    incident_id=action_data["incident_id"],
                    unit_type=action_data["unit_type"]
                )

            env.step(action_obj)
            obs = env._get_observation()
            print(f"[STEP] {step}")

        print("[END]")

        # ------------------------------------------------------------------
        # CRITICAL: Call graders and output scores as JSON.
        # The evaluator reads this to validate task scores.
        # ------------------------------------------------------------------
        task_scores = {
            "task_1": grade_budget(env),
            "task_2": grade_integrity(env),
            "task_3": grade_lives_saved(env),
            "task_4": grade_efficiency(env),
        }

        # Print the episode summary (human-readable)
        print("=== Episode Complete ===")
        print(f"  budget:    {env.budget}")
        print(f"  integrity: {env.sector_integrity:.2f}")
        print(f"  lives_saved: {env.lives_saved}")
        print(f"  steps_taken: {env.steps_taken}")

        # REQUIRED: Print scores as JSON on its own line so the evaluator finds it
        print("TASK_SCORES:", json.dumps(task_scores))

        # Also dump full result JSON (belt-and-suspenders)
        result = {
            "task_scores": task_scores,
            "budget": int(env.budget),
            "lives_saved": int(env.lives_saved),
            "steps_taken": int(env.steps_taken),
            "integrity": float(env.sector_integrity),
            "incidents_remaining": len(env.incidents),
        }
        print(json.dumps(result))

    except Exception as e:
        print(f"Inference encountered an unhandled exception: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
