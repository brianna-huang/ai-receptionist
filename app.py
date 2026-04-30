from fastapi import FastAPI
from schemas.api import ChatRequest, ChatResponse
from graph.graph import graph
from storage.memory import get_session, save_session, initialize_state

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    state = initialize_state(get_session(req.session_id))

    # inject selection
    if req.selection:
        state["selected_provider"] = req.selection["provider"]
        state["selected_time"] = req.selection["time"]

    # FIRST MESSAGE CASE (NEW)
    if not state.get("started"):
        state["started"] = True

        # immediately ask first question
        state["message"] = (
            "Hi, I'm an AI medical assistant 👋 "
            "I can help you schedule an appointment. "
            "To get started, what is your full name?"
        )
        state["step"] = "ask_fields"
        state["missing_fields"] = ["full_name"]

        save_session(req.session_id, state)

        return ChatResponse(
            message=state["message"],
            data=None,
            step=state["step"],
            is_complete=False,
        )

    # NORMAL GRAPH EXECUTION
    result = graph.invoke({
        **state,
        "user_input": req.message,
        "selection": req.selection
    })

    state.update(result)
    save_session(req.session_id, state)

    print("STATE:", state)

    return ChatResponse(
        message=result["message"],
        data=result.get("data"),
        step=result.get("step"),
        is_complete=result.get("is_complete", False),
    )