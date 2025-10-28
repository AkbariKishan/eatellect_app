"""
Configuration settings for the application.
"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""
    
    # API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # LLM Parameters
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1024
    
    # Health Score Thresholds
    HIGH_SUGAR_THRESHOLD: float = 15.0
    MEDIUM_SUGAR_THRESHOLD: float = 10.0
    HIGH_SODIUM_THRESHOLD: float = 1.5
    MEDIUM_SODIUM_THRESHOLD: float = 1.0
    
    def validate(self):
        """Validate required settings."""
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")


settings = Settings()
