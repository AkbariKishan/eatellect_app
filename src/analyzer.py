"""
Main health analyzer class with agentic workflow.
"""
import os
from src.graph.workflow import create_health_analysis_graph
from src.state.health_state import HealthAnalysisState



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
        # Create initial state using the HealthAnalysisState class
        initial_state = HealthAnalysisState(
            image_path=image_path,
            barcode="",  # Will be extracted from image
            product_data={},
            product_info={},
            analysis_type="",
            nutritional_data={},
            health_rating=0.0,
            concerns=[],
            final_analysis="",
            recommendations=[],
            needs_external_data=False,
            messages=[]
        )
        
        final_state = self.graph.invoke(initial_state)
    
        # Extract data from the final state
        return {
            "barcode": getattr(final_state, "barcode", ""),
            "product_name": getattr(final_state, "product_info", {}).get("product_name", "Unknown"),
            "health_rating": getattr(final_state, "health_rating", 0),
            "nutritional_data": getattr(final_state, "nutritional_data", {}),
            "concerns": getattr(final_state, "concerns", []),
            "analysis": getattr(final_state, "final_analysis", ""),
            "recommendations": getattr(final_state, "recommendations", []),
            "analysis_type": getattr(final_state, "analysis_type", "unknown")
        }

    def analyze_product(self, product_info: dict, barcode: str = None) -> dict:
        """Original method - analyze from product info dict."""
        initial_state = HealthAnalysisState(
            image_path="",
            product_info=product_info,
            barcode=barcode or "unknown",
            product_data=product_info,  # Set both for compatibility
            analysis_type="",
            nutritional_data={},
            health_rating=0.0,
            concerns=[],
            recommendations=[],
            needs_external_data=False,
            final_analysis="",
            messages=[]
        )
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "health_rating": getattr(final_state, "health_rating", 0),
            "nutritional_data": getattr(final_state, "nutritional_data", {}),
            "concerns": getattr(final_state, "concerns", []),
            "analysis": getattr(final_state, "final_analysis", ""),
            "recommendations": getattr(final_state, "recommendations", []),
            "analysis_type": getattr(final_state, "analysis_type", "unknown")
        }

