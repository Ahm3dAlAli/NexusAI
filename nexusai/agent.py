from nexusai.workflow.nodes import WorkflowNodes
from nexusai.workflow.graph import ResearchWorkflow
from nexusai.tools.functions import setup_tools
from nexusai.models.outputs import AgentMessage, AgentMessageType
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

def __build_messages(history: list[AgentMessage]) -> list[BaseMessage]:
    messages = []
    for message in history:
        if message.type == AgentMessageType.system:
            messages.append(SystemMessage(content=message.content))
        elif message.type == AgentMessageType.human:
            messages.append(HumanMessage(content=message.content))
        elif message.type in [AgentMessageType.agent, AgentMessageType.final, AgentMessageType.error]:
            messages.append(AIMessage(content=message.content))
    return messages

async def process_query(query: str, history: list[AgentMessage] = [], message_callback=None) -> AgentMessage:
    # Setup workflow
    tools = setup_tools()
    nodes = WorkflowNodes(tools)
    workflow = ResearchWorkflow(nodes)
    
    # Process the query using the agent's workflow
    messages = __build_messages(history)
    result = await workflow.process_query(query, messages, message_callback)
    return result