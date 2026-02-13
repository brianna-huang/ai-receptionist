from typing import Dict, Any, Tuple
from openai import OpenAI
import json
from datetime import datetime


def get_system_prompt() -> str:
    """Load the system prompt from prompt.txt"""
    try:
        with open("prompt.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError("prompt.txt not found. Please create it in the same directory.")


def serialize_state(state: Any) -> Dict[str, Any]:
    """
    Convert the ConversationState to a JSON-serializable dictionary.
    """
    return {
        "full_name": state.full_name,
        "date_of_birth": state.date_of_birth.isoformat() if state.date_of_birth else None,
        "payer_name": state.payer_name,
        "insurance_id": state.insurance_id,
        "chief_complaint": state.chief_complaint,
        "street": state.street,
        "city": state.city,
        "state": state.state,
        "zip_code": state.zip_code,
        "is_address_validated": state.is_address_validated,
        "selected_provider": state.selected_provider,
        "selected_appointment_time": state.selected_appointment_time.isoformat() if isinstance(state.selected_appointment_time, datetime) else state.selected_appointment_time,
        "is_complete": state.is_complete,
        "last_question_field": state.last_question_field,
        "last_agent_message": state.last_agent_message
    }


def decide_action(user_input: str, state: Any, api_key: str) -> Tuple[str, str]:
    """
    Call OpenAI API to decide which action to take based on user input and current state.
    
    Args:
        user_input: The user's message
        state: Current AppointmentSchedulingState object
        api_key: OpenAI API key
        
    Returns:
        Tuple of (action, message, field_being_asked) where:
        - action: One of ["ask_question", "validate_address", "show_appointments", "confirm_appointment", "finish"]
        - message: Message to show the user
        - field_being_asked: field name being asked about if action is ask_question
    """
    client = OpenAI(api_key=api_key)
    
    # Get system prompt
    system_prompt = get_system_prompt()
    
    # Serialize state
    state_dict = serialize_state(state)
    
    # Create user message with state context
    user_message = f"""Current conversation state:
    {json.dumps(state_dict, indent=2)}

    User input: {user_input}

    Based on the current state and user input, decide the next action and provide an appropriate message."""
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    
    # Parse response
    result = json.loads(response.choices[0].message.content)
    
    action = result.get("action", "ask_question")
    message = result.get("message", "I'm not sure what to do next. Can you please provide more information?")
    field_being_asked = result.get("field_being_asked", None)
    
    # Validate action
    valid_actions = ["ask_question", "validate_address", "show_appointments", "confirm_appointment", "finish"]
    if action not in valid_actions:
        action = "ask_question"
    
    return action, message, field_being_asked