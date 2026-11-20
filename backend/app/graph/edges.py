from typing import Literal
from langgraph.graph import END
from backend.app.graph.state import AgencyState

def check_orchestrator_decision(state: AgencyState) -> Literal["outreach_agent", "__end__"]:
    """
    Decides whether to process leads or terminate (e.g. paused, quota full).
    """
    if state.get("workflow_status") in ["paused", "completed", "error"]:
        return END
    
    if state.get("current_lead"):
        return "outreach_agent"
        
    return END

def check_qa_decision(state: AgencyState) -> Literal["dispatcher", "outreach_agent"]:
    """
    Cyclic Review Loop:
    If QA passes -> go to Dispatcher.
    If QA fails -> loop back to Outreach Agent for revision.
    """
    if state.get("qa_approved", False):
        return "dispatcher"
    return "outreach_agent"

def check_batch_completion(state: AgencyState) -> Literal["outreach_agent", "self_learning"]:
    """
    Loop for remaining leads in the 5-message batch:
    If more leads remain -> continue to next lead.
    If batch complete -> trigger self-learning node.
    """
    if state.get("current_lead"):
        return "outreach_agent"
    return "self_learning"
