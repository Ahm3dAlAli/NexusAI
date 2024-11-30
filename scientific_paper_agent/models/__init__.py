# scientific_paper_agent/models/__init__.py
"""Models for the Scientific Paper Agent."""
from .state import AgentState

__all__ = ["AgentState"]

# scientific_paper_agent/models/state.py
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The state of the agent during the paper research process."""
    requires_research: bool
    num_feedback_requests: int
    is_good_answer: bool
    messages: Annotated[Sequence[BaseMessage], add_messages]
