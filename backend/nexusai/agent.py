from langsmith import traceable
from nexusai.config import LANGCHAIN_PROJECT
from nexusai.models.outputs import AgentMessage
from nexusai.tools.functions import setup_tools
from nexusai.utils.messages import build_messages
from nexusai.workflow.graph import ResearchWorkflow
from nexusai.workflow.nodes import WorkflowNodes


@traceable(project_name=LANGCHAIN_PROJECT)
async def process_query(
    query: str, history: list[AgentMessage] = [], message_callback=None
) -> AgentMessage:
    """Process a query and return the result. It allows passing previous messages to ask follow-up questions."""
    # Setup workflow
    tools = setup_tools(query)
    nodes = WorkflowNodes(tools)
    workflow = ResearchWorkflow(nodes)

    # Process the query using the agent's workflow
    messages = build_messages(history)
    result = await workflow.process_query(query, messages, message_callback)
    return result
