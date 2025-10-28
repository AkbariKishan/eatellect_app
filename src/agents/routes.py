"""
Conditional routing logic for the workflow.
"""
from typing import Literal
from langgraph.graph import END
from src.state.health_state import HealthAnalysisState


def route_after_classification(state: HealthAnalysisState) -> Literal["extract_data", "fetch_external_data", END]:
    """
    Decide next step based on data availability.
    """
    if state.get("needs_external_data"):
        return "fetch_external_data"
    else:
        return "extract_data"


def route_after_extraction(state: HealthAnalysisState) -> Literal["llm_analysis", END]:
    """
    Decide if LLM analysis is needed.
    """
    if state.get("analysis_type") == "detailed":
        return "llm_analysis"
    else:
        return END
