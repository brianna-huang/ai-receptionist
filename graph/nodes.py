from services.extractor import extract_info
from services.llm import generate_message
from services.google_maps import validate_address
from services.providers import get_mock_providers
from services.validators import validate_field
from config import OPENAI_API_KEY
from graph.routers import REQUIRED_FIELDS


def extract_node(state):
    user_input = state.get("user_input", "")

    # handle confirmation
    if state.get("step") == "confirm":
        if any(word in user_input for word in ["yes", "y", "yeah", "yep", "confirm", "correct", "good"]):
            state["is_confirmed"] = True
            return state

        if any(word in user_input for word in ["no", "nope", "change", "back", "wrong"]):
            state["selected_provider"] = None
            state["selected_time"] = None
            state["is_confirmed"] = False
            return state

    extracted = extract_info(user_input, state)

    for field, value in extracted.items():
        # skip if already filled
        if state.get(field):
            continue

        # validate
        if validate_field(field, value):
            state[field] = value
        else:
            state["message"] = get_retry_message(field)
            state["step"] = "ask_question"

            # ONLY reject this field, not entire node
            return state
        
    state["missing_fields"] = [f for f in REQUIRED_FIELDS if not state.get(f)]

    return state

def get_retry_message(field: str) -> str:
    messages = {
        "full_name": "Hmm, could you share your full name (first and last)?",
        "date_of_birth": "Sorry, I couldn't recognize that date. Could you enter your date of birth as MM/DD/YYYY?",
        "zip_code": "Sorry, I couldn’t recognize that ZIP code — could you try again?",
        "payer_name": "Got it — do you have an insurance provider, or are you self-pay?",
        "default": "Sorry, I didn’t quite catch that — could you rephrase?"
    }

    return messages.get(field, messages["default"])

def ask_fields_node(state):
    missing = [f for f in REQUIRED_FIELDS if not state.get(f)]
    state["missing_fields"] = missing  # 🔥 always refresh

    if not missing:
        state["message"] = "All set — moving forward."
        state["step"] = "ask_question"
        return state

    field = missing[0]

    state["message"] = generate_message(
        "ask_question", field, state, OPENAI_API_KEY
    )
    state["step"] = "ask_question"

    return state

def validate_address_node(state):
    is_valid = validate_address(state)

    if not is_valid:
        state["is_address_validated"] = False
        state["message"] = "❌ I couldn’t verify that address. Could you double check it and tell me again?"
        state["step"] = "ask_question"
        return state

    state["is_address_validated"] = True
    return state

def show_appointments_node(state):
    state["data"] = get_mock_providers()
    state["message"] = "📅 Please select a provider and time below."
    state["step"] = "show_appointments"
    return state

def select_node(state):
    selection = state.get("selection")
    if selection:
        state["selected_provider"] = selection["provider"]
        state["selected_time"] = selection["time"]
    return state

def confirm_node(state):
    state["message"] = generate_message(
        "confirm_appointment", None, state, OPENAI_API_KEY
    )
    state["step"] = "confirm"
    return state

def finish_node(state):
    state["message"] = "✅ Your appointment has been scheduled!"
    state["is_complete"] = True
    return state