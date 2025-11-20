"""
Agent nodes for the health analysis workflow.
"""
import asyncio
from langchain_core.messages import SystemMessage
from src.state.health_state import HealthAnalysisState
from src.tools.product_fetcher import ProductFetcher
from src.agents.parallel import parallel_data_extraction, parallel_llm_analysis
from src.models.llm_config import get_groq_llm


def barcode_extraction_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """Extract barcode and fetch product information."""
    print("\n=== Starting Barcode Extraction Node ===")
    print(f"Input State Barcode: {state.barcode}")
    
    if not state.barcode:
        print("No barcode provided in state")
        state.needs_external_data = True
        state.product_data = {}
        state.product_info = {}
        state.messages.append(SystemMessage(content="No barcode provided"))
        return state
    
    # Fetch product info from Open Food Facts
    fetcher = ProductFetcher()
    result = fetcher.fetch_product_by_barcode(state.barcode)
    
    if not result.success:
        print(f"\n=== Product Fetch Failed ===\n{result.error}")
        state.product_data = {}
        state.product_info = {}
        state.needs_external_data = True
        state.messages.append(SystemMessage(content=f"Error fetching product: {result.error}"))
        return state
    
    print("\n=== Setting Product Info in State ===")
    state.product_data = result.data
    state.product_info = {
        'product_name': result.data.get('product_name', 'N/A'),
        'brands': result.data.get('brands', 'N/A'),
        'nutriments': result.data.get('nutriments', {}),
        'ingredients_text': result.data.get('ingredients_text', '')
    }
    
    state.needs_external_data = False
    print(f"Product Data Keys: {list(state.product_data.keys())}")
    print(f"Product Info Keys: {list(state.product_info.keys())}")
    
    msg = f"Product fetched successfully: {state.product_info['product_name']}"
    state.messages.append(SystemMessage(content=msg))
    
    return state


def classifier_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """Classify the type of analysis needed."""
    print("\n=== Starting Classifier Node ===")
    product_info = state.product_data
    
    if not isinstance(product_info, dict):
        state.analysis_type = "basic"
        state.needs_external_data = True
        state.messages.append(SystemMessage(content="Invalid product info format"))
        return state
    
    # Check data completeness
    has_nutritional_data = bool(product_info.get("nutriments"))
    has_ingredients = bool(product_info.get("ingredients_text"))
    
    if has_nutritional_data and has_ingredients:
        state.analysis_type = "detailed"
        state.needs_external_data = False
    elif has_nutritional_data or has_ingredients:
        state.analysis_type = "basic"
        state.needs_external_data = False
    else:
        state.analysis_type = "basic"
        state.needs_external_data = True
    
    print(f"Analysis Type: {state.analysis_type}")
    print(f"Needs External Data: {state.needs_external_data}")
    
    state.messages.append(SystemMessage(content=f"Analysis type determined: {state.analysis_type}"))
    return state


def data_extraction_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """Extract product data and nutrition info using parallel processing."""
    try:
        # Pass state to parallel extraction
        state = asyncio.run(parallel_data_extraction(state))
    except Exception as e:
        print(f"Error in parallel data extraction: {str(e)}")
        state.errors.append(f"Parallel data extraction failed: {str(e)}")
    
    return state


def llm_analysis_node(state: HealthAnalysisState) -> HealthAnalysisState:
    """Generate health analysis and recommendations using parallel LLM execution."""
    print("\n=== Starting LLM Analysis Node ===")
    print(f"Product Data: {state.product_data}")
    print(f"Product Info: {state.product_info}")
    print(f"Nutritional Data: {state.nutritional_data}")
    print(f"Concerns: {state.concerns}")
    
    try:
        # Validate state and preserve data
        product_data = state.product_data
        product_info = state.product_info
        nutritional_data = state.nutritional_data
        
        # Validate required data
        if not product_info or not product_data:
            print("Error: Missing product information")
            state.final_analysis = "Missing product information"
            return state
            
        if not nutritional_data:
            print("Error: Missing nutritional data")
            state.final_analysis = "Missing nutritional data"
            return state
        
        # Get LLM
        llm = get_groq_llm(temperature=0.7, max_tokens=1024)
        
        # Add context to state for the LLM to see (if we were passing the whole state, but here we might need to update the parallel function too)
        # For now, let's just print them to confirm availability, and we'll need to ensure parallel_llm_analysis uses them
        print(f"User Context: {state.user_context}")
        print(f"Alternatives Found: {len(state.alternatives)}")
        
        # Use parallel execution for LLM tasks
        analysis_result = asyncio.run(parallel_llm_analysis(state, llm))
        
        # Update state with analysis results while preserving original data
        state.product_data = product_data
        state.product_info = product_info
        state.nutritional_data = nutritional_data
        state.final_analysis = analysis_result.get('final_analysis', '')
        state.recommendations = analysis_result.get('recommendations', [])
        state.messages.append(SystemMessage(content="Analysis completed"))
        
        print("\n=== LLM Analysis Complete ===")
        print(f"Final Analysis: {state.final_analysis}")
        print(f"Recommendations: {state.recommendations}")
        print(f"Preserved Product Data: {state.product_data}")
        print(f"Preserved Product Info: {state.product_info}")
        
        return state
        
    except Exception as e:
        print(f"Error in parallel LLM analysis: {e}")
        state.final_analysis = f"Error during analysis: {str(e)}"
        state.messages.append(SystemMessage(content=f"Analysis failed: {str(e)}"))
        return state