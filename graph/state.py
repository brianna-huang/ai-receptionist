from typing import TypedDict, Optional, List, Dict

class AgentState(TypedDict):
    user_input: str
    
    # user data
    full_name: Optional[str]
    date_of_birth: Optional[str]
    payer_name: Optional[str]
    chief_complaint: Optional[str]

    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]

    # system
    is_address_validated: bool
    selected_provider: Optional[str]
    selected_time: Optional[str]

    # outputs
    message: str
    data: Optional[List[Dict]]
    step: str

    # runtime
    missing_fields: List[str]
    is_complete: bool