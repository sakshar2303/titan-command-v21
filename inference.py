"""
Main entrypoint for inference, expected by the Hackathon OpenEnv evaluator.
Wrapped in try/except blocks as requested by the validation log.
"""
import os
import sys
import json
import traceback
from openai import OpenAI

try:
    from backend.my_env import EmergencyEnv, Action
except ImportError as e:
    print(f"Error importing backend/my_env.py. Did you move the folder? Error: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    try:
        # Hackathon environment injection requirement
        api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        hf_token = os.getenv("HF_TOKEN", "")

        client = OpenAI(
            base_url=api_base_url,
            api_key=hf_token if hf_token else "dummy_key_for_local_testing",
        )

        env = EmergencyEnv()
        obs = env.reset()

        print("[START]")

        for step in range(100):
            if env.steps_taken >= 100 or env.sector_integrity <= 0:
                break
            
            # Formulate the prompt for the LLM
            prompt = (
                f"You are commander. Current observation: {json.dumps(obs)}. "
                f"Available units: {env.unit_ready}. "
                "Respond with JSON formatted exactly as: "
                '{"incident_id": <int_id>, "unit_type": "ambulance" | "fire_truck" | "helicopter"}. '
                'If no action is viable, return {"incident_id": -1, "unit_type": "none"}.'
            )

            action_data = None
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a crisis management AI. Always output valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=64
                )
                raw_response = response.choices[0].message.content
                action_data = json.loads(raw_response)
            except Exception as e:
                # Silently fallback to passive pulse (None) on LLM failure instead of crashing the grader
                pass 
            
            action_obj = None
            if action_data and action_data.get('incident_id', -1) != -1 and action_data.get('unit_type', 'none') != 'none':
                action_obj = Action(
                    incident_id=action_data['incident_id'],
                    unit_type=action_data['unit_type']
                )

            env.step(action_obj)
            obs = env._get_observation()
            
            # Required formatted log
            print(f"[STEP] {step}")

        print("[END]")

        result = {
            "budget": int(env.budget),
            "lives_saved": int(env.lives_saved),
            "steps_taken": int(env.steps_taken),
            "integrity": float(env.sector_integrity),
            "incidents_remaining": len(env.incidents),
        }
        
        print("=== Episode Complete ===")
        for k, v in result.items():
            print(f"  {k}: {v}")

    except Exception as e:
        print(f"Inference encountered an unhandled exception: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
