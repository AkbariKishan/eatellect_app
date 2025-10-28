"""
Main health analyzer class with agentic workflow.
"""
import os
from src.graph.workflow import create_health_analysis_graph



class AgenticHealthAnalyzer:
    """Agentic health analyzer with barcode scanning."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.graph = create_health_analysis_graph()
        
    def analyze_from_barcode_image(self, image_path: str) -> dict:
        """
        Analyze product from a barcode image.
        
        Args:
            image_path: Path to image containing product barcode
            
        Returns:
            Dictionary containing full analysis results
        """
        initial_state = {
            "image_path": image_path,
            "product_info": {},
            "barcode": "",
            "analysis_type": "",
            "nutritional_data": {},
            "health_rating": 0,
            "messages": [],
            "concerns": [],
            "recommendations": [],
            "needs_external_data": False,
            "final_analysis": ""
        }
        
        final_state = self.graph.invoke(initial_state)
    
        return {
        "barcode": final_state.get("barcode", ""),
        "product_name": final_state.get("product_info", {}).get("product_name", "Unknown"),
        "health_rating": final_state.get("health_rating", 0),
        "nutritional_data": final_state.get("nutritional_data", {}),
        "concerns": final_state.get("concerns", []),
        "analysis": final_state.get("final_analysis", ""),
        "recommendations": final_state.get("recommendations", []),
        "analysis_type": final_state.get("analysis_type", "unknown")
    }

    def analyze_product(self, product_info: dict, barcode: str = None) -> dict:
        """Original method - analyze from product info dict."""
        initial_state = {
            "image_path": "",
            "product_info": product_info,
            "barcode": barcode or "unknown",
            "analysis_type": "",
            "nutritional_data": {},
            "health_rating": 0,
            "messages": [],
            "concerns": [],
            "recommendations": [],
            "needs_external_data": False,
            "final_analysis": ""
        }
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "health_rating": final_state.get("health_rating", 0),
            "nutritional_data": final_state.get("nutritional_data", {}),
            "concerns": final_state.get("concerns", []),
            "analysis": final_state.get("final_analysis", ""),
            "recommendations": final_state.get("recommendations", []),
            "analysis_type": final_state.get("analysis_type", "unknown")
        }

