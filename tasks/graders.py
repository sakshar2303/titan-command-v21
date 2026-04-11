"""tasks/graders.py - Titan Command v21"""
import math

def _clamp(v):
    return max(0.01, min(0.99, float(v)))

def _get(env, key, default=0.0):
    try:
        if hasattr(env, key):
            val = getattr(env, key)
            if val is not None:
                return float(val)
        if isinstance(env, dict):
            return float(env.get(key, default))
    except Exception:
        pass
    return float(default)

def grade_budget(env) -> float:
    val = _get(env, "budget", 60000.0)
    return _clamp(val / 120000.0 * 0.88 + 0.05)

def grade_integrity(env) -> float:
    val = _get(env, "sector_integrity", 50.0)
    if val == 0.0:
        val = _get(env, "integrity", 50.0)
    return _clamp(val / 100.0 * 0.88 + 0.05)

def grade_lives_saved(env) -> float:
    val = _get(env, "lives_saved", 0.0)
    return _clamp(val / 5000.0 * 0.88 + 0.05)

def grade_efficiency(env) -> float:
    return 0.5
