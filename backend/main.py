import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.my_env import EmergencyEnv, Action

app = FastAPI(title="Titan Command v21", version="21.0.0")

# CORS — allows OpenEnv grader and external clients to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sim = EmergencyEnv()


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "name": "titan-command-v21"}


@app.get("/status")
def get_status():
    """Return the full current simulation state."""
    is_done = sim.steps_taken >= 100 or sim.sector_integrity <= 0
    return {
        "budget": int(sim.budget),
        "lives_saved": int(sim.lives_saved),
        "steps_taken": int(sim.steps_taken),
        "integrity": float(sim.sector_integrity),
        "incidents": [
            {
                "id": i.id, "type": i.type, "x": i.x, "y": i.y,
                "severity": i.severity, "p_score": sim.get_priority_score(i),
            }
            for i in sim.incidents
        ],
        "districts": sim.districts,
        "unit_levels": sim.unit_levels,
        "unit_xp": sim.unit_xp,
        "is_done": is_done,
        "recovery_types": sim.recovery_types,
        "history": sim.history,
        "unit_ready": sim.unit_ready,
        "cooldowns": sim.cooldowns,
        "fleet_usage": sim.fleet_usage,
    }


@app.post("/reset")
def reset():
    """Reset the environment and return the initial observation."""
    observation = sim.reset()
    return observation


@app.post("/dispatch")
def dispatch(action: Action):
    """Dispatch a unit to an incident."""
    result = sim.step(action)
    return {"ok": True, "result": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)