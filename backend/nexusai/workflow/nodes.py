import asyncio
from datetime import datetime
from typing import Any

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from nexusai.config import LLM_PROVIDER, MAX_FEEDBACK_REQUESTS
from nexusai.models.agent_state import AgentState
from nexusai.models.outputs import DecisionMakingOutput, JudgeOutput
from nexusai.prompts.system_prompts import (
    agent_prompt,
    decision_making_prompt,
    judge_prompt,
    planning_prompt,
)
from nexusai.utils.messages import get_agent_messages


class WorkflowNodes:
    """Implementation of the workflow nodes for the research agent."""

    def __init__(self, tools: list[BaseTool]):
        """Initialize workflow nodes with tools."""
        self.tools = tools
        self.tools_dict = {tool.name: tool for tool in tools}

        # Initialize base LLMs
        if LLM_PROVIDER == "openai":
            small_llm = ChatOpenAI(
                model="gpt-4o-mini", temperature=0.0, max_tokens=16384
            )
            large_llm = None
        elif LLM_PROVIDER == "azure":
            small_llm = AzureChatOpenAI(
                azure_deployment="gpt-4o-mini", temperature=0.0, max_tokens=16384
            )
            large_llm = AzureChatOpenAI(
                azure_deployment="gpt-4o", temperature=0.0, max_tokens=16384
            )
        else:
            raise ValueError(f"Invalid LLM provider: {LLM_PROVIDER}")

        # Workflow LLMs
        self.decision_making_llm = small_llm.with_structured_output(
            DecisionMakingOutput
        )
        self.planning_llm = large_llm or small_llm
        self.agent_llm = (large_llm or small_llm).bind_tools(tools)
        self.judge_llm = (large_llm or small_llm).with_structured_output(JudgeOutput)

    def __format_tools_description(self) -> str:
        """Format the description of available tools."""
        return "\n\n".join(
            [
                f"- {tool.name}: {tool.description}\n  Input arguments: {tool.args}"
                for tool in self.tools
            ]
        )

    def decision_making_node(self, state: AgentState) -> dict[str, Any]:
        """Entry point node that decides whether research is needed."""
        system_prompt = SystemMessage(
            content=decision_making_prompt.format(
                current_date=datetime.now().strftime("%Y-%m-%d"),
            )
        )
        response: DecisionMakingOutput = self.decision_making_llm.invoke(
            [system_prompt] + state["messages"]
        )

        output = {"requires_research": response.requires_research}
        if response.answer:
            output["messages"] = [AIMessage(content=response.answer)]
        return output

    def planning_node(self, state: AgentState) -> dict[str, Any]:
        """Planning node that creates a research strategy."""
        system_prompt = SystemMessage(
            content=planning_prompt.format(
                tools=self.__format_tools_description(),
                current_date=datetime.now().strftime("%Y-%m-%d"),
            )
        )
        response = self.planning_llm.invoke([system_prompt] + state["messages"])

        # Add the latest planning to the state for easier access
        return {"messages": [response], "current_planning": response}

    async def __execute_tool_call(self, tool_call: dict) -> ToolMessage:
        """Execute a single tool call asynchronously."""
        try:
            tool_result = await self.tools_dict[tool_call["name"]].ainvoke(
                tool_call["args"]
            )
            return ToolMessage(
                content=str(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Error executing tool {tool_call['name']}: {e}",
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )

    def tools_node(self, state: AgentState) -> dict[str, Any]:
        """Node that executes tool calls based on the plan. It runs them asynchronously to reduce latency."""

        async def run_tool_calls() -> list[ToolMessage]:
            tasks = [
                self.__execute_tool_call(tool_call)
                for tool_call in state["messages"][-1].tool_calls
            ]
            return await asyncio.gather(*tasks)

        outputs = asyncio.run(run_tool_calls())
        return {"messages": outputs}

    def agent_node(self, state: AgentState) -> dict[str, Any]:
        """Node that uses the LLM with tools to process results."""
        system_prompt = SystemMessage(
            content=agent_prompt.format(
                tools=self.__format_tools_description(),
                current_date=datetime.now().strftime("%Y-%m-%d"),
            )
        )
        messages = get_agent_messages(state)
        response = self.agent_llm.invoke([system_prompt] + messages)
        return {"messages": [response]}

    def judge_node(self, state: AgentState) -> dict[str, Any]:
        """Node that evaluates the quality of the final answer."""
        # End execution if the LLM failed twice
        num_feedback_requests = state.get("num_feedback_requests", 0)
        if num_feedback_requests >= MAX_FEEDBACK_REQUESTS:
            return {"is_good_answer": True}

        system_prompt = SystemMessage(
            content=judge_prompt.format(
                current_date=datetime.now().strftime("%Y-%m-%d")
            )
        )
        response: JudgeOutput = self.judge_llm.invoke(
            [system_prompt] + state["messages"]
        )

        output = {
            "is_good_answer": response.is_good_answer,
            "num_feedback_requests": num_feedback_requests + 1,
        }
        if response.feedback:
            output["messages"] = [AIMessage(content=response.feedback)]
        return output
