from typing import Optional, List


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


def get_missing_fields(state) -> List[str]:
    return [f for f in REQUIRED_FIELDS if not getattr(state, f)]


def next_step(state):
    """
    Determine the next step in the flow.
    Returns (step, field)
    """

    # 1. Collect missing info
    missing = get_missing_fields(state)
    if missing:
        return "ask_question", missing[0]

    # 2. Validate address
    if not state.is_address_validated:
        return "validate_address", None

    # 3. Show appointments
    if not state.selected_provider or not state.selected_appointment_time:
        return "show_appointments", None

    # 4. Confirm
    if not getattr(state, "is_confirmed", False):
        return "confirm_appointment", None

    # 5. Finish
    return "finish", None