from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from backend.app.graph.state import AgencyState
from backend.app.graph.nodes import (
    orchestrator_node,
    outreach_agent_node,
    qa_evaluator_node,
    dispatcher_node,
    self_learning_node
)
from backend.app.graph.edges import (
    check_orchestrator_decision,
    check_qa_decision,
    check_batch_completion
)

def create_agency_graph():
    """
    Constructs the Production LangGraph Multi-Agent Architecture.
    Fully cyclic, resilient, with QA review loops and self-learning.
    """
    builder = StateGraph(AgencyState)

    # 1. Register Agent Nodes
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("outreach_agent", outreach_agent_node)
    builder.add_node("qa_evaluator", qa_evaluator_node)
    builder.add_node("dispatcher", dispatcher_node)
    builder.add_node("self_learning", self_learning_node)

    # 2. Define Execution Graph Edges
    builder.add_edge(START, "orchestrator")

    # From Orchestrator -> conditional branch
    builder.add_conditional_edges(
        "orchestrator",
        check_orchestrator_decision,
        {
            "outreach_agent": "outreach_agent",
            END: END
        }
    )

    # From Outreach Agent -> QA Evaluator
    builder.add_edge("outreach_agent", "qa_evaluator")

    # From QA Evaluator -> conditional review loop (Pass to Dispatcher OR Re-try)
    builder.add_conditional_edges(
        "qa_evaluator",
        check_qa_decision,
        {
            "dispatcher": "dispatcher",
            "outreach_agent": "outreach_agent"
        }
    )

    # From Dispatcher -> check if more leads in batch or complete
    builder.add_conditional_edges(
        "dispatcher",
        check_batch_completion,
        {
            "outreach_agent": "outreach_agent",
            "self_learning": "self_learning"
        }
    )

    builder.add_edge("self_learning", END)

    # Checkpointer for State persistence and time-travel
    checkpointer = MemorySaver()
    app = builder.compile(checkpointer=checkpointer)
    return app

agency_graph = create_agency_graph()
