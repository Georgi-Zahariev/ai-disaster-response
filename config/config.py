"""
File: config.py
Purpose: Load and validate application configuration from environment variables
Inputs: Environment variables from .env file
Outputs: Config object with validated settings
Dependencies: os, typing
Used By: All modules requiring configuration
"""

import os
from typing import Optional


class Config:
    """Application configuration loaded from environment variables."""
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///disaster.db")
    
    # Redis
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: int = int(os.getenv("PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    MAPS_API_KEY: Optional[str] = os.getenv("MAPS_API_KEY")
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            raise ValueError("At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required")
        
        if cls.DEBUG:
            print("⚠️  Running in DEBUG mode")


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("💡 Please set required environment variables in .env file")
