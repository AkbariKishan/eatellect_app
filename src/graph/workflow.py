"""
LangGraph workflow construction.
"""
from langgraph.graph import StateGraph, END
from src.state.health_state import HealthAnalysisState
from src.agents.nodes import (
    classifier_node,
    data_extraction_node,
    llm_analysis_node,
    recommendation_node,
    barcode_extraction_node
)
from src.agents.routes import route_after_classification


def create_health_analysis_graph():
    """
    Create and compile the agentic workflow graph.
    """
    workflow = StateGraph(HealthAnalysisState)
    
    # Add nodes
    workflow.add_node("barcode_extractor", barcode_extraction_node)  # NEW
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("extract_data", data_extraction_node)
    workflow.add_node("llm_analysis", llm_analysis_node)
    workflow.add_node("recommendations", recommendation_node)
    
    # Set entry point to barcode extraction
    workflow.set_entry_point("barcode_extractor")  # CHANGED
    
    # After barcode extraction, go to classifier
    workflow.add_edge("barcode_extractor", "classifier")  # NEW
    
    # Conditional routing after classification
    workflow.add_conditional_edges(
        "classifier",
        route_after_classification,
        {
            "extract_data": "extract_data",
            "fetch_external_data": END,
            END: END
        }
    )
    
    workflow.add_edge("extract_data", "llm_analysis")
    workflow.add_edge("llm_analysis", "recommendations")
    workflow.add_edge("recommendations", END)
    
    return workflow.compile()
