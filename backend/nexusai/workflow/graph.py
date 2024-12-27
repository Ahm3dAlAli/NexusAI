import json

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from nexusai.config import RECURSION_LIMIT
from nexusai.models.agent_state import AgentState
from nexusai.models.outputs import AgentMessage, AgentMessageType
from nexusai.utils.logger import logger
from nexusai.workflow.nodes import WorkflowNodes


class ResearchWorkflow:
    """Implementation of the langgraph workflow."""

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
            },
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
            },
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

    def __infer_message_type(self, message: BaseMessage) -> AgentMessageType:
        """Map langchain message types to agent message types."""
        if message.type == "system":
            return AgentMessageType.system
        elif message.type == "human":
            return AgentMessageType.human
        elif message.type == "ai":
            return AgentMessageType.agent
        elif message.type == "tool":
            return AgentMessageType.tool

    def __add_tool_calls_to_message(self, message: AIMessage) -> str:
        """Add tool calls to the message content."""
        content = ""
        if message.content:
            content += message.content + "\n\n"
        tool_calls_strs = []
        for tool_call in message.tool_calls:
            tool_calls_strs.append(
                f"- **Tool name:** {tool_call['name']}\n"
                f"- **Args:** {json.dumps(tool_call['args'], indent=2)}\n"
            )
        return content + "\n---\n".join(tool_calls_strs)

    async def process_query(
        self, query: str, messages: list[BaseMessage], message_callback=None
    ) -> AgentMessage:
        """Process a research query streaming the intermediate messages."""
        try:
            all_messages: list[BaseMessage] = []
            async for chunk in self.workflow.astream(
                {"messages": messages + [query]},
                config={"recursion_limit": RECURSION_LIMIT},
                stream_mode="updates",
            ):
                for updates in chunk.values():
                    if messages := updates.get("messages"):
                        for message in messages:
                            # Truncate long tool messages
                            if (
                                message.name == "download-paper"
                                and len(message.content) > 1000
                            ):
                                message = ToolMessage(
                                    content=message.content[:1000] + "[...]",
                                    name=message.name,
                                    tool_call_id=message.tool_call_id,
                                )

                            if isinstance(message, AIMessage) and message.tool_calls:
                                message.content = self.__add_tool_calls_to_message(
                                    message
                                )

                            # Send intermediate message if callback is provided
                            if message_callback:
                                msg_type = self.__infer_message_type(message)
                                await message_callback(
                                    AgentMessage(
                                        order=len(all_messages) + 1,
                                        type=msg_type,
                                        content=message.content,
                                        tool_name=(
                                            message.name
                                            if msg_type == AgentMessageType.tool
                                            else None
                                        ),
                                    )
                                )

                            all_messages.append(message)
                            logger.info(f"New message:\n{message.json(indent=2)}")

            # Return final message
            if not all_messages:
                return AgentMessage(
                    order=1,
                    type=AgentMessageType.final,
                    content="No answer provided.",
                )

            final_message = all_messages[-1]
            return AgentMessage(
                order=len(all_messages) + 1,
                type=AgentMessageType.final,
                content=final_message.content,
            )
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return AgentMessage(
                order=len(all_messages) + 1,
                type=AgentMessageType.error,
                content=str(e),
            )
