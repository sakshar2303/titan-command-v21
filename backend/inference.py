"""
Inference module for Titan Command Emergency Triage Environment.
Provides the agent logic for dispatching units to incidents.
"""

from backend.my_env import EmergencyEnv, Action


def get_best_action(env: EmergencyEnv) -> Action | None:
    """
    Greedy inference: pick the highest-priority incident
    and dispatch the best available unit.
    Returns an Action or None if no dispatch is possible.
    """
    if not env.incidents:
        return None

    # Rank incidents by priority score (highest first)
    ranked = sorted(
        env.incidents,
        key=lambda inc: env.get_priority_score(inc),
        reverse=True,
    )

    # Unit effectiveness mapping
    unit_preference = {
        "fire": "fire_truck",
        "medical": "ambulance",
        "chemical": "helicopter",
    }

    for inc in ranked:
        # Try the preferred unit first, then any available unit
        preferred = unit_preference.get(inc.type, "ambulance")
        candidates = [preferred] + [u for u in env.unit_ready if u != preferred]

        for unit in candidates:
            if env.unit_ready.get(unit) and env.budget > 2000:
                return Action(incident_id=inc.id, unit_type=unit)

    return None


def run_episode(env: EmergencyEnv | None = None, max_steps: int = 100) -> dict:
    """
    Run a full episode using the greedy inference agent.
    Returns the final status dict.
    """
    if env is None:
        env = EmergencyEnv()

    env.reset()

    for _ in range(max_steps):
        if env.steps_taken >= 100 or env.sector_integrity <= 0:
            break

        action = get_best_action(env)
        env.step(action)

    return {
        "budget": int(env.budget),
        "lives_saved": int(env.lives_saved),
        "steps_taken": int(env.steps_taken),
        "integrity": float(env.sector_integrity),
        "incidents_remaining": len(env.incidents),
    }


if __name__ == "__main__":
    result = run_episode()
    print("=== Episode Complete ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
