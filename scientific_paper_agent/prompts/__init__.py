
# scientific_paper_agent/prompts/__init__.py
"""Prompts for the Scientific Paper Agent."""
from .system_prompts import (
    decision_making_prompt,
    planning_prompt,
    agent_prompt,
    judge_prompt
)

__all__ = [
    "decision_making_prompt",
    "planning_prompt",
    "agent_prompt",
    "judge_prompt"
]