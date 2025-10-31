"""
Eatellect - AI-Powered Food Health Analysis App
"""
import os
import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from PIL import Image
import plotly.graph_objects as go
from src.graph.workflow import HealthAnalysisWorkflow
from src.state.health_state import HealthAnalysisState
from dotenv import load_dotenv
import io
import base64

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Eatellect - Smart Food Analysis",
    page_icon="🥗",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def create_radar_chart(nutrients: dict, standards: dict) -> go.Figure:
    """Create a radar chart comparing nutrient levels to standards."""
    categories = list(nutrients.keys())
    values = list(nutrients.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Product'
    ))
    
    # Add standard values if available
    if standards:
        fig.add_trace(go.Scatterpolar(
            r=list(standards.values()),
            theta=categories,
            fill='toself',
            name='Recommended'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True
    )
    
    return fig

def create_nutrient_bars(nutrients: dict, rdi_percentages: dict) -> go.Figure:
    """Create a bar chart showing nutrient levels vs RDI."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=list(nutrients.keys()),
        y=list(rdi_percentages.values()),
        name='% of RDI'
    ))
    
    # Add 100% RDI line
    fig.add_hline(y=100, line_dash="dash", line_color="red",
                  annotation_text="100% RDI")
    
    fig.update_layout(
        title="Nutrient Levels (% of Recommended Daily Intake)",
        xaxis_title="Nutrients",
        yaxis_title="Percentage of RDI",
        showlegend=True
    )
    
    return fig

def main():
    st.title("🥗 Eatellect")
    st.subheader("AI-Powered Food Health Analysis")
    
    # Initialize workflow
    workflow = HealthAnalysisWorkflow()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload an image of the product barcode",
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_file:
        # Convert uploaded file to image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Display image
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Process image
        with st.spinner("Analyzing barcode..."):
            print("\n=== Starting Barcode Detection ===")
            barcodes = decode(image)
            print(f"Number of barcodes detected: {len(barcodes)}")
            
            if barcodes:
                barcode = barcodes[0].data.decode('utf-8')
                print(f"Decoded barcode value: {barcode}")
                print(f"Barcode type: {barcodes[0].type}")
                st.success(f"Barcode detected: {barcode}")
                
                # Process through workflow
                with st.spinner("Analyzing product..."):
                    try:
                        state = HealthAnalysisState()
                        state.barcode = barcode
                        result = workflow.execute(state)
                        
                        # Debug logging
                        print("Workflow result:", result)
                        
                        # First check if we have a valid result
                        if not result:
                            st.error("Failed to analyze product. Please try again.")
                            return
                        
                        # Get product info from the result
                        product_info = result.get('product_info', {})
                        print("Product info:", product_info)
                        
                        # More detailed check of product info
                        if not isinstance(product_info, dict):
                            print("Product info is not a dictionary:", type(product_info))
                            st.error("Invalid product information format.")
                            return
                        
                        if not product_info:
                            print("Product info is empty")
                            st.error("Could not find product information in the database.")
                            return
                        
                        if not (product_info.get('product_name') or product_info.get('brands')):
                            print("Missing required product info fields")
                            print("Available fields:", list(product_info.keys()))
                            st.error("Product information is incomplete.")
                            
                        # Create columns for layout
                        col1, col2 = st.columns([1, 1])
                    except Exception as e:
                        st.error(f"An error occurred while analyzing the product: {str(e)}")
                        return
                        
                    with col1:
                            st.subheader("Product Information")
                            if isinstance(product_info, dict):
                                st.write(f"**Name:** {product_info.get('product_name', 'N/A')}")
                                st.write(f"**Brand:** {product_info.get('brands', 'N/A')}")
                            else:
                                st.write("Product information not available")
                            
                            # Health Score - using health_rating
                            st.metric("Health Score", f"{result['health_rating']}/10" if result['health_rating'] is not None else "N/A")
                            
                            # Final Analysis
                            if result['final_analysis']:
                                st.subheader("Health Analysis")
                                st.info(result['final_analysis'])
                        
                    with col2:
                            # Health Concerns and Allergens
                            st.subheader("Health Concerns & Allergens")
                            if result['concerns']:
                                for concern in result['concerns']:
                                    st.warning(concern)
                        
                    # Nutritional Analysis
                    st.subheader("Nutritional Analysis")
                        
                    if result['nutritional_data']:
                            col3, col4 = st.columns([1, 1])
                            
                            nutrients_data = result['nutritional_data']
                            
                            with col3:
                                st.subheader("Nutritional Values (per 100g)")
                                st.write(f"**Energy:** {nutrients_data.get('energy_100g', 0)} kcal")
                                st.write(f"**Proteins:** {nutrients_data.get('proteins_100g', 0)}g")
                                st.write(f"**Carbs:** {nutrients_data.get('carbohydrates_100g', 0)}g")
                                st.write(f"**Sugars:** {nutrients_data.get('sugars_100g', 0)}g")
                                st.write(f"**Fat:** {nutrients_data.get('fat_100g', 0)}g")
                                st.write(f"**Fiber:** {nutrients_data.get('fiber_100g', 0)}g")
                            
                            with col4:
                                # Create simple bar chart of main nutrients
                                nutrients = {
                                    "Proteins": nutrients_data.get("proteins_100g", 0),
                                    "Carbs": nutrients_data.get("carbohydrates_100g", 0),
                                    "Fat": nutrients_data.get("fat_100g", 0),
                                    "Fiber": nutrients_data.get("fiber_100g", 0)
                                }
                                
                                fig = go.Figure(data=[
                                    go.Bar(
                                        x=list(nutrients.keys()),
                                        y=list(nutrients.values()),
                                        text=[f"{val:.1f}g" for val in nutrients.values()],
                                        textposition="auto"
                                    )
                                ])
                                
                                fig.update_layout(
                                    title="Main Nutrients per 100g",
                                    yaxis_title="Grams"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # If we have analysis information, show it
                            if isinstance(result['nutritional_data'], dict) and "analysis" in result['nutritional_data']:
                                analysis = result['nutritional_data']["analysis"]
                                
                                if "nutrition_claims" in analysis and analysis["nutrition_claims"]:
                                    st.subheader("Nutrition Claims")
                                    for claim in analysis["nutrition_claims"]:
                                        st.success(claim)
                                
                                if "health_insights" in analysis and analysis["health_insights"]:
                                    st.subheader("Health Insights")
                                    for insight in analysis["health_insights"]:
                                        st.info(
                                            f"**{insight['nutrient']}:** {insight['concern']}\n\n"
                                            f"💡 *Suggestion:* {insight['suggestion']}"
                                        )
                    else:
                        st.error("Could not find product information.")
            else:
                st.error("No barcode detected in the image. Please try another image.")

if __name__ == "__main__":
    main()