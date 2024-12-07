from nexusai.models.outputs import AgentMessage, AgentMessageType
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

def build_messages(history: list[AgentMessage]) -> list[BaseMessage]:
    messages = []
    for message in history:
        if message.type == AgentMessageType.system:
            messages.append(SystemMessage(content=message.content))
        elif message.type == AgentMessageType.human:
            messages.append(HumanMessage(content=message.content))
        elif message.type in [AgentMessageType.agent, AgentMessageType.final, AgentMessageType.error]:
            messages.append(AIMessage(content=message.content))
    return messages
