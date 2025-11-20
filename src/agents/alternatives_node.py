"""
Node for finding healthier product alternatives.
"""
from langchain_core.messages import SystemMessage
from src.state.health_state import HealthAnalysisState
from src.tools.product_fetcher import ProductFetcher

def alternatives_search_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """
    Check if alternatives are needed and search for them.
    """
    print("\n=== Starting Alternatives Search Node ===")
    
    product_data = state.product_data
    if not product_data:
        print("No product data available for alternatives search")
        return state
        
    # Determine if we need alternatives
    # Logic: If Nutri-Score is D or E, or if NOVA group is 4
    nutri_score = product_data.get('nutrition_grades', '').lower()
    nova_group = product_data.get('nova_group')
    
    needs_alternatives = False
    if nutri_score in ['d', 'e']:
        needs_alternatives = True
    elif nova_group == 4:
        needs_alternatives = True
        
    print(f"Nutri-Score: {nutri_score}, NOVA: {nova_group}")
    print(f"Needs Alternatives: {needs_alternatives}")
    
    if not needs_alternatives:
        return state
        
    # Prepare search criteria
    categories = product_data.get('categories', [])
    # Use the last category as it's usually the most specific
    category = categories[-1] if categories else ""
    
    # If we have a specific category, search for better grades
    if category:
        print(f"Searching for better alternatives in category: {category}")
        fetcher = ProductFetcher()
        # Search for A, B, or C grade products in the same category
        alternatives = fetcher.search_products(
            category=category,
            nutrition_grades="a,b,c"
        )
        
        if alternatives:
            state.alternatives = alternatives
            state.messages.append(SystemMessage(content=f"Found {len(alternatives)} healthier alternatives"))
        else:
            print("No alternatives found with category tag. Trying text search...")
            # Fallback: Search using category name as text
            clean_category = category.split(':')[-1].replace('-', ' ')
            print(f"Fallback search query: {clean_category}")
            
            alternatives = fetcher.search_products(
                query=clean_category,
                nutrition_grades="a,b,c"
            )
            
            if alternatives:
                state.alternatives = alternatives
                state.messages.append(SystemMessage(content=f"Found {len(alternatives)} healthier alternatives (fallback)"))
            else:
                print("No alternatives found with fallback search")
            
    return state
