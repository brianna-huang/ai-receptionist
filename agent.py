from typing import Optional
from datetime import datetime
from state import ConversationState
from helper import extract_info_from_input
from llm import decide_action


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
    
    def process_input(self, user_input: str) -> str:
        """
        Main function to process user input and return agent response.
        
        This method:
        1. Extracts information from user input
        2. Updates the conversation state
        3. Calls LLM to decide next action
        4. Executes the action
        5. Returns the message to show the user
        
        Args:
            user_input: The user's message
            
        Returns:
            Message to display to the user
        """
        # Step 1: Extract information from user input
        extracted_info = extract_info_from_input(user_input, self.state)
        
        # Step 2: Update state with exsracted information
        self._update_state(extracted_info)
        
        # Step 3: Call LLM to decide action
        action, message, field_being_asked = decide_action(user_input, self.state, self.openai_api_key)
        # update last question field
        setattr(self.state, "last_question_field", field_being_asked)

        # Step 4: Execute the action
        action_result = self._execute_action(action)
        
        # Step 5: Combine message with action result if needed
        if action_result:
            final_message = f"{message}\n\n{action_result}"
        else:
            final_message = message
        
        return final_message
    
    def _update_state(self, extracted_info: dict) -> None:
        """
        Update the conversation state with extracted information.
        
        Args:
            extracted_info: Dictionary of extracted field names and values
        """
        for field, value in extracted_info.items():
            if hasattr(self.state, field):
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

        import requests
        
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
    
    def _show_appointments(self) -> str:
        """
        Format and return available appointments.
        
        Returns:
            Formatted list of available providers and times
        """
        appointments_text = "📅 Available Appointments:\n\n"
        
        for i, provider in enumerate(self.available_providers, 1):
            appointments_text += f"{i}. {provider['name']} - {provider['specialty']}\n"
            appointments_text += "   Available times:\n"
            for time in provider['times']:
                # Format the time nicely
                try:
                    dt = datetime.strptime(time, "%Y-%m-%d %H:%M")
                    formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
                    appointments_text += f"   • {formatted_time}\n"
                except:
                    appointments_text += f"   • {time}\n"
            appointments_text += "\n"
        
        appointments_text += "Please let me know which provider and time you'd prefer!"
        
        return appointments_text
    
    def _confirm_appointment(self) -> str:
        """
        Confirm the appointment.
        
        Returns:
            Confirmation message
        """
        # Format confirmation details
        confirmation = "\n" + "="*50 + "\n"
        confirmation += "📋 APPOINTMENT CONFIRMATION\n"
        confirmation += "="*50 + "\n\n"
        
        confirmation += f"Patient: {self.state.full_name}\n"
        confirmation += f"Date of Birth: {self.state.date_of_birth}\n"
        confirmation += f"Insurance: {self.state.payer_name}"
        if self.state.insurance_id:
            confirmation += f" (ID: {self.state.insurance_id})"
        confirmation += f"\nReason: {self.state.chief_complaint}\n"
        confirmation += f"Address: {self.state.street}, {self.state.city}, {self.state.state} {self.state.zip_code}\n"
        
        if self.state.selected_provider:
            confirmation += f"\nProvider: {self.state.selected_provider}\n"
        if self.state.selected_appointment_time:
            if isinstance(self.state.selected_appointment_time, datetime):
                time_str = self.state.selected_appointment_time.strftime("%B %d, %Y at %I:%M %p")
            else:
                time_str = str(self.state.selected_appointment_time)
            confirmation += f"Time: {time_str}\n"
        
        confirmation += "\n" + "="*50
        
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
