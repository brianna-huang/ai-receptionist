REQUIRED_FIELDS = [
    "full_name",
    "date_of_birth",
    "payer_name",
    "chief_complaint",
    "street",
    "city",
    "state",
    "zip_code",
]

def route_missing(state):
    missing = [f for f in REQUIRED_FIELDS if not state.get(f)]
    state["missing_fields"] = missing

    if missing:
        return "ask_fields"

    return "validate_address"


def route_after_validation(state):
    if not state.get("is_address_validated"):
        return "validate_address"

    # if user already selected → skip UI
    if state.get("selected_provider") and state.get("selected_time"):
        return "confirm"

    return "show_appointments"


def route_after_selection(state):
    # If user has not selected anything yet → stay in appointment UI
    if not state.get("selected_provider") or not state.get("selected_time"):
        return "show_appointments"

    # Once both are selected → move forward
    return "confirm"


def route_after_confirm(state):
    if state.get("is_confirmed"):
        return "finish"

    # if user said no → go back to scheduling
    if not state.get("selected_provider") or not state.get("selected_time"):
        return "show_appointments"

    return "confirm"