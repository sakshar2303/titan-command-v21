import sys
import os
import importlib
import yaml

# Add current directory to path so we can import from backend
sys.path.append(os.getcwd())

def verify():
    print("--- 🔍 TITAN COMMAND EVALUATOR INTERFACE VERIFICATION ---")
    
    # 1. Verify openenv.yaml discovery
    print("\n1. Testing openenv.yaml discovery...")
    try:
        with open("openenv.yaml", "r") as f:
            config = yaml.safe_load(f)
            tasks = config.get("tasks", [])
            print(f"✅ Found {len(tasks)} tasks in openenv.yaml")
            if len(tasks) < 3:
                print("❌ FAILED: Need at least 3 tasks.")
                return False
    except Exception as e:
        print(f"❌ FAILED: Could not read openenv.yaml: {e}")
        return False

    # 2. Verify Grader Imports & Range
    print("\n2. Testing Grader Imports & score ranges (0, 1)...")
    from backend.my_env import EmergencyEnv
    env = EmergencyEnv()
    
    # Simulate various states
    test_states = [
        {"name": "Initial State", "obs": env._get_observation()},
        {"name": "Critical State", "obs": {"budget": 500, "integrity": 5, "lives_saved": 0}},
        {"name": "Success State", "obs": {"budget": 110000, "integrity": 99, "lives_saved": 6000}},
        {"name": "Empty State", "obs": {}}
    ]

    for task in tasks:
        grader_str = task.get("grader")
        print(f"\nTask: {task['name']} -> Grader: {grader_str}")
        
        try:
            # Parse grader string: "module:function"
            module_path, function_name = grader_str.split(":")
            module = importlib.import_module(module_path)
            grader_func = getattr(module, function_name)
            
            for state in test_states:
                score = grader_func(state["obs"])
                is_valid = 0.0 < score < 1.0
                status = "✅" if is_valid else "❌"
                print(f"  [{status}] {state['name']}: {score}")
                if not is_valid:
                    print(f"    ERROR: Score {score} is not strictly within (0, 1)!")
                    return False
        except Exception as e:
            print(f"❌ FAILED to run grader {grader_str}: {e}")
            return False

    print("\n✅ ALL VERIFICATION CHECKS PASSED.")
    return True

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
