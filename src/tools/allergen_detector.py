"""
Enhanced allergen and dietary restriction detection tool based on international standards.
"""
from langchain_core.tools import tool
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class AllergenInfo:
    """Structured allergen information."""
    name: str
    aliases: Set[str]
    description: str

# FDA major food allergens + EU additional allergens
ALLERGENS = {
    "milk": AllergenInfo(
        "Dairy",
        {"milk", "cream", "cheese", "butter", "whey", "casein", "lactose", "dairy"},
        "Milk and dairy products - major allergen"
    ),
    "eggs": AllergenInfo(
        "Eggs",
        {"egg", "albumin", "lysozyme", "globulin", "livetin", "ovomucin"},
        "Eggs and egg products - major allergen"
    ),
    "fish": AllergenInfo(
        "Fish",
        {"fish", "cod", "salmon", "tuna", "hake", "sardine", "anchovy"},
        "Fish and fish products - major allergen"
    ),
    "shellfish": AllergenInfo(
        "Shellfish",
        {"shellfish", "shrimp", "crab", "lobster", "prawn", "crayfish"},
        "Crustacean shellfish - major allergen"
    ),
    "tree_nuts": AllergenInfo(
        "Tree Nuts",
        {"almond", "hazelnut", "walnut", "cashew", "pecan", "pistachio", "macadamia"},
        "Tree nuts - major allergen"
    ),
    "peanuts": AllergenInfo(
        "Peanuts",
        {"peanut", "arachis", "groundnut"},
        "Peanuts and peanut products - major allergen"
    ),
    "wheat": AllergenInfo(
        "Wheat",
        {"wheat", "flour", "spelt", "semolina", "durum", "kamut"},
        "Wheat and wheat products - major allergen"
    ),
    "soybeans": AllergenInfo(
        "Soy",
        {"soy", "soya", "tofu", "edamame", "tempeh", "miso"},
        "Soybeans and soy products - major allergen"
    ),
    "sesame": AllergenInfo(
        "Sesame",
        {"sesame", "tahini", "gingelly", "benne"},
        "Sesame seeds and sesame products - major allergen"
    ),
    "celery": AllergenInfo(
        "Celery",
        {"celery", "celeriac"},
        "Celery and celery products (EU allergen)"
    ),
    "mustard": AllergenInfo(
        "Mustard",
        {"mustard", "mustard seed", "mustard powder"},
        "Mustard and mustard products (EU allergen)"
    ),
    "sulfites": AllergenInfo(
        "Sulfites",
        {"sulphite", "sulfite", "e220", "e228", "preservative"},
        "Sulfites above 10mg/kg (EU allergen)"
    ),
    "lupin": AllergenInfo(
        "Lupin",
        {"lupin", "lupine", "lupini"},
        "Lupin and lupin products (EU allergen)"
    ),
    "molluscs": AllergenInfo(
        "Molluscs",
        {"mollusc", "oyster", "mussel", "clam", "scallop", "squid", "octopus"},
        "Molluscs and mollusc products (EU allergen)"
    )
}

DIETARY_RESTRICTIONS = {
    "vegan": {
        "excluded": {"meat", "fish", "egg", "dairy", "honey", "gelatin", "shellac", "carmine"},
        "tags": {"en:non-vegan", "en:non-vegan-verified"}
    },
    "vegetarian": {
        "excluded": {"meat", "fish", "gelatin", "rennet"},
        "tags": {"en:non-vegetarian", "en:non-vegetarian-verified"}
    },
    "halal": {
        "excluded": {"pork", "alcohol", "lard"},
        "tags": {"en:non-halal"}
    },
    "kosher": {
        "excluded": {"pork", "shellfish"},
        "tags": {"en:non-kosher"}
    }
}

@tool
def identify_allergens(product_info: dict) -> Dict[str, List[Dict[str, str]]]:
    """
    Enhanced allergen and dietary restriction detection using FDA and EU standards.
    
    Args:
        product_info: Product information dictionary
        
    Returns:
        Dictionary with allergens and dietary information
    """
    results = {
        "allergens": [],
        "dietary_restrictions": [],
        "warnings": []
    }
    
    ingredients_text = str(product_info.get("ingredients_text", "")).lower()
    allergens_tags = set(product_info.get("allergens_tags", []))
    ingredients_analysis = product_info.get("ingredients_analysis_tags", [])
    
    # Process official allergen tags
    for tag in allergens_tags:
        clean_tag = tag.replace("en:", "").replace("-", " ").title()
        for allergen_key, info in ALLERGENS.items():
            if any(term in clean_tag.lower() for term in info.aliases):
                results["allergens"].append({
                    "type": info.name,
                    "source": "Official product labeling",
                    "description": info.description
                })
    
    # Deep ingredients text analysis
    for allergen_key, info in ALLERGENS.items():
        if any(term in ingredients_text for term in info.aliases):
            allergen_entry = {
                "type": info.name,
                "source": "Ingredients analysis",
                "description": info.description
            }
            if allergen_entry not in results["allergens"]:
                results["allergens"].append(allergen_entry)
    
    # Dietary restrictions analysis
    for diet_type, restrictions in DIETARY_RESTRICTIONS.items():
        # Check ingredients
        if any(excluded in ingredients_text for excluded in restrictions["excluded"]):
            results["dietary_restrictions"].append({
                "type": f"Not {diet_type}",
                "reason": f"Contains ingredients not suitable for {diet_type} diet"
            })
        
        # Check official tags
        if isinstance(ingredients_analysis, list):
            if any(tag in ingredients_analysis for tag in restrictions["tags"]):
                results["dietary_restrictions"].append({
                    "type": f"Not {diet_type}",
                    "reason": f"Product labeled as not suitable for {diet_type} diet"
                })
    
    # Cross-contamination warnings
    traces = product_info.get("traces_tags", [])
    if traces:
        for trace in traces:
            clean_trace = trace.replace("en:", "").replace("-", " ").title()
            results["warnings"].append({
                "type": "Cross-contamination risk",
                "allergen": clean_trace,
                "description": f"May contain traces of {clean_trace}"
            })
    
    return results
