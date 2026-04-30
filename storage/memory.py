import json
import os

DB_FILE = "sessions.json"

def initialize_state(existing_state=None):
    base = {
        "full_name": None,
        "date_of_birth": None,
        "payer_name": None,
        "chief_complaint": None,
        "street": None,
        "city": None,
        "state": None,
        "zip_code": None,
        "is_address_validated": False,
        "selected_provider": None,
        "selected_time": None,
        "missing_fields": [],
        "message": "",
        "data": None,
        "step": "",
        "is_complete": False,
        "user_input": "",
        "selection": None,
    }

    if existing_state:
        base.update(existing_state)

    return base

def load_sessions():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_sessions(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)


def get_session(session_id):
    sessions = load_sessions()
    return sessions.get(session_id, {})


def save_session(session_id, state):
    sessions = load_sessions()
    sessions[session_id] = state
    save_sessions(sessions)