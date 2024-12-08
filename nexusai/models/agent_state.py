from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """The state of the agent during the paper research process."""

    requires_research: bool
    current_planning: AIMessage
    num_feedback_requests: int
    is_good_answer: bool
    messages: Annotated[Sequence[BaseMessage], add_messages]
