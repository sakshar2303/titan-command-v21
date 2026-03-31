import random
import json
import os
from pydantic import BaseModel
from typing import List, Optional

# --- DATA MODELS ---
class Action(BaseModel):
    incident_id: int
    unit_type: str 

class Incident(BaseModel):
    id: int
    type: str
    location: str
    x: float
    y: float
    z: float 
    severity: float
    population: int

# --- MAIN ENVIRONMENT ---
class EmergencyEnv:
    def __init__(self):
        self.reset()

    def reset(self, p_levels=None, p_xp=None):
        """Initializes or Restarts the Simulation State"""
        # Core Metrics
        self.budget = 120000 
        self.steps_taken = 0
        self.lives_saved = 0
        self.sector_integrity = 100.0
        
        # Unit Management
        self.unit_ready = {"helicopter": True, "fire_truck": True, "ambulance": True}
        self.cooldowns = {"helicopter": 0, "fire_truck": 0, "ambulance": 0}
        
        # Analytics Tracking
        self.history = {
            "steps": [0], "budget": [120000], "saved": [0], 
            "integrity": [100.0], "drain": [150]
        }
        
        # Geospatial Infrastructure
        self.districts = {
            "Medical": {"x": 2, "y": 2, "status": "NOMINAL", "fortified": False},
            "Financial": {"x": 8, "y": 8, "status": "NOMINAL", "fortified": False},
            "Power": {"x": 5, "y": 5, "status": "NOMINAL", "fortified": False}
        }
        
        # Threat Engine
        self.predictions = []
        self.global_event = "NONE"
        self.last_drain = 150
        
        # Veteran Persistence (Levels & XP)
        self.unit_levels = p_levels if p_levels else {"helicopter": 1, "fire_truck": 1, "ambulance": 1}
        self.unit_xp = p_xp if p_xp else {"helicopter": 0, "fire_truck": 0, "ambulance": 0}
        self.fleet_usage = {"helicopter": 0, "fire_truck": 0, "ambulance": 0}
        self.recovery_types = {"fire": 0, "medical": 0, "chemical": 0}
        
        # Initial Incidents
        self.incidents = []
        for _ in range(3):
            self._spawn_incident()

        # Return the initial observation (required by OpenEnv grader)
        return self._get_observation()

    def _get_observation(self) -> dict:
        """Build and return the current observation dictionary."""
        return {
            "budget": int(self.budget),
            "lives_saved": int(self.lives_saved),
            "steps_taken": int(self.steps_taken),
            "integrity": float(self.sector_integrity),
            "incidents": [
                {
                    "id": i.id, "type": i.type, "x": i.x, "y": i.y,
                    "severity": i.severity,
                }
                for i in self.incidents
            ],
            "districts": self.districts,
            "unit_levels": self.unit_levels,
            "unit_xp": self.unit_xp,
            "is_done": False,
            "unit_ready": self.unit_ready,
            "cooldowns": self.cooldowns,
        }

    def _spawn_incident(self, x=None, y=None, sev=None):
        """Generates a new threat on the 3D grid"""
        types = ["fire", "medical", "chemical"]
        new_id = random.randint(1000, 9999)
        self.incidents.append(Incident(
            id=new_id,
            type=random.choice(types),
            location=f"ZONE_{new_id}",
            x=x if x is not None else random.uniform(1, 9), 
            y=y if y is not None else random.uniform(1, 9), 
            z=random.uniform(1, 8),
            severity=sev if sev is not None else random.uniform(5.0, 10.0), 
            population=random.randint(500, 4000)
        ))

    def step(self, action: Optional[Action] = None):
        """Advances the simulation by one clock cycle"""
        if self.steps_taken >= 100 or self.sector_integrity <= 0:
            return
            
        self.steps_taken += 1

        # 1. Logic: Update Cooldowns
        for unit in self.cooldowns:
            if self.cooldowns[unit] > 0:
                self.cooldowns[unit] -= 1
            self.unit_ready[unit] = (self.cooldowns[unit] == 0)

        # 2. Logic: The Financial Death Spiral
        # Penalty increases as integrity drops
        integrity_penalty = (100.0 - self.sector_integrity) * 20 
        self.last_drain = 150 + int(integrity_penalty)
        self.budget -= self.last_drain

        # 3. Logic: Satellite Predictions
        if random.random() < 0.15:
            self.predictions.append({"x": random.uniform(1, 9), "y": random.uniform(1, 9), "steps": 5})
        
        for p in self.predictions[:]:
            p["steps"] -= 1
            if p["steps"] <= 0:
                self._spawn_incident(x=p["x"], y=p["y"], sev=5.0)
                self.predictions.remove(p)

        # 4. Logic: Incident Growth & Integrity Decay
        for inc in self.incidents:
            inc.severity += 0.9  # Passive growth
            # Integrity loss is proportional to total city severity
            self.sector_integrity = max(0, self.sector_integrity - (inc.severity / 45.0))

        # 5. Logic: Process Dispatch Action
        if action and action.unit_type != "none":
            target = next((i for i in self.incidents if i.id == action.incident_id), None)
            if target and self.unit_ready.get(action.unit_type):
                u = action.unit_type
                lvl = self.unit_levels[u]
                
                # Suppression Power Calculation
                power = 8.0 + (lvl * 0.5)
                target.severity -= power
                
                # Check for Incident Resolution
                if target.severity <= 0:
                    bonus = int(target.population * 0.20)
                    self.lives_saved += bonus
                    self.recovery_types[target.type] += bonus
                    self.incidents = [i for i in self.incidents if i.id != action.incident_id]
                
                # Leveling Logic
                self.unit_xp[u] += 10
                if self.unit_xp[u] >= (lvl * 30):
                    self.unit_levels[u] += 1
                    self.unit_xp[u] = 0
                
                # Cost & Cooldown Application
                self.budget -= int(2000 * (1 - (lvl - 1) * 0.05))
                self.cooldowns[u] = (5 if u == "helicopter" else 2) - (lvl // 3)
                self.fleet_usage[u] += 1

        # 6. Logic: Record History for Graphs
        self.history["steps"].append(self.steps_taken)
        self.history["budget"].append(self.budget)
        self.history["integrity"].append(self.sector_integrity)
        self.history["drain"].append(self.last_drain)

    def get_priority_score(self, inc: Incident):
        """Neural Priority Score used by Auto-Pilot"""
        return round((inc.severity * 2.5) + (inc.population / 400.0), 2)