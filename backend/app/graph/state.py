from typing import TypedDict, List, Dict, Any, Optional

class AgencyState(TypedDict):
    """
    LangGraph Central State Machine:
    Maintains the state across all nodes (CEO, Outreach, QA, Evaluator).
    """
    campaign_id: str
    campaign_name: str
    campaign_status: str       # 'Active', 'Paused', 'Stopped'
    daily_quota: int           # e.g. 5
    sent_today: int            # How many sent so far today
    
    leads_to_process: List[Dict[str, Any]]
    current_lead: Optional[Dict[str, Any]]
    
    generated_message: Optional[str]
    qa_approved: bool
    qa_feedback: Optional[str]
    
    retry_count: int
    learned_insights: List[str]
    
    workflow_status: str       # 'running', 'paused', 'completed', 'error'
    logs: List[str]
