"""tasks/graders.py - Titan Command v21 - OpenEnv Graders

These graders are referenced by openenv.yaml and called by the evaluator.
Each grader MUST return a float strictly in (0, 1) — never 0.0 or 1.0.

Grader signatures accept (*args, **kwargs) so they work regardless of
whether the evaluator passes (env,), (env, history), or other combinations.
"""
import math


# ---------------------------------------------------------------------------
# Internal helpers — zero external dependencies
# ---------------------------------------------------------------------------

def _extract_metric(source, key, default=0.0):
    """
    Robustly extract a numeric metric from any source the evaluator might
    pass: an environment object, an observation dict, a list of steps, or None.
    """
    try:
        if source is None:
            return float(default)

        # 1. Attribute access (Environment object)
        if hasattr(source, key):
            val = getattr(source, key)
            if val is not None:
                return float(val)

        # 2. Dictionary access (Observation dict)
        if isinstance(source, dict):
            if key in source:
                return float(source[key])
            # Common aliases
            aliases = {
                "sector_integrity": "integrity",
                "integrity": "sector_integrity",
                "budget": "remaining_budget",
                "lives_saved": "saved",
            }
            alt = aliases.get(key)
            if alt and alt in source:
                return float(source[alt])

        # 3. List access (Trajectory / history)
        if isinstance(source, list) and len(source) > 0:
            last = source[-1]
            if isinstance(last, dict) and key in last:
                return float(last[key])

    except (ValueError, TypeError, KeyError, IndexError):
        pass

    return float(default)


def _safe_sigmoid(x: float) -> float:
    """Logistic sigmoid, safe against NaN / Inf / overflow."""
    try:
        if math.isnan(x) or math.isinf(x):
            return 0.5
        x = max(-500.0, min(500.0, x))
        return 1.0 / (1.0 + math.exp(-x))
    except Exception:
        return 0.5


def _clamp(score: float) -> float:
    """Force score into (0.01, 0.99) — strict open interval."""
    try:
        s = float(score)
        if math.isnan(s) or math.isinf(s):
            return 0.5
        return max(0.01, min(0.99, s))
    except Exception:
        return 0.5


# ---------------------------------------------------------------------------
# Public graders — referenced from openenv.yaml
# ---------------------------------------------------------------------------

def grade_budget(*args, **kwargs) -> float:
    """Grades performance based on remaining budget.  Range: (0, 1)"""
    env = args[0] if args else kwargs.get("env") or kwargs.get("environment")
    val = _extract_metric(env, "budget", 120000.0)
    x = (val / 120000.0) * 6.0 - 3.0
    return _clamp(_safe_sigmoid(x))


def grade_integrity(*args, **kwargs) -> float:
    """Grades performance based on sector integrity.  Range: (0, 1)"""
    env = args[0] if args else kwargs.get("env") or kwargs.get("environment")
    val = _extract_metric(env, "sector_integrity", 100.0)
    x = (val / 100.0) * 6.0 - 3.0
    return _clamp(_safe_sigmoid(x))


def grade_lives_saved(*args, **kwargs) -> float:
    """Grades performance based on total lives saved.  Range: (0, 1)"""
    env = args[0] if args else kwargs.get("env") or kwargs.get("environment")
    val = _extract_metric(env, "lives_saved", 0.0)
    x = (val / 5000.0) * 6.0 - 3.0
    return _clamp(_safe_sigmoid(x))


def grade_efficiency(*args, **kwargs) -> float:
    """Grades efficiency (lives saved per 10k budget spent).  Range: (0, 1)"""
    env = args[0] if args else kwargs.get("env") or kwargs.get("environment")
    lives = _extract_metric(env, "lives_saved", 0.0)
    budget_used = 120000.0 - _extract_metric(env, "budget", 120000.0)

    if budget_used <= 1000:
        return 0.85  # Minimal spending → high efficiency (but not 0.95 to stay safe)

    efficiency = lives / (budget_used / 10000.0)
    x = (efficiency / 5.0) * 4.0 - 2.0
    return _clamp(_safe_sigmoid(x))
