
from typing import Dict, Any
from langgraph.graph import END, StateGraph

from ..models.state import AgentState

class ResearchWorkflow:
    """Implementation of the research workflow graph."""
    
    def __init__(self, nodes):
        """Initialize the workflow with nodes."""
        self.nodes = nodes
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build and compile the workflow graph."""
        # Initialize the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("decision_making", self.nodes.decision_making_node)
        workflow.add_node("planning", self.nodes.planning_node)
        workflow.add_node("tools", self.nodes.tools_node)
        workflow.add_node("agent", self.nodes.agent_node)
        workflow.add_node("judge", self.nodes.judge_node)

        # Set entry point
        workflow.set_entry_point("decision_making")

        # Add edges with conditional routing
        workflow.add_conditional_edges(
            "decision_making",
            self._router,
            {
                "planning": "planning",
                "end": END,
            }
        )
        workflow.add_edge("planning", "agent")
        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": "judge",
            },
        )
        workflow.add_conditional_edges(
            "judge",
            self._final_answer_router,
            {
                "planning": "planning",
                "end": END,
            }
        )

        return workflow.compile()

    @staticmethod
    def _router(state: AgentState) -> str:
        """Route based on whether research is required."""
        if state["requires_research"]:
            return "planning"
        return "end"

    @staticmethod
    def _should_continue(state: AgentState) -> str:
        """Determine if the agent should continue processing."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Continue if there are tool calls, otherwise end
        return "continue" if last_message.tool_calls else "end"

    @staticmethod
    def _final_answer_router(state: AgentState) -> str:
        """Route based on the quality of the answer."""
        if state["is_good_answer"]:
            return "end"
        return "planning"

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a research query through the workflow."""
        try:
            return await self.workflow.arun({"messages": [query]})
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return {"error": str(e)}