"""
Nutritional data extraction tool.
"""
from langchain_core.tools import tool


@tool
def extract_nutritional_data(product_info: dict) -> dict:
    """
    Extract and normalize nutritional data from product information.
    
    Args:
        product_info: Raw product data from Open Food Facts
        
    Returns:
        Normalized nutritional data dictionary
    """
    nutriments = product_info.get("nutriments", {})
    return {
        "energy_100g": nutriments.get("energy-kcal_100g", 0),
        "proteins_100g": nutriments.get("proteins_100g", 0),
        "carbohydrates_100g": nutriments.get("carbohydrates_100g", 0),
        "sugars_100g": nutriments.get("sugars_100g", 0),
        "fat_100g": nutriments.get("fat_100g", 0),
        "saturated_fat_100g": nutriments.get("saturated-fat_100g", 0),
        "fiber_100g": nutriments.get("fiber_100g", 0),
        "sodium_100g": nutriments.get("sodium_100g", 0),
        "salt_100g": nutriments.get("salt_100g", 0),
    }
