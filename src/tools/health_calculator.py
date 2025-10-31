"""
Health score calculation tool using international health standards.
"""
from langchain_core.tools import tool
from typing import Dict, Tuple

# WHO and FDA recommended daily values (per 100g)
NUTRITION_STANDARDS = {
    "sugars": {"high": 22.5, "low": 5.0},  # WHO guidelines
    "sodium": {"high": 600, "low": 120},    # WHO guidelines (mg)
    "saturated_fat": {"high": 5.0, "low": 1.5},  # WHO/FDA
    "fiber": {"target": 3.0},  # Based on 25g daily recommendation
    "proteins": {"target": 10.0},  # Based on 50g daily recommendation
    "trans_fat": {"limit": 0.5},  # FDA guidelines
    "calories": {"high": 400, "low": 100}  # Per 100g basis
}

def evaluate_nutrient(value: float, standard: Dict[str, float]) -> float:
    """Calculate score contribution for a nutrient based on health standards."""
    if "high" in standard and "low" in standard:
        if value >= standard["high"]:
            return -2.0
        elif value > standard["low"]:
            return -1.0
        return 0.0
    elif "target" in standard:
        if value >= standard["target"]:
            return 1.0
        return 0.0
    elif "limit" in standard and value > standard["limit"]:
        return -2.0
    return 0.0

@tool
def calculate_health_score(nutritional_data: dict) -> Tuple[int, Dict[str, str]]:
    """
    Calculate a health score (1-10) based on WHO and FDA nutritional guidelines.
    
    Args:
        nutritional_data: Dictionary containing nutrients per 100g
        
    Returns:
        Tuple of (health score from 1-10, detailed analysis)
    """
    base_score = 7.0  # Start from neutral-positive
    analysis = {}
    
    # Convert sodium from g to mg if needed
    sodium_mg = nutritional_data.get("sodium_100g", 0) * 1000
    
    # Core nutrient evaluation
    nutrients_eval = {
        "sugars": evaluate_nutrient(nutritional_data.get("sugars_100g", 0), 
                                  NUTRITION_STANDARDS["sugars"]),
        "sodium": evaluate_nutrient(sodium_mg, 
                                  NUTRITION_STANDARDS["sodium"]),
        "saturated_fat": evaluate_nutrient(nutritional_data.get("saturated_fat_100g", 0),
                                         NUTRITION_STANDARDS["saturated_fat"]),
        "fiber": evaluate_nutrient(nutritional_data.get("fiber_100g", 0),
                                 NUTRITION_STANDARDS["fiber"]),
        "proteins": evaluate_nutrient(nutritional_data.get("proteins_100g", 0),
                                    NUTRITION_STANDARDS["proteins"]),
    }
    
    # Calculate final score and generate analysis
    score = base_score
    
    # Sugars analysis
    if nutrients_eval["sugars"] < 0:
        analysis["sugars"] = "High sugar content - exceeds WHO recommendations"
        score += nutrients_eval["sugars"]
    else:
        analysis["sugars"] = "Acceptable sugar levels"
    
    # Sodium analysis
    if nutrients_eval["sodium"] < 0:
        analysis["sodium"] = "High sodium content - exceeds WHO guidelines"
        score += nutrients_eval["sodium"]
    else:
        analysis["sodium"] = "Acceptable sodium levels"
    
    # Saturated fat analysis
    if nutrients_eval["saturated_fat"] < 0:
        analysis["saturated_fat"] = "High saturated fat - exceeds WHO/FDA guidelines"
        score += nutrients_eval["saturated_fat"]
    else:
        analysis["saturated_fat"] = "Good saturated fat levels"
    
    # Fiber analysis
    if nutrients_eval["fiber"] > 0:
        analysis["fiber"] = "Good source of fiber"
        score += nutrients_eval["fiber"]
    else:
        analysis["fiber"] = "Could benefit from more fiber"
    
    # Protein analysis
    if nutrients_eval["proteins"] > 0:
        analysis["proteins"] = "Good protein content"
        score += nutrients_eval["proteins"]
    else:
        analysis["proteins"] = "Could benefit from more protein"
    
    # Energy density check
    calories = nutritional_data.get("energy_100g", 0)
    if calories > NUTRITION_STANDARDS["calories"]["high"]:
        analysis["calories"] = "High calorie density"
        score -= 1.0
    elif calories < NUTRITION_STANDARDS["calories"]["low"]:
        analysis["calories"] = "Low calorie density"
        score += 0.5
    else:
        analysis["calories"] = "Moderate calorie density"
    
    # Ensure score stays within bounds
    final_score = max(1, min(10, round(score)))
    
    return final_score, analysis
