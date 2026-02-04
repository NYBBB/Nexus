import json
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(new_data):
    current = load_config()
    current.update(new_data)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(current, f, indent=2)
    return current

def check_status():
    cfg = load_config()
    missing = []
    if not cfg.get("canvas_token"): missing.append("canvas_token")
    if not cfg.get("gmail_token"): missing.append("gmail_token") # or credentials.json path
    # Calendar usually needs an ICS url or similar
    if not cfg.get("calendar_urls"): missing.append("calendar_urls")
    
    return {
        "configured": len(missing) == 0,
        "missing": missing,
        "config_path": CONFIG_PATH
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            print(json.dumps(check_status(), indent=2))
        elif cmd == "set" and len(sys.argv) > 3:
            key = sys.argv[2]
            val = sys.argv[3]
            save_config({key: val})
            print(f"Set {key} = {val[:4]}***")
