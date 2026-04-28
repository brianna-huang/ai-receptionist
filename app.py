import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from agent_manager import AgentManager

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


class ChatResponse(BaseModel):
    response: str
    is_complete: bool


# ---- Routes ----
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    response = manager.process_message(req.session_id, req.message)
    
    agent = manager.get_agent(req.session_id)
    is_complete = agent.get_state().is_complete

    return ChatResponse(
        response=response,
        is_complete=is_complete
    )


@app.post("/reset")
def reset(session_id: str):
    manager.reset_session(session_id)
    return {"status": "reset"}