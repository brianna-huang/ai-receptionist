from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import *
from graph.routers import *

builder = StateGraph(AgentState)

builder.add_node("extract", extract_node)
builder.add_node("ask_fields", ask_fields_node)
builder.add_node("validate_address", validate_address_node)
builder.add_node("show_appointments", show_appointments_node)
builder.add_node("select", select_node)
builder.add_node("confirm", confirm_node)
builder.add_node("finish", finish_node)

builder.set_entry_point("extract")

builder.add_conditional_edges(
    "extract",
    route_missing,
    {
        "ask_fields": "ask_fields",
        "validate_address": "validate_address",
    },
)

builder.add_conditional_edges(
    "validate_address",
    route_after_validation,
    {
        "ask_fields": "ask_fields",
        "show_appointments": "show_appointments",
        "confirm": "confirm",
    },
)

builder.add_conditional_edges(
    "confirm",
    route_after_confirm,
    {
        "confirm": "confirm",
        "finish": "finish",
        "show_appointments": "show_appointments",
    },
)

builder.add_edge("show_appointments", END)
builder.add_edge("ask_fields", END)
builder.add_edge("finish", END)
# builder.add_edge("confirm", END)

graph = builder.compile()