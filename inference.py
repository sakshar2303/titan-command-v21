"""
inference.py - Titan Command v21
Root-level inference script for OpenEnv hackathon evaluator.
Output format strictly follows the required specification.
"""
import os
import sys
import json
import traceback

from openai import OpenAI

# --- Required environment variables ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

try:
    from backend.my_env import (
        EmergencyEnv, Action,
        grade_budget, grade_integrity, grade_lives_saved, grade_efficiency
    )
except ImportError as e:
    print(f"[END] success=false steps=0 rewards=0.00", flush=True)
    sys.exit(1)


def main():
    task_name = "emergency-triage"
    env_name  = "titan-command-v21"

    env = EmergencyEnv()
    env.reset()

    # [START] line — required exactly once
    print(f"[START] task={task_name} env={env_name} model={MODEL_NAME}", flush=True)

    rewards = []
    success = False

    try:
        for step in range(1, 101):
            if env.steps_taken >= 100 or env.sector_integrity <= 0:
                break

            obs = env._get_observation()
            action_str = "none"
            error_str  = "null"
            action_obj = None

            # LLM action
            try:
                prompt = (
                    f"You are commander. Observation: {json.dumps(obs)}. "
                    f"Available units: {env.unit_ready}. "
                    "Respond with JSON: "
                    '{\"incident_id\": <int>, \"unit_type\": \"ambulance\"|\"fire_truck\"|\"helicopter\"}. '
                    'If no action: {\"incident_id\": -1, \"unit_type\": \"none\"}.'
                )
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a crisis management AI. Always output valid JSON."},
                        {"role": "user",   "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=64
                )
                action_data = json.loads(response.choices[0].message.content)
                inc_id   = action_data.get("incident_id", -1)
                unit     = action_data.get("unit_type", "none")

                if inc_id != -1 and unit != "none":
                    action_obj = Action(incident_id=inc_id, unit_type=unit)
                    action_str = f"dispatch(incident={inc_id},unit={unit})"
                else:
                    action_str = "passive_pulse"

            except Exception as ex:
                error_str  = str(ex).replace("\n", " ")[:80]
                action_str = "passive_pulse"

            env.step(action_obj)

            reward = 0.00
            done   = (env.steps_taken >= 100 or env.sector_integrity <= 0)
            rewards.append(reward)

            # [STEP] line — required once per step
            print(
                f"[STEP] step={step} action={action_str} "
                f"reward={reward:.2f} done={'true' if done else 'false'} "
                f"error={error_str}",
                flush=True
            )

            if done:
                break

        success = env.sector_integrity > 0

    except Exception as e:
        success = False
        traceback.print_exc(file=sys.stderr)

    # [END] line — always emitted
    rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
    print(
        f"[END] success={'true' if success else 'false'} "
        f"steps={len(rewards)} rewards={rewards_str}",
        flush=True
    )

    # --- Task scores for evaluator ---
    task_scores = {
        "task_1": grade_budget(env),
        "task_2": grade_integrity(env),
        "task_3": grade_lives_saved(env),
        "task_4": grade_efficiency(env),
    }
    print("TASK_SCORES:", json.dumps(task_scores), flush=True)
    print(json.dumps({"task_scores": task_scores}), flush=True)


if __name__ == "__main__":
    main()