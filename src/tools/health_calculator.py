"""
Health score calculation tool.
"""
from langchain_core.tools import tool


@tool
def calculate_health_score(nutritional_data: dict) -> int:
    """
    Calculate a health score (1-10) based on nutritional data.
    
    Args:
        nutritional_data: Dictionary containing nutrients per 100g
        
    Returns:
        Health score from 1-10
    """
    score = 10
    
    # Penalize high sugar
    if nutritional_data.get("sugars_100g", 0) > 15:
        score -= 2
    elif nutritional_data.get("sugars_100g", 0) > 10:
        score -= 1
        
    # Penalize high sodium
    if nutritional_data.get("sodium_100g", 0) > 1.5:
        score -= 2
    elif nutritional_data.get("sodium_100g", 0) > 1.0:
        score -= 1
        
    # Penalize high saturated fat
    if nutritional_data.get("saturated_fat_100g", 0) > 10:
        score -= 2
    elif nutritional_data.get("saturated_fat_100g", 0) > 5:
        score -= 1
        
    # Reward high protein
    if nutritional_data.get("proteins_100g", 0) > 15:
        score += 1
        
    # Reward high fiber
    if nutritional_data.get("fiber_100g", 0) > 5:
        score += 1
        
    return max(1, min(10, score))
