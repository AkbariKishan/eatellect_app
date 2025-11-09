"""
LangGraph workflow construction with improved error handling and logging.
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.state.health_state import HealthAnalysisState
from src.agents.nodes import barcode_extraction_node
from src.agents.nodes import (
    classifier_node,
    data_extraction_node,
    llm_analysis_node
)
from src.agents.routes import route_after_classification


class HealthAnalysisWorkflow:
    """
    Workflow manager for health analysis pipeline.
    """
    
    def __init__(self):
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """Create and compile the workflow graph."""
        workflow = StateGraph(HealthAnalysisState)
        
        # Add nodes
        workflow.add_node("barcode_extractor", barcode_extraction_node)
        workflow.add_node("classifier", classifier_node)
        workflow.add_node("extract_data", data_extraction_node)
        workflow.add_node("llm_analysis", llm_analysis_node)
        
        # Set entry point
        workflow.set_entry_point("barcode_extractor")
        
        # Define workflow
        workflow.add_edge("barcode_extractor", "classifier")
        
        workflow.add_conditional_edges(
            "classifier",
            route_after_classification,
            {
                "extract_data": "extract_data",
                "fetch_external_data": END
            }
        )
        
        workflow.add_edge("extract_data", "llm_analysis")
        workflow.add_edge("llm_analysis", END)
        
        return workflow.compile()
    
    def execute(self, state: HealthAnalysisState) -> Dict[str, Any]:
        """
        Execute the workflow and return results as dictionary.
        
        Args:
            state: Initial state for workflow
            
        Returns:
            Dictionary with analysis results
        """
        print("\n=== Starting Workflow Execution ===")
        try:
            result_state = self.workflow.invoke(state)
            
            print("\n=== Final State ===")
            print(f"Result State Type: {type(result_state)}")
            print(f"Result State: {result_state}")
            
            # Check if result_state is a dictionary and extract values
            if isinstance(result_state, dict):
                result = {
                    "product_data": result_state.get("product_data", state.product_data),
                    "product_info": result_state.get("product_info", state.product_info),
                    "health_rating": result_state.get("health_rating", state.health_rating),
                    "nutritional_data": result_state.get("nutritional_data", state.nutritional_data),
                    "concerns": result_state.get("concerns", state.concerns),
                    "final_analysis": result_state.get("final_analysis", state.final_analysis),
                    "allergens": {
                        "concerns": result_state.get("concerns", state.concerns)
                    }
                }
            else:
                # If it's a state object, convert to dictionary
                result = {
                    "product_data": getattr(result_state, "product_data", state.product_data),
                    "product_info": getattr(result_state, "product_info", state.product_info),
                    "health_rating": getattr(result_state, "health_rating", state.health_rating),
                    "nutritional_data": getattr(result_state, "nutritional_data", state.nutritional_data),
                    "concerns": getattr(result_state, "concerns", state.concerns),
                    "final_analysis": getattr(result_state, "final_analysis", state.final_analysis),
                    "allergens": {
                        "concerns": getattr(result_state, "concerns", state.concerns)
                    }
                }
            
            print("\n=== Workflow Result ===")
            print(f"Product Info Present: {bool(result['product_info'])}")
            print(f"Product Data Present: {bool(result['product_data'])}")
            print(f"Result Keys: {list(result.keys())}")
            
            return result
            
        except Exception as e:
            print(f"\n=== Workflow Error ===\n{str(e)}")
            # Return a valid result structure even in case of error
            return {
                "product_data": {},
                "product_info": {},
                "health_rating": None,
                "nutritional_data": {},
                "concerns": [f"Error during analysis: {str(e)}"],
                "final_analysis": "",
                "allergens": {"concerns": []}
            }