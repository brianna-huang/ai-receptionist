from typing import Dict
from agent import AppointmentAgent


class AgentManager:
    """
    Manages multiple user sessions.
    Each session gets its own AppointmentAgent instance.
    """

    def __init__(self, openai_api_key: str, google_maps_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.google_maps_api_key = google_maps_api_key
        self.sessions: Dict[str, AppointmentAgent] = {}

    def get_agent(self, session_id: str) -> AppointmentAgent:
        """Get or create an agent for a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = AppointmentAgent(
                self.openai_api_key,
                self.google_maps_api_key
            )
        return self.sessions[session_id]

    def process_message(self, session_id: str, user_input: str) -> str:
        """Process a message for a specific session."""
        agent = self.get_agent(session_id)
        return agent.process_input(user_input)

    def reset_session(self, session_id: str):
        """Reset a user's session."""
        if session_id in self.sessions:
            self.sessions[session_id].reset()