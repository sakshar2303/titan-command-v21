from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# --- 1. ADD CORS MIDDLEWARE (CRITICAL FOR SCALER CHECKS) ---
# This allows the Scaler automated grader to talk to your API safely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sim = EmergencyEnv()

@app.get("/status")
def get_status():
    is_done = sim.steps_taken >= 100 or sim.sector_integrity <= 0
    return {
        "budget": int(sim.budget), 
        "lives_saved": int(sim.lives_saved),
        "steps_taken": int(sim.steps_taken), 
        "integrity": float(sim.sector_integrity),
        "incidents": [{"id": i.id, "type": i.type, "x": i.x, "y": i.y, "severity": i.severity, "p_score": sim.get_priority_score(i)} for i in sim.incidents],
        "districts": sim.districts, 
        "unit_levels": sim.unit_levels, 
        "unit_xp": sim.unit_xp,
        "is_done": is_done, 
        "recovery_types": sim.recovery_types, 
        "history": sim.history, 
        "unit_ready": sim.unit_ready, 
        "cooldowns": sim.cooldowns, 
        "fleet_usage": sim.fleet_usage
    }

# --- 2. ENSURE RESET RETURNS THE OBSERVATION ---
# The OpenEnv grader pings this to see if the environment is ready.
@app.post("/reset")
def reset():
    observation = sim.reset()
    return observation  # MUST return the initial state/observation dictionary

@app.post("/dispatch")
def dispatch(action: Action):
    # step() returns (observation, reward, done, info)
    result = sim.step(action)
    return {"ok": True, "result": result}

# --- 3. FIX HOST FOR DOCKER COMPATIBILITY ---
if __name__ == "__main__":
    # 0.0.0.0 allows the app to be reachable from outside the container.
    uvicorn.run(app, host="0.0.0.0", port=8000)