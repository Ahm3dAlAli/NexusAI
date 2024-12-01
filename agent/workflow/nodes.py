from typing import Any
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from ..config import MAX_FEEDBACK_REQUESTS
from ..models.agent_state import AgentState
from ..models.outputs import DecisionMakingOutput, JudgeOutput
from ..prompts.system_prompts import (
    decision_making_prompt,
    planning_prompt,
    agent_prompt,
    judge_prompt
)

class WorkflowNodes:
    """Implementation of the workflow nodes for the research agent."""
    
    def __init__(self, tools: list[BaseTool]):
        """Initialize workflow nodes with tools."""
        self.tools = tools
        self.tools_dict = {tool.name: tool for tool in tools}
        
        # Initialize base LLMs
        self.__groq_llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0.0
        )
        self.__openai_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0
        )

        # Workflow LLMs
        self.planning_llm = self.__groq_llm
        self.decision_making_llm = self.__groq_llm.with_structured_output(
            DecisionMakingOutput
        )
        self.agent_llm = self.__openai_llm.bind_tools(tools)
        self.judge_llm = self.__openai_llm.with_structured_output(JudgeOutput)

    def __format_tools_description(self) -> str:
        """Format the description of available tools."""
        return "\n\n".join([
            f"- {tool.name}: {tool.description}\n  Input arguments: {tool.args}"
            for tool in self.tools
        ])

    def decision_making_node(self, state: AgentState) -> dict[str, Any]:
        """Entry point node that decides whether research is needed."""
        system_prompt = SystemMessage(content=decision_making_prompt)
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
                tools=self.__format_tools_description()
            )
        )
        response = self.planning_llm.invoke([system_prompt] + state["messages"])
        return {"messages": [response]}

    def tools_node(self, state: AgentState) -> dict[str, Any]:
        """Node that executes tools based on the plan."""
        outputs = []
        for tool_call in state["messages"][-1].tool_calls:
            try:
                tool_result = self.tools_dict[tool_call["name"]].invoke(
                    tool_call["args"]
                )
                outputs.append(
                    ToolMessage(
                        content=str(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
            except Exception as e:
                outputs.append(
                    ToolMessage(
                        content=f"Error executing tool {tool_call['name']}: {str(e)}",
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
        return {"messages": outputs}

    def agent_node(self, state: AgentState) -> dict[str, Any]:
        """Node that uses the LLM with tools to process results."""
        system_prompt = SystemMessage(content=agent_prompt)
        response = self.agent_llm.invoke([system_prompt] + state["messages"])
        return {"messages": [response]}

    def judge_node(self, state: AgentState) -> dict[str, Any]:
        """Node that evaluates the quality of the final answer."""
        # End execution if the LLM failed twice
        num_feedback_requests = state.get("num_feedback_requests", 0)
        if num_feedback_requests >= MAX_FEEDBACK_REQUESTS:
            return {"is_good_answer": True}

        system_prompt = SystemMessage(content=judge_prompt)
        response: JudgeOutput = self.judge_llm.invoke(
            [system_prompt] + state["messages"]
        )
        
        output = {
            "is_good_answer": response.is_good_answer,
            "num_feedback_requests": num_feedback_requests + 1
        }
        if response.feedback:
            output["messages"] = [AIMessage(content=response.feedback)]
        return output