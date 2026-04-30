from pydantic import BaseModel
from typing import Optional, List, Dict


class ChatRequest(BaseModel):
    session_id: str
    message: str
    selection: Optional[Dict] = None


class ChatResponse(BaseModel):
    message: str
    data: Optional[List[Dict]] = None
    step: str
    is_complete: bool