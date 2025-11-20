"""
State definition for health analysis workflow.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from langchain_core.messages import BaseMessage


@dataclass
class HealthAnalysisState:
    """State object that tracks the analysis workflow."""
    
    # Input data
    image_path: str = ""
    barcode: str = ""
    
    # Product information
    product_data: Dict[str, Any] = field(default_factory=dict)
    product_info: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis results
    analysis_type: str = ""
    nutritional_data: Dict[str, Any] = field(default_factory=dict)
    health_rating: float = 0.0
    concerns: List[str] = field(default_factory=list)
    final_analysis: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # Agentic features
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    user_context: Dict[str, Any] = field(default_factory=lambda: {"dietary_goals": [], "allergens": []})
    search_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Processing flags
    needs_external_data: bool = False
    
    # Message history
    messages: List[BaseMessage] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize optional fields if not provided."""
        if self.nutritional_data is None:
            self.nutritional_data = {}
