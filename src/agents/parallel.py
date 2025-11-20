"""
Parallel execution helpers for workflow nodes.
"""
from typing import List, Dict, Any
import asyncio
from src.state.health_state import HealthAnalysisState
from src.tools import (
        extract_nutritional_data,
        identify_allergens,
        calculate_health_score
    )

from langchain_core.messages import HumanMessage

async def parallel_data_extraction(state: HealthAnalysisState) -> HealthAnalysisState:
    """
    Run data extraction tasks in parallel and update state.
    """
    # Save original data
    product_data = state.product_data
    product_info = state.product_info
    
    # Define coroutines for parallel execution
    async def get_nutrition():
        return await asyncio.to_thread(
            extract_nutritional_data.invoke,
            {"product_info": product_info}
        )
        
    async def get_allergens():
        return await asyncio.to_thread(
            identify_allergens.invoke,
            {"product_info": product_info}
        )
    
    try:
        print("\n=== Starting Parallel Data Extraction ===")
        print(f"Input product_info: {product_info}")
        
        # Run extractions in parallel
        nutrition_task = asyncio.create_task(get_nutrition())
        allergens_task = asyncio.create_task(get_allergens())
        
        # Wait for both tasks
        nutrition_result = await nutrition_task
        allergens_result = await allergens_task
        
        print(f"\nNutrition Result: {nutrition_result}")
        print(f"Allergens Result: {allergens_result}")
        
        # Update state while preserving original data
        state.product_data = product_data
        state.product_info = product_info
        state.nutritional_data = nutrition_result.get("nutrients", {}) if isinstance(nutrition_result, dict) else {}
        state.concerns = allergens_result if allergens_result else []
        
        # Calculate health score after getting nutritional data
        state.health_rating = calculate_health_score.invoke({"nutritional_data": state.nutritional_data})
        
    except Exception as e:
        print(f"Error in parallel extraction: {str(e)}")
        # Restore original data on error
        state.product_data = product_data
        state.product_info = product_info
        
    return state

async def parallel_llm_analysis(state: HealthAnalysisState, llm) -> Dict[str, Any]:
    """
    Run LLM analysis tasks in parallel and return analysis results.
    
    Returns a dictionary with analysis results instead of modifying state directly.
    """
    
    # Define analysis prompts
    analysis_prompt = f"""You are a nutritionist AI assistant. Based on the data:
    Health Rating: {state.health_rating}/10
    Nutritional Data: {state.nutritional_data}
    Concerns: {state.concerns}
    Product Info: {state.product_info}
    User Context: {state.user_context}
    Alternatives Found: {state.alternatives}
    
    Generate a detailed but concise health analysis including benefits, concerns, and implications.
    If alternatives are provided, compare the current product with the best alternative and explain why it is better."""
    
    recommendations_prompt = f"""Based on:
    Health Rating: {state.health_rating}/10
    Concerns: {state.concerns}
    Alternatives: {state.alternatives}
    User Context: {state.user_context}
    
    Provide 3-5 specific, actionable recommendations for consuming this product.
    If alternatives are available, strongly suggest switching to them.
    Format as bullet points."""
    
    # Run LLM tasks in parallel
    async def get_analysis():
        response = await asyncio.to_thread(
            llm.invoke,
            [HumanMessage(content=analysis_prompt)]
        )
        return response.content
    
    async def get_recommendations():
        response = await asyncio.to_thread(
            llm.invoke,
            [HumanMessage(content=recommendations_prompt)]
        )
        return response.content
    
    try:
        # Execute in parallel
        analysis_task = asyncio.create_task(get_analysis())
        recommendations_task = asyncio.create_task(get_recommendations())
        
        analysis = await analysis_task
        recommendations = await recommendations_task
        
        # Process recommendations into list
        recommendations_list = [
            r.strip("- •*").strip()
            for r in recommendations.split("\n")
            if r.strip() and r.strip("- •*").strip()
        ]
        
        # Return results as dictionary
        return {
            "product_data": state.product_data,
            "product_info": state.product_info,
            "nutritional_data": state.nutritional_data,
            "health_rating": state.health_rating,
            "concerns": state.concerns,
            "final_analysis": analysis,
            "recommendations": recommendations_list
        }
        
    except Exception as e:
        print(f"Error in parallel LLM analysis: {str(e)}")
        return {
            "product_data": state.product_data,
            "product_info": state.product_info,
            "nutritional_data": state.nutritional_data,
            "health_rating": state.health_rating,
            "concerns": state.concerns,
            "final_analysis": f"Error in analysis: {str(e)}",
            "recommendations": []
        }
    
    return state