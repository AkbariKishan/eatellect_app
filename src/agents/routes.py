"""
Conditional routing logic for the workflow.
"""
from langgraph.graph import END
from src.state.health_state import HealthAnalysisState


def route_after_classification(state: HealthAnalysisState) -> str:
    """
    Decide next step based on data availability.
    """
    if state.needs_external_data:
        return END
    else:
        return "extract_data"
