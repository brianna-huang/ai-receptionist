from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime


@dataclass
class ConversationState:
    """
    Conversation state for AI-powered appointment scheduling agent.
    Tracks all required information and completion status.
    """
    
    # Patient Information
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    
    # Insurance Information
    payer_name: Optional[str] = None
    insurance_id: Optional[str] = None  # Optional field
    
    # Medical Information
    chief_complaint: Optional[str] = None
    
    # Demographics - Address
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    is_address_validated: bool = False
    
    # Appointment Selection
    selected_provider: Optional[str] = None
    selected_appointment_time: Optional[datetime] = None
    
    # Completion status
    is_complete: bool = False

    # Track context
    last_question_field: Optional[str] = None
    last_agent_message: Optional[str] = None
