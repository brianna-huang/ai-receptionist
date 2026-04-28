import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from agent_manager import AgentManager
from typing import Optional, List, Dict

load_dotenv()

app = FastAPI()

# Load keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

manager = AgentManager(OPENAI_API_KEY, GOOGLE_MAPS_API_KEY)


# ---- Request/Response Models ----
class ChatRequest(BaseModel):
    session_id: str
    message: str
    selection: Optional[Dict] = None

class ChatResponse(BaseModel):
    message: str
    data: Optional[List[Dict]] = None
    step: str
    is_complete: bool


# ---- Routes ----
@app.post("/chat", response_model=ChatResponse)
# def chat(req: ChatRequest):
#     result = manager.process_message(
#         req.session_id,
#         req.message,
#         selection=req.selection
#     )
    
#     agent = manager.get_agent(req.session_id)

#     return ChatResponse(
#         message=result["message"],
#         data=result.get("data"),
#         step=result["step"],
#         is_complete=agent.get_state().is_complete
#     )
def chat(req: ChatRequest):
    agent = manager.get_agent(req.session_id)

    if req.selection:
        agent.state.selected_provider = req.selection["provider"]
        agent.state.selected_appointment_time = req.selection["time"]

        result = agent.process_input("", selection=req.selection)  # trigger next step
    else:
        result = agent.process_input(req.message)

    return ChatResponse(
        message=result["message"],
        data=result.get("data"),
        step=result["step"],
        is_complete=agent.get_state().is_complete
    )
    


@app.post("/reset")
def reset(session_id: str):
    manager.reset_session(session_id)
    return {"status": "reset"}