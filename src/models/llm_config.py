"""
LLM configuration and initialization.
"""
import os
from langchain_groq import ChatGroq


def get_groq_llm(temperature: float = 0.7, max_tokens: int = 1024) -> ChatGroq:
    """
    Get configured Groq LLM instance.
    
    Args:
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Configured ChatGroq instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key
    )
