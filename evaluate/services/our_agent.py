
from typing import Dict, Any
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from nexusai.workflow.nodes import WorkflowNodes
from nexusai.workflow.graph import ResearchWorkflow
from nexusai.tools.functions import setup_tools
from .base import BaseServiceEvaluator

class OurAgentEvaluator(BaseServiceEvaluator):
    """Evaluator for our research agent."""
    
    def __init__(self, service_config):
        super().__init__(service_config)
        # Initialize our agent's components
        tools = setup_tools()
        self.nodes = WorkflowNodes(tools)
        self.workflow = ResearchWorkflow(self.nodes)
        
    async def query(self, text: str) -> Dict[str, Any]:
        """Execute a query using our agent."""
        try:
            # Process the query using our workflow
            result = await self.workflow.process_query(text,[])
            
            # Handle error cases
            if "error" in result:
                raise Exception(result["error"])
            
            # Return result in standard format
            return {
                "answer": result.content,
                "metadata": {
                    "model_used": "gpt-4o-mini",
                    "tools_used": ["search-papers", "download-paper", "ask-human-feedback"],
                    "tokens":result.get("response_metadata", {}).get("toke_usage", {}).get("completion_token"),
                    "price": 0.015
                }
            }
        except Exception as e:
            raise Exception(f"Error in our agent: {str(e)}")