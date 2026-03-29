import requests
import time

API_URL = "http://127.0.0.1:8000"

def run_baseline_inference():
    print("🛰️ INITIALIZING BASELINE AGENT...")
    requests.post(f"{API_URL}/reset")
    
    total_reward = 0
    steps = 0
    
    while steps < 100:
        # 1. GET STATE
        resp = requests.get(f"{API_URL}/status").json()
        if resp.get("is_done"): break
        
        # 2. SIMPLE HEURISTIC AGENT (The "Greedy" Logic)
        incidents = resp.get("incidents", [])
        action = {"incident_id": 0, "unit_type": "none"}
        
        if incidents:
            # Target the highest priority threat
            target = sorted(incidents, key=lambda x: x['severity'], reverse=True)[0]
            # Check if any unit is ready
            ready_units = [u for u, r in resp['unit_ready'].items() if r]
            if ready_units:
                action = {"incident_id": target['id'], "unit_type": ready_units[0]}
        
        # 3. STEP
        requests.post(f"{API_URL}/dispatch", json=action)
        steps += 1
        
    # 4. FINAL GRADING (0.0 - 1.0)
    final = requests.get(f"{API_URL}/status").json()
    score = min(1.0, (final['lives_saved'] / 5000) * (final['integrity'] / 100))
    
    print(f"--- MISSION COMPLETE ---")
    print(f"Final Survivors: {final['lives_saved']}")
    print(f"Final Integrity: {final['integrity']:.1f}%")
    print(f"🚀 AGER GRADER SCORE: {score:.2f}")

if __name__ == "__main__":
    run_baseline_inference()