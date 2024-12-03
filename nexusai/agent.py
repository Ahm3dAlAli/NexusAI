from typing import Any

from nexusai.workflow.nodes import WorkflowNodes
from nexusai.workflow.graph import ResearchWorkflow
from nexusai.tools.functions import setup_tools

async def process_query(query: str) -> dict[str, Any]:
    # Setup workflow
    tools = setup_tools()
    nodes = WorkflowNodes(tools)
    workflow = ResearchWorkflow(nodes)
    
    # Process the query using the agent's workflow
    result = await workflow.process_query(query)
    return result