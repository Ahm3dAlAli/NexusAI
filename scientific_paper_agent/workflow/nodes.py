from typing import Any, Dict, List
import json
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from ..config import MODEL_NAME, TEMPERATURE
from ..models.state import AgentState
from ..prompts.system_prompts import (
    decision_making_prompt,
    planning_prompt,
    agent_prompt,
    judge_prompt
)

class DecisionMakingOutput(BaseModel):
    """Output object of the decision making node."""
    requires_research: bool = Field(description="Whether the user query requires research or not.")
    answer: str | None = Field(
        default=None,
        description="The answer to the user query. None if research is required."
    )

class JudgeOutput(BaseModel):
    """Output object of the judge node."""
    is_good_answer: bool = Field(description="Whether the answer is good or not.")
    feedback: str | None = Field(
        default=None,
        description="Feedback about why the answer is not good. None if answer is good."
    )

def format_tools_description(tools: List[BaseTool]) -> str:
    """Format the description of available tools."""
    return "\n\n".join([
        f"- {tool.name}: {tool.description}\n  Input arguments: {tool.args}"
        for tool in tools
    ])

class WorkflowNodes:
    """Implementation of the workflow nodes for the research agent."""
    
    def __init__(self, tools: List[BaseTool]):
        """Initialize workflow nodes with tools."""
        self.tools = tools
        self.tools_dict = {tool.name: tool for tool in tools}
        
        # Initialize LLMs
        self.base_llm = ChatOpenAI(
            model=MODEL_NAME,
            temperature=TEMPERATURE
        )
        self.decision_making_llm = self.base_llm.with_structured_output(
            DecisionMakingOutput
        )
        self.agent_llm = self.base_llm.bind_tools(tools)
        self.judge_llm = self.base_llm.with_structured_output(JudgeOutput)

    def decision_making_node(self, state: AgentState) -> Dict[str, Any]:
        """Entry point node that decides whether research is needed."""
        system_prompt = SystemMessage(content=decision_making_prompt)
        response: DecisionMakingOutput = self.decision_making_llm.invoke(
            [system_prompt] + state["messages"]
        )
        
        output = {"requires_research": response.requires_research}
        if response.answer:
            output["messages"] = [AIMessage(content=response.answer)]
        return output

    def planning_node(self, state: AgentState) -> Dict[str, Any]:
        """Planning node that creates a research strategy."""
        system_prompt = SystemMessage(
            content=planning_prompt.format(
                tools=format_tools_description(self.tools)
            )
        )
        response = self.base_llm.invoke([system_prompt] + state["messages"])
        return {"messages": [response]}

    def tools_node(self, state: AgentState) -> Dict[str, Any]:
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

    def agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Node that uses the LLM with tools to process results."""
        system_prompt = SystemMessage(content=agent_prompt)
        response = self.agent_llm.invoke([system_prompt] + state["messages"])
        return {"messages": [response]}

    def judge_node(self, state: AgentState) -> Dict[str, Any]:
        """Node that evaluates the quality of the final answer."""
        # End execution if the LLM failed twice
        num_feedback_requests = state.get("num_feedback_requests", 0)
        if num_feedback_requests >= 2:
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