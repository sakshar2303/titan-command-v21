"""
tasks/graders.py — Titan Command v21
Grader functions for OpenEnv Phase 2 evaluation.

CRITICAL RULE: All scores must be STRICTLY between 0 and 1.
               Never return exactly 0.0 or exactly 1.0.
               We use max(0.01, min(0.99, raw_score)) to enforce this.
"""


def _clamp(value: float) -> float:
    """Clamp a score to strictly (0, 1) — never 0.0, never 1.0."""
    return max(0.01, min(0.99, float(value)))


def grade_budget(env_state: dict) -> float:
    """
    Task 1 — Budget Preservation
    Score how well the agent preserved the budget.
    env_state must contain 'budget' (current) and optionally 'initial_budget'.
    Score = current_budget / initial_budget, clamped to (0.01, 0.99).
    """
    budget = env_state.get("budget", 0)
    initial_budget = env_state.get("initial_budget", 200_000)

    if initial_budget <= 0:
        return 0.5  # fallback — safely in range

    raw = budget / initial_budget
    return _clamp(raw)


def grade_integrity(env_state: dict) -> float:
    """
    Task 2 — Sector Integrity
    Score how well the agent maintained sector integrity (0–100).
    Score = integrity / 100, clamped to (0.01, 0.99).
    """
    integrity = env_state.get("integrity", 50)

    raw = integrity / 100.0
    return _clamp(raw)


def grade_lives_saved(env_state: dict) -> float:
    """
    Task 3 — Lives Saved
    Score the fraction of lives saved out of total lives at risk.
    env_state must contain 'lives_saved' and 'total_lives'.
    Score = lives_saved / total_lives, clamped to (0.01, 0.99).
    """
    lives_saved = env_state.get("lives_saved", 0)
    total_lives = env_state.get("total_lives", 1)

    if total_lives <= 0:
        return 0.5  # fallback — safely in range

    raw = lives_saved / total_lives
    return _clamp(raw)
