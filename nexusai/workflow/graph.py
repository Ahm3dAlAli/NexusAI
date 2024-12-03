from typing import Any
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import BaseMessage, ToolMessage

from ..models.agent_state import AgentState
from ..workflow.nodes import WorkflowNodes

class ResearchWorkflow:
    """Implementation of the research workflow graph."""
    
    def __init__(self, nodes: WorkflowNodes):
        """Initialize the workflow with nodes."""
        self.nodes = nodes
        self.workflow = self.__build_workflow()

    def __build_workflow(self) -> CompiledStateGraph:
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
            self.__decision_making_router,
            {
                "planning": "planning",
                "end": END,
            }
        )
        workflow.add_edge("planning", "agent")
        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges(
            "agent",
            self.__agent_action_router,
            {
                "continue": "tools",
                "end": "judge",
            },
        )
        workflow.add_conditional_edges(
            "judge",
            self.__final_answer_router,
            {
                "planning": "planning",
                "end": END,
            }
        )

        return workflow.compile()

    @staticmethod
    def __decision_making_router(state: AgentState) -> str:
        """Route based on whether research is required."""
        if state["requires_research"]:
            return "planning"
        return "end"

    @staticmethod
    def __agent_action_router(state: AgentState) -> str:
        """Determine if the agent should continue processing."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Continue if there are tool calls, otherwise end
        return "continue" if last_message.tool_calls else "end"

    @staticmethod
    def __final_answer_router(state: AgentState) -> str:
        """Route based on the quality of the answer."""
        if state["is_good_answer"]:
            return "end"
        return "planning"

    async def __astream(self, input: str) -> BaseMessage | None:
        """Stream the results of the workflow."""
        # Stream the results 
        all_messages = []
        async for chunk in self.workflow.astream({"messages": [input]}, stream_mode="updates"):
            for updates in chunk.values():
                if messages := updates.get("messages"):
                    all_messages.extend(messages)
                    for message in messages:
                        if isinstance(message, ToolMessage) and len(message.content) > 1000:
                            message = ToolMessage(
                                content=message.content[:1000] + " [...]",
                                name=message.name,
                                tool_call_id=message.tool_call_id,
                            )
                        message.pretty_print()

        # Return the last message if any
        if not all_messages:
            return None
        return all_messages[-1]

    async def process_query(self, query: str) -> dict[str, Any]:
        """Process a research query through the workflow."""
        try:
            final_message = await self.__astream(query)
            return {"answer": final_message.content or "No answer provided."}
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return {"error": str(e)}