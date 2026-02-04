import requests
import datetime
from datetime import timedelta, timezone
import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add Config Utils
try:
    from config_utils import load_config
except ImportError:
    # Handle running from same dir
    import config_utils
    load_config = config_utils.load_config

CANVAS_URL = "https://tlos.vt.edu/tools/canvas.html" 
CANVAS_API_URL = "https://canvas.vt.edu/api/v1"

def fetch_course_assignments(course, headers, now):
    """Fetch assignments for a single course."""
    if 'name' not in course or 'id' not in course:
        return []
    
    course_id = course['id']
    course_name = course['name']
    assignments_url = f"{CANVAS_API_URL}/courses/{course_id}/assignments?bucket=upcoming&per_page=50"
    
    found = []
    try:
        a_resp = requests.get(assignments_url, headers=headers, timeout=10)
        if a_resp.status_code == 200:
            assignments = a_resp.json()
            for asm in assignments:
                if not asm.get('due_at'):
                    continue
                
                # Canvas due_at is UTC ISO8601 (e.g., 2023-10-27T03:59:59Z)
                try:
                    due_date = datetime.datetime.fromisoformat(asm['due_at'].replace('Z', '+00:00'))
                except ValueError:
                    continue

                # Filter: Due in next 7 days
                if now < due_date < now + timedelta(days=7):
                    found.append({
                        "course": course_name,
                        "name": asm['name'],
                        "due": due_date,
                        "url": asm['html_url']
                    })
    except:
        pass # Ignore individual course errors
    return found

def get_due_assignments(token=None):
    if not token:
        cfg = load_config()
        token = cfg.get("canvas_token")
    
    if not token:
        return "Error: No Canvas Token provided or found in config."

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get Courses
    courses_url = f"{CANVAS_API_URL}/courses?enrollment_state=active"
    try:
        resp = requests.get(courses_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return f"Error connecting to Canvas: {resp.status_code} {resp.text}"
        courses = resp.json()
    except Exception as e:
        return f"Failed to connect to Canvas: {e}"

    report = []
    now = datetime.datetime.now(timezone.utc)
    
    # 2. Parallel Fetch
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_course_assignments, c, headers, now) for c in courses]
        for future in as_completed(futures):
            report.extend(future.result())

    # Sort by due date
    report.sort(key=lambda x: x['due'])
    
    if not report:
        return "No assignments due in the next 7 days."
        
    output = "## Canvas Upcoming (Next 7 Days)\n"
    
    # Use system local timezone for display
    # .astimezone(None) converts to local system time
    for item in report:
        local_due = item['due'].astimezone(None)
        # Format: MM-DD HH:MM (Timezone Name)
        due_str = local_due.strftime("%m-%d %H:%M")
        output += f"*   **{item['course']}**: [{item['name']}]({item['url']}) (Due: {due_str})\n"
        
    return output

if __name__ == "__main__":
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1]
    
    # If no token passed, function will try config
    print(get_due_assignments(token))
