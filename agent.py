from typing import Optional
from datetime import datetime
from state import ConversationState
from helper import extract_info_from_input
from state_machine import next_step
from llm import generate_message
import requests


class AppointmentAgent:
    """
    Main agent class for handling appointment scheduling conversations.
    Coordinates between state management, information extraction, and LLM decision-making.
    """
    
    def __init__(self, openai_api_key: str, google_maps_api_key: Optional[str] = None):
        """
        Initialize the appointment scheduling agent.
        
        Args:
            openai_api_key: OpenAI API key for LLM calls
            google_maps_api_key: Google Maps API key for address validation (optional)
        """
        self.openai_api_key = openai_api_key
        self.google_maps_api_key = google_maps_api_key
        self.state = ConversationState()
        
        # Mock available providers and times
        self.available_providers = [
            {
                "name": "Dr. Sarah Johnson",
                "specialty": "Primary Care",
                "times": ["2026-03-15 09:00", "2026-03-15 14:00", "2026-03-16 10:00"]
            },
            {
                "name": "Dr. Michael Chen",
                "specialty": "Internal Medicine",
                "times": ["2026-03-15 11:00", "2026-03-16 09:00", "2026-03-17 15:00"]
            },
            {
                "name": "Dr. Emily Rodriguez",
                "specialty": "Family Medicine",
                "times": ["2026-03-16 13:00", "2026-03-17 10:00", "2026-03-18 14:00"]
            }
        ]
    
    def process_input(self, user_input: str, selection=None) -> dict:
        # Handle structured selection FIRST
        if selection:
            self.state.selected_provider = selection["provider"]
            self.state.selected_appointment_time = selection["time"]

        # introduction text
        if user_input.strip() == "" and not self.state.full_name:
            return {
                "message": "Hi! I am an AI medical assistant. What can I help you with?",
                "data": None,
                "step": "ask_question"
            }

        # 1. Extract info
        extracted_info = extract_info_from_input(user_input, self.state)
        self._update_state(extracted_info)
        just_collected = list(extracted_info.keys())

        # detect confirmation in input
        confirmation_words = ["yes", "correct", "confirmed", "looks good"]
        if any(word in user_input.lower() for word in confirmation_words):
            if self.state.selected_provider and self.state.selected_appointment_time:
                self.state.is_confirmed = True

        # 2. Decide next step
        step, field = next_step(self.state)
        self.state.last_question_field = field

        if step != "ask_question":
            self.state.last_question_field = None

        # 3. Execute system actions
        action_result = None
        structured_data = None

        if step == "validate_address":
            action_result = self._validate_address()
            # recompute step AFTER validation
            step, field = next_step(self.state)

        elif step == "show_appointments":
            action_result, structured_data = self._show_appointments()

        elif step == "confirm_appointment":
            action_result = self._confirm_appointment()

        elif step == "finish":
            self.state.is_complete = True
            return {
                "message": "✅ Your appointment has been scheduled!",
                "data": None,
                "step": step
            }
        
        # Track last question field (for extractor)
        if step == "ask_question":
            self.state.last_question_field = field
        else:
            self.state.last_question_field = None

        # 4. Generate message via LLM
        if step == "ask_question":
            message = generate_message(
                step, field, self.state, self.openai_api_key, just_collected
            )
        else:
            message = ""

        # 5. Combine
        if action_result:
            final_message = f"{action_result}\n\n{message}"
        else:
            final_message = message

        return {
            "message": final_message,
            "data": structured_data,
            "step": step
        }
    
    def _update_state(self, extracted_info: dict) -> None:
        for field, value in extracted_info.items():
            if hasattr(self.state, field):
                if value is not None and value != "":
                    setattr(self.state, field, value)
    
    def _execute_action(self, action: str) -> Optional[str]:
        """
        Execute the specified action and return any additional message.
        
        Args:
            action: One of ["ask_question", "validate_address", "show_appointments", "confirm_appointment", "finish"]
            
        Returns:
            Additional message from action execution, or None
        """
        if action == "ask_question":
            # No additional action needed, just return the LLM's message
            return None
        
        elif action == "validate_address":
            return self._validate_address()
        
        elif action == "show_appointments":
            return self._show_appointments()
        
        elif action == "confirm_appointment":
            # return self._confirm_appointment()
            # LLM message already contains the detailed summary
            return "Confirm appointment?"
        
        elif action == "finish":
            return self._finish_appointment()
        
        return None
    
    def _validate_address(self) -> str:
        """
        Validate the address using Google Maps API.
        
        Returns:
            Validation result message
        """
        if not self.google_maps_api_key:
            return "GOOGLE_MAPS_API_KEY not found in .env file"
        
        address_string = f"{self.state.street}, {self.state.city}, {self.state.state} {self.state.zip_code}"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address_string,
            "key": self.google_maps_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "OK" and len(data["results"]) > 0:
                # Mark address as validated in state
                self.state.is_address_validated = True
                return "✅ Address validated successfully!"
            else:
                self.state.is_address_validated = False
                return "❌ Address could not be verified. Please check and try again."
                
        except Exception as e:
            self.state.is_address_validated = False
            return f"❌ Address validation error: {str(e)}"   
    
    def _show_appointments(self):
        appointments = []

        for provider in self.available_providers:
            appointments.append({
                "name": provider["name"],
                "specialty": provider["specialty"],
                "times": provider["times"]
            })

        # Keep text for display
        text = "📅 Please select a provider and time below."

        return text, appointments
        
    def _confirm_appointment(self) -> str:
        """
        Confirm the appointment.
        
        Returns:
            Confirmation message
        """
        # Format confirmation details
        confirmation = f"""
            ### 📋 Confirm Appointment

            **Patient:** {self.state.full_name}  
            **DOB:** {self.state.date_of_birth}  
            **Insurance:** {self.state.payer_name}  
            **Reason:** {self.state.chief_complaint}  

            **Address:**  
            {self.state.street}  
            {self.state.city}, {self.state.state} {self.state.zip_code}  

            **Provider:** {self.state.selected_provider}  
            **Time:** {self.state.selected_appointment_time}
            """
        return confirmation
    
    def _finish_appointment(self) -> str:
        """
        Finalize the appointment and mark state as complete.
        
        Returns:
            Confirmation message
        """
        self.state.is_complete = True
        return None
    
    def reset(self) -> None:
        """Reset the agent state for a new conversation."""
        self.state = ConversationState()
    
    def get_state(self) -> ConversationState:
        """Get the current conversation state."""
        return self.state
