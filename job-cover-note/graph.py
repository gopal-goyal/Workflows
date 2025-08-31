from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import State
from nodes import extract_company_details, draft_cover_note, send_email_node

def build_graph(checkpointer=None):
    builder = StateGraph(State)

    # Define Nodes
    builder.add_node("extract_company_details", extract_company_details)
    builder.add_node("draft_cover_note", draft_cover_note)
    builder.add_node("send_email", send_email_node)

    # Set Entry Point
    builder.set_entry_point("extract_company_details")

    # Define Edges
    builder.add_edge("extract_company_details", "draft_cover_note")
    builder.add_edge("draft_cover_note", "send_email")
    builder.add_edge("send_email", END)

    return builder.compile(
        interrupt_before=["send_email"],
        checkpointer=checkpointer or MemorySaver(),
    )
