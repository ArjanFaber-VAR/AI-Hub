import os
import json
import subprocess
import glob

# --- Configuration ---
WATCH_FOLDER = r"C:\Users\ArjanFaberVAR\OneDrive - Van Amersfoort Racing B.V\Regulations-VAR - Documenten"
SCRIPT_TO_RUN = r"C:\Users\ArjanFaberVAR\OneDrive - Van Amersfoort Racing B.V\Regulations-VAR - Documenten\regulations_f3.py"
STATE_FILE = os.path.join(WATCH_FOLDER, "state.json")

# --- Helper functions ---
def get_latest_html():
    files = [f for f in os.listdir(WATCH_FOLDER) if f.endswith(".html")]
    if not files:
        return None
    full_paths = [os.path.join(WATCH_FOLDER, f) for f in files]
    return max(full_paths, key=os.path.getmtime)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

# --- Main logic ---
state = load_state()
latest_file = get_latest_html()

if latest_file:
    last_modified = os.path.getmtime(latest_file)
    
    if state.get("last_run") != last_modified:
        print(f"New or updated html detected: {os.path.basename(latest_file)}")
        
        # Run your Python script (or replace with notebook execution if needed)
        subprocess.run(["python", SCRIPT_TO_RUN], check=True)

        # Update state
        state["last_run"] = last_modified
        save_state(state)
    else:
        print("No new html files detected.")
else:
    print("No html files found in folder.")


folder_path = r"C:\Users\ArjanFaberVAR\OneDrive - Van Amersfoort Racing B.V\Regulations-VAR - Documenten"

# List of patterns to delete
patterns = ["*.html"]

for pattern in patterns:
    files_to_delete = glob.glob(os.path.join(folder_path, pattern))
    if files_to_delete:
        for file_path in files_to_delete:
            os.remove(file_path)
            print(f"Deleted {os.path.basename(file_path)}")
    else:
        print(f"No files found for pattern: {pattern}")