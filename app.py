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

# Custom CSS for professional look with theme support
st.markdown("""
    <style>
    /* Theme variables */
    [data-theme="light"] {
        --background-color: #ffffff;
        --text-color: #2c3e50;
        --card-bg: #f0f2f6;
        --border-color: #eee;
        --shadow: rgba(0,0,0,0.1);
        --logo-color: #2c3e50;
    }
    
    [data-theme="dark"] {
        --background-color: #0e1117;
        --text-color: #ffffff;
        --card-bg: #1a1c23;
        --border-color: #2d3139;
        --shadow: rgba(0,0,0,0.3);
        --logo-color: #ffffff;
    }
    
    /* Logo styles */
    .app-header {
        padding: 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        background: var(--card-bg);
        border-bottom: 2px solid var(--border-color);
        box-shadow: 0 2px 4px var(--shadow);
    }
    
    .app-header:hover {
        box-shadow: 0 3px 6px var(--shadow);
        transition: all 0.3s ease;
    }
    
    .main {
        padding: 0rem 1rem;
        color: var(--text-color);
    }
    
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    
    .metric-card {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px var(--shadow);
        color: var(--text-color);
    }
    
    .citation {
        font-size: 0.8rem;
        color: var(--text-color);
        opacity: 0.7;
        border-left: 3px solid var(--border-color);
        padding-left: 1rem;
        margin: 1rem 0;
    }
    
    .health-score {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: var(--card-bg);
        border-radius: 1rem;
        margin: 1rem 0;
    }
    
    .section-header {
        color: var(--text-color);
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .insight-card {
        background: var(--card-bg);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px var(--shadow);
        color: var(--text-color);
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
    # Custom container for header with logo
    st.markdown(
        '''
        <div class="app-header">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 2.5rem; line-height: 1;">🥗</div>
                <div>
                    <div style="font-size: 2rem; font-weight: bold; color: var(--text-color);">Eatellect</div>
                    <div style="font-size: 1.1rem; opacity: 0.8; color: var(--text-color);">Professional Food Health Analysis</div>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Initialize workflow
    workflow = HealthAnalysisWorkflow()
    
    # Scanner options with instructions
    st.markdown("""
        <div class='section-header'>
        📸 Product Scanner
        </div>
    """, unsafe_allow_html=True)
    
    scan_option = st.radio(
        "Choose scanning method:",
        ["Upload Image", "Live Camera"], 
        horizontal=True
    )
    
    image = None
    if scan_option == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload a product barcode image",
            type=["jpg", "jpeg", "png"]
        )
        
        if not uploaded_file:
            st.info("👋 Welcome! Upload a clear image of your product's barcode to get started.")
        
        if uploaded_file:
            try:
                # Read the file once
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if image is None:
                    st.error("Failed to process the uploaded image. Please try another image.")
                    return
            except Exception as e:
                st.error(f"Error processing uploaded image: {str(e)}")
                return
    else:
        st.info("📸 Point your camera at the product's barcode")
        camera_image = st.camera_input("Take a photo")
        
        if camera_image:
            try:
                # Read the camera image once
                file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if image is None:
                    st.error("Failed to process the camera image. Please try again.")
                    return
            except Exception as e:
                st.error(f"Error processing camera image: {str(e)}")
                return
        else:
            st.info("Waiting for camera capture...")
            
    if image is not None:
        # Create two columns for image display
        img_col1, img_col2 = st.columns([1, 1])
        
        with img_col1:
            st.markdown("##### Scanned Barcode")
            # Convert BGR to RGB for proper display
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            st.image(image_rgb, caption="Scanned Barcode Image", use_column_width=True)
        
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
                            st.markdown("""
                                <div class='section-header'>
                                🏷️ Product Details
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if isinstance(product_info, dict):
                                # Product image display
                                product_image_url = None
                                # Try to get image URL from different possible sources
                                if 'image_url' in product_info:
                                    product_image_url = product_info['image_url']
                                elif 'image_front_url' in product_info:
                                    product_image_url = product_info['image_front_url']
                                elif 'image_small_url' in product_info:
                                    product_image_url = product_info['image_small_url']
                                
                                if product_image_url:
                                    try:
                                        st.image(product_image_url, 
                                                caption="Product Image",
                                                width=200)
                                    except Exception as e:
                                        st.warning("Could not load product image")
                                        print(f"Error loading product image: {str(e)}")
                                
                                st.markdown(f"""
                                    <div class='metric-card'>
                                    <h3>{product_info.get('product_name', 'N/A')}</h3>
                                    <p><strong>Brand:</strong> {product_info.get('brands', 'N/A')}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.write("Product information not available")
                            
                            # Health Score with professional styling
                            if result['health_rating'] is not None:
                                try:
                                    # Convert to float if it's a tuple or string
                                    score = float(result['health_rating'] if isinstance(result['health_rating'], (int, float)) 
                                                else result['health_rating'][0] if isinstance(result['health_rating'], tuple) 
                                                else 0)
                                    # Ensure score is between 0 and 10
                                    score = min(max(score, 0), 10)
                                    color = "#2ecc71" if score >= 7 else "#f1c40f" if score >= 4 else "#e74c3c"
                                    st.markdown(f"""
                                        <div class='health-score' style='color: {color}'>
                                        {score:.1f}/10
                                        <div style='font-size: 1rem; color: #666;'>Health Score</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                except (ValueError, IndexError) as e:
                                    print(f"Error processing health score: {e}")
                                    st.markdown("""
                                        <div class='health-score' style='color: #666'>
                                        N/A
                                        <div style='font-size: 1rem; color: #666;'>Health Score</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                            
                            # Key findings from analysis
                            if result['final_analysis']:
                                st.markdown("""
                                    <div class='section-header'>
                                    🔍 Key Findings
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Extract key points from analysis
                                analysis = result['final_analysis']
                                # Limit to 3-4 key points
                                key_points = analysis.split("\n\n")[:3]
                                for point in key_points:
                                    if point.strip():
                                        st.markdown(f"""
                                            <div class='insight-card'>
                                            {point.strip()}
                                            </div>
                                        """, unsafe_allow_html=True)
                        
                    with col2:
                            # Health Concerns and Allergens
                            st.markdown("""
                                <div class='section-header'>
                                ⚠️ Health Alerts
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if result['concerns']:
                                for concern in result['concerns']:
                                    if isinstance(concern, dict):
                                        st.markdown(f"""
                                            <div class='insight-card' style='border-left-color: #e74c3c'>
                                            <strong>{concern.get('type', 'Alert')}:</strong><br>
                                            {concern.get('description', '')}
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                            <div class='insight-card' style='border-left-color: #e74c3c'>
                                            {concern}
                                            </div>
                                        """, unsafe_allow_html=True)
                        
                    # Nutritional Analysis
                    st.markdown("""
                        <div class='section-header'>
                        📊 Nutritional Profile
                        </div>
                    """, unsafe_allow_html=True)
                        
                    if result['nutritional_data']:
                            col3, col4 = st.columns([1, 1])
                            
                            nutrients_data = result['nutritional_data']
                            
                            with col3:
                                st.markdown("""
                                    <div style='background: var(--card-bg); padding: 1rem; border-radius: 0.5rem;'>
                                    <h4 style='margin-bottom: 1rem; color: var(--text-color);'>Nutrition Facts (per 100g)</h4>
                                """, unsafe_allow_html=True)
                                
                                nutrients = [
                                    ("Energy", nutrients_data.get('energy_100g', 0), "kcal"),
                                    ("Proteins", nutrients_data.get('proteins_100g', 0), "g"),
                                    ("Carbohydrates", nutrients_data.get('carbohydrates_100g', 0), "g"),
                                    ("Sugars", nutrients_data.get('sugars_100g', 0), "g"),
                                    ("Fat", nutrients_data.get('fat_100g', 0), "g"),
                                    ("Fiber", nutrients_data.get('fiber_100g', 0), "g")
                                ]
                                
                                for name, value, unit in nutrients:
                                    st.markdown(f"""
                                        <div style='display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #dee2e6;'>
                                        <span><strong>{name}</strong></span>
                                        <span>{value:.1f} {unit}</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                # Add citations
                                st.markdown("""
                                    <div class='citation'>
                                    Sources: FDA Nutritional Guidelines, WHO Dietary Recommendations
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with col4:
                                # Create professional nutrient visualization
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
                                        textposition="auto",
                                        marker_color=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f']
                                    )
                                ])
                                
                                fig.update_layout(
                                    title={
                                        'text': "Macronutrient Distribution",
                                        'y':0.95,
                                        'x':0.5,
                                        'xanchor': 'center',
                                        'yanchor': 'top'
                                    },
                                    yaxis_title="Grams per 100g",
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font=dict(
                                        family="Arial, sans-serif",
                                        size=12
                                    )
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # If we have analysis information, show it professionally
                            if isinstance(result['nutritional_data'], dict) and "analysis" in result['nutritional_data']:
                                analysis = result['nutritional_data']["analysis"]
                                
                                if "nutrition_claims" in analysis and analysis["nutrition_claims"]:
                                    st.markdown("""
                                        <div class='section-header'>
                                        🏅 Nutrition Highlights
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    for claim in analysis["nutrition_claims"]:
                                        st.markdown(f"""
                                            <div class='insight-card' style='border-left-color: #2ecc71'>
                                            ✓ {claim}
                                            </div>
                                        """, unsafe_allow_html=True)
                                
                                if "health_insights" in analysis and analysis["health_insights"]:
                                    st.markdown("""
                                        <div class='section-header'>
                                        💡 Expert Recommendations
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Group insights by type (concerns vs suggestions)
                                    for insight in analysis["health_insights"][:3]:  # Limit to top 3 insights
                                        st.markdown(f"""
                                            <div class='insight-card'>
                                            <strong>{insight['nutrient']}</strong><br>
                                            {insight['suggestion']}
                                            </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # Add scientific citations
                                    st.markdown("""
                                        <div class='citation'>
                                        Analysis based on:
                                        <ul>
                                            <li>WHO Nutritional Guidelines (2024)</li>
                                            <li>FDA Recommended Daily Values</li>
                                            <li>European Food Safety Authority Standards</li>
                                        </ul>
                                        </div>
                                    """, unsafe_allow_html=True)
                    else:
                        st.error("Could not find product information.")
            else:
                st.error("No barcode detected in the image. Please try another image.")

if __name__ == "__main__":
    main()