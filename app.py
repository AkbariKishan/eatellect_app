"""
Eatellect - AI-Powered Food Health Analysis App
"""
import os
import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from src.graph.workflow import HealthAnalysisWorkflow
from src.state.health_state import HealthAnalysisState
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

def main():
    # Header: prefer a provided logo.png in assets/, fall back to inline emoji header
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_bytes = f.read()
        logo_b64 = base64.b64encode(logo_bytes).decode()
        logo_src = f"data:image/png;base64,{logo_b64}"
        st.markdown(
            f'''
            <div class="app-header">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <img src="{logo_src}" style="height: 50px; width: 50px; object-fit: contain;" alt="Eatellect Logo">
                    <div>
                        <div style="font-size: 2rem; font-weight: bold; color: var(--text-color);">Eatellect</div>
                        <div style="font-size: 1.1rem; opacity: 0.8; color: var(--text-color);">Professional Food Health Analysis</div>
                    </div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
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

    workflow = HealthAnalysisWorkflow()

    st.markdown("""
        <div class='section-header'>
        📸 Product Scanner
        </div>
    """, unsafe_allow_html=True)

    scan_option = st.radio("Choose scanning method:", ["Upload Image", "Live Camera"], horizontal=True)

    image = None
    uploaded_file = None
    if scan_option == "Upload Image":
        uploaded_file = st.file_uploader("Upload a product barcode image", type=["jpg", "jpeg", "png"])
        if not uploaded_file:
            st.info("👋 Welcome! Upload a clear image of your product's barcode to get started.")
        else:
            try:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if image is None:
                    st.error("Failed to process the uploaded image. Please try another image.")
                    return
            except Exception as e:
                st.error(f"Error processing uploaded image: {e}")
                return
    else:
        st.info("📸 Point your camera at the product's barcode")
        camera_image = st.camera_input("Take a photo")
        if camera_image:
            try:
                file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if image is None:
                    st.error("Failed to process the camera image. Please try again.")
                    return
            except Exception as e:
                st.error(f"Error processing camera image: {e}")
                return

    if image is not None:
        # Display scanned image
        img_col1, _ = st.columns([1, 1])
        with img_col1:
            st.markdown("##### Scanned Barcode")
            try:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            except Exception:
                image_rgb = image
            st.image(image_rgb, caption="Scanned Barcode Image", use_container_width=True)

        # Decode barcode and analyze
        with st.spinner("Analyzing barcode..."):
            barcodes = decode(image)
            if not barcodes:
                st.error("No barcode detected in the image. Please try another image.")
                return

            barcode = barcodes[0].data.decode('utf-8')
            st.success(f"Barcode detected: {barcode}")

            try:
                state = HealthAnalysisState()
                state.barcode = barcode
                result = workflow.execute(state)
            except Exception as e:
                st.error(f"Error during product analysis: {e}")
                return

            if not result:
                st.error("Failed to analyze product. Please try again.")
                return

            product_info = result.get('product_info', {}) or {}

            col1, col2 = st.columns([1, 1])

            # Left column: product details and score
            with col1:
                st.markdown("""
                    <div class='section-header'>
                    🏷️ Product Details
                    </div>
                """, unsafe_allow_html=True)

                # Show product image if available
                product_image_url = product_info.get('image_url') or product_info.get('image_front_url') or product_info.get('image_small_url')
                if product_image_url:
                    try:
                        st.image(product_image_url, caption="Product Image", width=200)
                    except Exception:
                        st.warning("Could not load product image")

                st.markdown(f"""
                    <div class='metric-card'>
                    <h3>{product_info.get('product_name', 'N/A')}</h3>
                    <p><strong>Brand:</strong> {product_info.get('brands', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)

                # Health score visualization
                raw = result.get('health_rating')
                if raw is not None:
                    try:
                        raw_val = raw[0] if isinstance(raw, (list, tuple)) and raw else raw
                        score = float(raw_val)
                        score = min(max(score, 0), 10)

                        color = "#2ecc71" if score >= 7 else "#f1c40f" if score >= 4 else "#e74c3c"
                        st.markdown(f"""
                            <div class='health-score' style='color: {color}'>
                            {score:.1f}/10
                            <div style='font-size: 1rem; color: var(--text-color);'>Health Score</div>
                            </div>
                        """, unsafe_allow_html=True)

                        gauge = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=score,
                            gauge={'axis': {'range': [0, 10]},
                                   'bar': {'color': color}},
                            domain={'x': [0, 1], 'y': [0, 1]}
                        ))
                        gauge.update_layout(margin={'t': 0, 'b': 0, 'l': 0, 'r': 0}, height=220)
                        st.plotly_chart(gauge, use_container_width=True)

                        breakdown = result.get('score_breakdown') or result.get('health_breakdown')
                        if breakdown and isinstance(breakdown, dict):
                            labels = list(breakdown.keys())
                            values = [float(v) for v in breakdown.values()]
                            bar_fig = go.Figure(go.Bar(x=values, y=labels, orientation='h', marker_color='rgba(45,150,255,0.8)'))
                            bar_fig.update_layout(title='Health score breakdown', xaxis_title='Score', yaxis=dict(autorange='reversed'), height=260)
                            st.plotly_chart(bar_fig, use_container_width=True)

                    except Exception as e:
                        st.warning(f"Could not render health score: {e}")

                # Key findings: concise summary, recommendations, and replacement suggestions
                final_analysis = result.get('final_analysis')
                if final_analysis:
                    st.markdown("""
                        <div class='section-header'>
                        🔍 Key Findings — Summary & Recommendations
                        </div>
                    """, unsafe_allow_html=True)

                    
                    # Display raw LLM analysis
                    st.markdown("""
                        <div class='section-header'>
                        🤖 LLM Analysis Output
                        </div>
                    """, unsafe_allow_html=True)
                    if final_analysis:
                        st.text_area("Complete Analysis", final_analysis, height=200, disabled=True)
                    else:
                        st.info("No LLM analysis available for this product")

            # Right column: nutritional profile
            with col2:
                # Nutritional Profile (compact)
                st.markdown("""
                    <div class='section-header'>
                    📊 Nutritional Profile
                    </div>
                """, unsafe_allow_html=True)

                nutritional_data = result.get('nutritional_data') or {}
                if nutritional_data:
                    nutrients = {
                        'Energy (kcal)': nutritional_data.get('energy_100g', 0),
                        'Proteins (g)': nutritional_data.get('proteins_100g', 0),
                        'Carbs (g)': nutritional_data.get('carbohydrates_100g', 0),
                        'Sugars (g)': nutritional_data.get('sugars_100g', 0),
                        'Fat (g)': nutritional_data.get('fat_100g', 0),
                        'Fiber (g)': nutritional_data.get('fiber_100g', 0)
                    }

                    # Table
                    df = pd.DataFrame(list(nutrients.items()), columns=['Nutrient', 'Amount_per_100g'])
                    df = df.set_index('Nutrient')
                    st.dataframe(df.style.format('{:.2f}'))

                    # Pie chart for macros
                    macros = ['Proteins (g)', 'Carbs (g)', 'Fat (g)', 'Sugars (g)', 'Fiber (g)']
                    macro_vals = [nutrients.get(k, 0) for k in macros]
                    pie = go.Figure(go.Pie(labels=macros, values=macro_vals, hole=0.4))
                    pie.update_layout(title='Macronutrients (per 100g)')
                    st.plotly_chart(pie, use_container_width=True)

    else:
        st.info("No image provided yet. Use Upload Image or Live Camera to scan a product.")

    # End of main

if __name__ == "__main__":
    main()