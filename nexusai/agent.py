from nexusai.workflow.nodes import WorkflowNodes
from nexusai.workflow.graph import ResearchWorkflow
from nexusai.tools.functions import setup_tools
from nexusai.models.outputs import AgentMessage

async def process_query(query: str, message_callback=None) -> AgentMessage:
    # Setup workflow
    tools = setup_tools()
    nodes = WorkflowNodes(tools)
    workflow = ResearchWorkflow(nodes)
    
    # Process the query using the agent's workflow
    result = await workflow.process_query(query, message_callback)
    return result