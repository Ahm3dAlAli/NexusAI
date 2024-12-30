from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)
from nexusai.models.agent_state import AgentState
from nexusai.models.outputs import AgentMessage, AgentMessageType


def build_messages(history: list[AgentMessage]) -> list[BaseMessage]:
    """Build a list of langchain messages from the agent history."""
    messages = []
    for message in history:
        if message.type == AgentMessageType.system:
            messages.append(SystemMessage(content=message.content))
        elif message.type == AgentMessageType.human:
            messages.append(HumanMessage(content=message.content))
        elif message.type in [
            AgentMessageType.agent,
            AgentMessageType.final,
            AgentMessageType.error,
        ]:
            messages.append(AIMessage(content=message.content))
    return messages


def get_agent_messages(state: AgentState) -> list[BaseMessage]:
    """Get the relevant context for the agent to use.

    To make the agent more responsive to the current planning, we remove all messages between the last human message and the last planning message,
    and add the current planning message at the end.

    This removes all the context from previous failed attempts to answer the question.
    """
    last_human_message = next(
        (msg for msg in reversed(state["messages"]) if msg.type == "human"), None
    )
    current_planning_message = next(
        (
            msg
            for msg in reversed(state["messages"])
            if msg == state["current_planning"]
        ),
        None,
    )
    return (
        state["messages"][: state["messages"].index(last_human_message) + 1]
        + state["messages"][state["messages"].index(current_planning_message) :]
    )
