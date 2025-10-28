"""
Allergen and dietary restriction detection tool.
"""
from langchain_core.tools import tool


@tool
def identify_allergens(product_info: dict) -> list[str]:
    """
    Identify allergens and dietary restrictions from product data.
    
    Args:
        product_info: Product information dictionary
        
    Returns:
        List of allergens and dietary concerns
    """
    concerns = []
    
    # Safely handle allergens_tags (can be list or missing)
    allergens = product_info.get("allergens_tags", [])
    if allergens and isinstance(allergens, list):
        concerns.extend([a.replace("en:", "").replace("-", " ").title() for a in allergens])
    
    # Check for dietary labels - ingredients_analysis_tags is typically a LIST, not a dict
    ingredients_analysis = product_info.get("ingredients_analysis_tags", [])
    
    # Handle if it's a list (most common from Open Food Facts)
    if isinstance(ingredients_analysis, list):
        # Check for vegan/vegetarian tags in the list
        if "en:non-vegan" in ingredients_analysis or "en:non-vegan" in str(ingredients_analysis):
            concerns.append("Not vegan")
        if "en:non-vegetarian" in ingredients_analysis or "en:non-vegetarian" in str(ingredients_analysis):
            concerns.append("Not vegetarian")
    
    # Handle if it's a dict (less common, but possible)
    elif isinstance(ingredients_analysis, dict):
        if not ingredients_analysis.get("en:vegan"):
            concerns.append("Not vegan")
        if not ingredients_analysis.get("en:vegetarian"):
            concerns.append("Not vegetarian")
    
    # Check ingredients text for common allergens
    ingredients_text = str(product_info.get("ingredients_text", "")).lower()
    
    if "gluten" in ingredients_text or "wheat" in ingredients_text:
        concerns.append("Contains gluten")
    if "milk" in ingredients_text or "dairy" in ingredients_text:
        concerns.append("Contains dairy")
    if "soy" in ingredients_text or "soya" in ingredients_text:
        concerns.append("Contains soy")
    if "egg" in ingredients_text:
        concerns.append("Contains eggs")
    if any(nut in ingredients_text for nut in ["peanut", "almond", "cashew", "walnut", "hazelnut"]):
        concerns.append("Contains nuts")
    
    # Remove duplicates and return
    return list(set(concerns))
