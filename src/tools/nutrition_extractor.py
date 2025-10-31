"""
Enhanced nutritional data extraction and analysis tool based on international standards.
"""
from langchain_core.tools import tool
from typing import Dict, Any
from dataclasses import dataclass
from typing import Optional

@dataclass
class NutrientInfo:
    """Structured nutrient information with health guidelines."""
    name: str
    unit: str
    rdi: float  # Recommended Daily Intake
    description: str
    high_threshold: Optional[float] = None
    low_threshold: Optional[float] = None

# Based on FDA and WHO guidelines
NUTRIENT_STANDARDS = {
    "energy": NutrientInfo(
        "Energy", "kcal", 2000,
        "Total energy content",
        high_threshold=400,  # per 100g
        low_threshold=100
    ),
    "proteins": NutrientInfo(
        "Protein", "g", 50,
        "Essential for muscle maintenance and growth",
        low_threshold=10
    ),
    "carbohydrates": NutrientInfo(
        "Carbohydrates", "g", 300,
        "Primary energy source",
    ),
    "sugars": NutrientInfo(
        "Sugars", "g", 50,
        "Added and natural sugars",
        high_threshold=22.5,  # WHO guideline
        low_threshold=5
    ),
    "fat": NutrientInfo(
        "Total Fat", "g", 65,
        "Essential for nutrient absorption",
        high_threshold=17.5,
        low_threshold=3
    ),
    "saturated_fat": NutrientInfo(
        "Saturated Fat", "g", 20,
        "Linked to cardiovascular health",
        high_threshold=5,
        low_threshold=1.5
    ),
    "fiber": NutrientInfo(
        "Fiber", "g", 25,
        "Important for digestive health",
        low_threshold=3
    ),
    "sodium": NutrientInfo(
        "Sodium", "mg", 2300,
        "Essential mineral, but harmful in excess",
        high_threshold=600,
        low_threshold=120
    ),
    "potassium": NutrientInfo(
        "Potassium", "mg", 3500,
        "Essential for heart and muscle function",
        low_threshold=300
    ),
    "calcium": NutrientInfo(
        "Calcium", "mg", 1000,
        "Essential for bone health",
        low_threshold=120
    ),
    "iron": NutrientInfo(
        "Iron", "mg", 18,
        "Essential for blood health",
        low_threshold=1.8
    ),
    "vitamin_c": NutrientInfo(
        "Vitamin C", "mg", 60,
        "Antioxidant properties",
        low_threshold=6
    ),
    "vitamin_a": NutrientInfo(
        "Vitamin A", "µg", 900,
        "Important for vision and immunity",
        low_threshold=90
    ),
    "trans_fat": NutrientInfo(
        "Trans Fat", "g", 0,
        "Artificial fats to be avoided",
        high_threshold=0.5
    )
}

def evaluate_nutrient_level(value: float, info: NutrientInfo) -> str:
    """Evaluate the level of a nutrient based on standards."""
    if info.high_threshold and value >= info.high_threshold:
        return "high"
    if info.low_threshold and value <= info.low_threshold:
        return "low"
    return "moderate"

@tool
def extract_nutritional_data(product_info: dict) -> Dict[str, Any]:
    """
    Extract and analyze nutritional data using international health standards.
    
    Args:
        product_info: Raw product data from Open Food Facts
        
    Returns:
        Dictionary containing normalized nutritional data and analysis
    """
    nutriments = product_info.get("nutriments", {})
    
    # Basic nutrient extraction
    nutrients = {
        "energy_100g": nutriments.get("energy-kcal_100g", 0),
        "proteins_100g": nutriments.get("proteins_100g", 0),
        "carbohydrates_100g": nutriments.get("carbohydrates_100g", 0),
        "sugars_100g": nutriments.get("sugars_100g", 0),
        "fat_100g": nutriments.get("fat_100g", 0),
        "saturated_fat_100g": nutriments.get("saturated-fat_100g", 0),
        "trans_fat_100g": nutriments.get("trans-fat_100g", 0),
        "fiber_100g": nutriments.get("fiber_100g", 0),
        "sodium_100g": nutriments.get("sodium_100g", 0),
        "potassium_100g": nutriments.get("potassium_100g", 0),
        "calcium_100g": nutriments.get("calcium_100g", 0),
        "iron_100g": nutriments.get("iron_100g", 0),
        "vitamin_a_100g": nutriments.get("vitamin-a_100g", 0),
        "vitamin_c_100g": nutriments.get("vitamin-c_100g", 0),
    }
    
    # Convert sodium to mg if needed
    if nutrients["sodium_100g"] < 1:  # Likely in grams
        nutrients["sodium_100g"] *= 1000
    
    # Detailed analysis
    analysis = {
        "nutrient_levels": {},
        "health_insights": [],
        "rdi_percentages": {},
        "nutrition_claims": []
    }
    
    # Analyze each nutrient
    for key, value in nutrients.items():
        base_key = key.replace("_100g", "")
        if base_key in NUTRIENT_STANDARDS:
            info = NUTRIENT_STANDARDS[base_key]
            
            # Calculate %RDI
            if info.rdi > 0:  # Prevent division by zero
                rdi_percentage = (value / info.rdi) * 100
                analysis["rdi_percentages"][base_key] = round(rdi_percentage, 1)
            else:
                analysis["rdi_percentages"][base_key] = 0
            
            # Evaluate levels
            level = evaluate_nutrient_level(value, info)
            analysis["nutrient_levels"][base_key] = level
            
            # Generate insights
            if level == "high" and info.high_threshold:
                analysis["health_insights"].append({
                    "nutrient": info.name,
                    "concern": f"High in {info.name.lower()} - exceeds recommended levels",
                    "suggestion": f"Consider alternatives lower in {info.name.lower()}"
                })
            elif level == "low" and info.low_threshold:
                if base_key in ["sugars", "saturated_fat", "sodium"]:
                    analysis["nutrition_claims"].append(f"Low in {info.name}")
                else:
                    analysis["health_insights"].append({
                        "nutrient": info.name,
                        "concern": f"Low in {info.name.lower()} - below recommended levels",
                        "suggestion": f"Consider supplementing with {info.name.lower()}-rich foods"
                    })
    
    # Additional nutrition claims based on standards
    if nutrients["fiber_100g"] >= 6:
        analysis["nutrition_claims"].append("High Fiber")
    if nutrients["proteins_100g"] >= 12:
        analysis["nutrition_claims"].append("High Protein")
    if nutrients["fat_100g"] <= 3:
        analysis["nutrition_claims"].append("Low Fat")
    
    return {
        "nutrients": nutrients,
        "analysis": analysis
    }
