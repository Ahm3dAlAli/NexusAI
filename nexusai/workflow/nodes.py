import asyncio
from datetime import datetime
from typing import Any

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from nexusai.config import MAX_FEEDBACK_REQUESTS
from nexusai.models.agent_state import AgentState
from nexusai.models.outputs import DecisionMakingOutput, JudgeOutput
from nexusai.prompts.system_prompts import (agent_prompt,
                                            decision_making_prompt,
                                            judge_prompt, planning_prompt)
from nexusai.utils.messages import get_agent_messages
from nexusai.utils.logger import logger
class WorkflowNodes:
    """Implementation of the workflow nodes for the research agent."""

    def __init__(self, tools: list[BaseTool], user_id: str = None):
        """Initialize workflow nodes with tools."""
        self.tools = tools
        self.tools_dict = {tool.name: tool for tool in tools}
        self.user_id = user_id
        
        # Initialize base LLMs
        self.__base_llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.0, max_tokens=16384
        )

        # Workflow LLMs
        self.planning_llm = self.__base_llm
        self.decision_making_llm = self.__base_llm.with_structured_output(
            DecisionMakingOutput
        )
        self.agent_llm = self.__base_llm.bind_tools(tools)
        self.judge_llm = self.__base_llm.with_structured_output(JudgeOutput)

    def __format_tools_description(self) -> str:
        """Format the description of available tools."""
        return "\n\n".join(
            [
                f"- {tool.name}: {tool.description}\n  Input arguments: {tool.args}"
                for tool in self.tools
            ]
        )

    def __get_memory_context(self, query: str) -> str:
        """Get memory context if available."""
        if not self.user_id or "search_memory" not in self.tools_dict:
            return ""
        
        try:
            return self.tools_dict["search_memory"].invoke({
                "query": query,
                "user_id": self.user_id,
                "filters": {"version": "v2"}
            })
        except Exception as e:
            logger.warning(f"Error retrieving memory context: {e}")
            return ""

    def __store_interaction(self, human_msg: str, ai_msg: str) -> None:
        """Store interaction in memory if available."""
        if not self.user_id or "add_memory" not in self.tools_dict:
            return

        try:
            self.tools_dict["add_memory"].invoke({
                "messages": [
                    {"role": "user", "content": human_msg},
                    {"role": "assistant", "content": ai_msg}
                ],
                "user_id": self.user_id
            })
        except Exception as e:
            logger.warning(f"Error storing memory: {e}")

    # Update decision_making_node
    def decision_making_node(self, state: AgentState) -> dict[str, Any]:
        """Entry point node that decides whether research is needed."""
        # Get memory context if available
        memory_context = self.__get_memory_context(state["messages"][-1].content)
        
        system_prompt = SystemMessage(
            content=decision_making_prompt.format(
                current_date=datetime.now().strftime("%Y-%m-%d"),
                memory_context=memory_context
            )
        )
        response: DecisionMakingOutput = self.decision_making_llm.invoke(
            [system_prompt] + state["messages"]
        )

        # Store the interaction in memory if available
        if response.answer:
            self.__store_interaction(
                state["messages"][-1].content,
                response.answer
            )

        output = {"requires_research": response.requires_research}
        if response.answer:
            output["messages"] = [AIMessage(content=response.answer)]
        return output

    def planning_node(self, state: AgentState) -> dict[str, Any]:
        """Planning node that creates a research strategy."""
        memory_context = self.__get_memory_context(state["messages"][-1].content)
        
        system_prompt = SystemMessage(
            content=planning_prompt.format(
                tools=self.__format_tools_description(),
                current_date=datetime.now().strftime("%Y-%m-%d"),
                memory_context=memory_context
            )
        )
        response = self.planning_llm.invoke([system_prompt] + state["messages"])

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
                content=f"Error executing tool {tool_call['name']}: {str(e)}",
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
        memory_context = self.__get_memory_context(state["messages"][-1].content)
        
        system_prompt = SystemMessage(
            content=agent_prompt.format(
                tools=self.__format_tools_description(),
                current_date=datetime.now().strftime("%Y-%m-%d"),
                memory_context=memory_context
            )
        )
        messages = get_agent_messages(state)
        response = self.agent_llm.invoke([system_prompt] + messages)

        # Store significant interactions (non-tool responses)
        if not response.tool_calls:
            self.__store_interaction(
                state["messages"][-1].content,
                response.content
            )

        return {"messages": [response]}

    def judge_node(self, state: AgentState) -> dict[str, Any]:
        """Node that evaluates the quality of the final answer."""
        memory_context = self.__get_memory_context(state["messages"][-1].content)
        
        if num_feedback_requests := state.get("num_feedback_requests", 0) >= MAX_FEEDBACK_REQUESTS:
            return {"is_good_answer": True}

        system_prompt = SystemMessage(
            content=judge_prompt.format(
                current_date=datetime.now().strftime("%Y-%m-%d"),
                memory_context=memory_context
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
