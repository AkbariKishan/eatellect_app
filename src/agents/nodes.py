"""
Agent nodes for the health analysis workflow.
"""
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.state.health_state import HealthAnalysisState
from src.tools import calculate_health_score, extract_nutritional_data, identify_allergens
from src.models.llm_config import get_groq_llm

from src.tools.barcode_scanner import BarcodeScanner
from src.tools.product_fetcher import ProductFetcher


def classifier_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """
    Classify the type of analysis needed based on product data completeness.
    """
    product_info = state.get("product_info", {})
    
    # Validate product_info is a dictionary
    if not isinstance(product_info, dict):
        return {
            "analysis_type": "basic",
            "needs_external_data": True,
            "messages": [SystemMessage(content="Invalid product info format")]
        }
    
    # Check if we have sufficient data
    has_nutritional_data = bool(product_info.get("nutriments"))
    has_ingredients = bool(product_info.get("ingredients_text"))
    
    if has_nutritional_data and has_ingredients:
        analysis_type = "detailed"
        needs_external = False
    elif has_nutritional_data or has_ingredients:
        analysis_type = "basic"
        needs_external = False
    else:
        analysis_type = "basic"
        needs_external = True
        
    return {
        "analysis_type": analysis_type,
        "needs_external_data": needs_external,
        "messages": [SystemMessage(content=f"Analysis type determined: {analysis_type}")]
    }



def data_extraction_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """
    Extract and process nutritional data using tools.
    """
    product_info = state.get("product_info", {})
    
    # Validate product_info
    if not product_info or not isinstance(product_info, dict):
        return {
            "nutritional_data": {},
            "concerns": ["No valid product information available"],
            "health_rating": 0,
            "messages": [SystemMessage(content="No valid product info available")]
        }
    
    try:
        # Use tools to extract data
        nutritional_data = extract_nutritional_data.invoke({"product_info": product_info})
        concerns = identify_allergens.invoke({"product_info": product_info})
        health_rating = calculate_health_score.invoke({"nutritional_data": nutritional_data})
        
        return {
            "nutritional_data": nutritional_data,
            "concerns": concerns,
            "health_rating": health_rating,
            "messages": [SystemMessage(content="Data extraction completed")]
        }
    except Exception as e:
        # Handle any extraction errors gracefully
        return {
            "nutritional_data": {},
            "concerns": [f"Error during data extraction: {str(e)}"],
            "health_rating": 0,
            "messages": [SystemMessage(content=f"Data extraction failed: {str(e)}")]
        }




def llm_analysis_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """
    Use LLM to generate detailed health analysis and recommendations.
    """
    llm = get_groq_llm(temperature=0.7, max_tokens=1024)
    
    # Safely get state values with defaults
    health_rating = state.get('health_rating', 0)
    nutritional_data = state.get('nutritional_data', {})
    concerns = state.get('concerns', [])
    analysis_type = state.get('analysis_type', 'basic')
    product_info = state.get('product_info', {})
    
    # Build context for LLM
    context = f"""
    Product Analysis Request:
    
    Health Rating: {health_rating}/10
    Nutritional Data: {nutritional_data}
    Identified Concerns: {concerns}
    Analysis Type: {analysis_type}
    
    Product Information:
    {product_info}
    """
    
    prompt = f"""You are a nutritionist AI assistant. Based on the product data provided, generate:

1. NUTRITIONAL BENEFITS: Key health benefits of this product
2. HEALTH CONCERNS: Specific concerns about nutrients, additives, or ingredients
3. RECOMMENDATIONS: Consumption guidance and healthier alternatives if needed

{context}

Provide a comprehensive but concise analysis."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "final_analysis": response.content,
        "messages": [AIMessage(content="LLM analysis completed")]
    }



def recommendation_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """
    Generate final structured recommendations using LLM reasoning.
    """
    llm = get_groq_llm(temperature=0.5, max_tokens=512)
    
    # Safely get state values
    health_rating = state.get('health_rating', 0)
    concerns = state.get('concerns', [])
    
    prompt = f"""Based on the health rating of {health_rating}/10 and concerns: {concerns},
    provide 3-5 specific, actionable recommendations for consuming this product.
    
    Format as a bullet list."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    recommendations = response.content.strip().split("\n")
    
    # Clean up recommendations
    cleaned_recs = [r.strip("- •*").strip() for r in recommendations if r.strip() and r.strip("- •*").strip()]
    
    return {
        "recommendations": cleaned_recs,
        "messages": [AIMessage(content="Recommendations generated")]
    }


def barcode_extraction_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """
    Extract barcode from image and fetch product information.
    """
    
    image_path = state.get("image_path")
    
    if not image_path:
        return {
            "needs_external_data": True,
            "product_info": {},
            "barcode": "",
            "messages": [SystemMessage(content="No image path provided")]
        }
    
    # Scan barcode from image
    scanner = BarcodeScanner()
    try:
        barcode = scanner.scan_barcode_from_image(image_path)
    except Exception as e:
        return {
            "needs_external_data": True,
            "product_info": {},
            "barcode": "",
            "messages": [SystemMessage(content=f"Error scanning barcode: {str(e)}")]
        }
    
    if not barcode:
        return {
            "needs_external_data": True,
            "product_info": {},
            "barcode": "",
            "messages": [SystemMessage(content="No barcode detected in image")]
        }
    
    # Fetch product info from Open Food Facts
    fetcher = ProductFetcher()
    try:
        product_info = fetcher.fetch_product_by_barcode(barcode)
    except Exception as e:
        return {
            "barcode": barcode,
            "product_info": {},
            "needs_external_data": True,
            "messages": [SystemMessage(content=f"Error fetching product: {str(e)}")]
        }
    
    if not product_info:
        return {
            "barcode": barcode,
            "product_info": {},
            "needs_external_data": True,
            "messages": [SystemMessage(content=f"Product not found for barcode {barcode}")]
        }
    
    return {
        "barcode": barcode,
        "product_info": product_info,
        "needs_external_data": False,
        "messages": [SystemMessage(content=f"Product fetched successfully: {product_info.get('product_name', 'Unknown')}")]
    }


