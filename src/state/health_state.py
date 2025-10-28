"""
State definition for health analysis workflow.
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator


class HealthAnalysisState(TypedDict):
    """State object that tracks the analysis workflow"""
    image_path: str
    product_info: dict
    barcode: str
    analysis_type: str
    nutritional_data: dict
    health_rating: int
    concerns: list[str]
    recommendations: list[str]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    needs_external_data: bool
    final_analysis: str
