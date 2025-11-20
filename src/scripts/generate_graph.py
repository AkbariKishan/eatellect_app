import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.graph.workflow import HealthAnalysisWorkflow

def generate_graph_image():
    """Generate the workflow graph image."""
    try:
        workflow = HealthAnalysisWorkflow()
        graph = workflow.workflow.get_graph()
        
        # Generate PNG image
        png_data = graph.draw_mermaid_png()
        
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../image.png"))
        
        with open(output_path, "wb") as f:
            f.write(png_data)
            
        print(f"Graph image successfully generated at: {output_path}")
        
    except Exception as e:
        print(f"Error generating graph image: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    generate_graph_image()
