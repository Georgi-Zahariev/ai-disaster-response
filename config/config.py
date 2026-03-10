"""
File: config.py
Purpose: Load and validate application configuration from environment variables
Inputs: Environment variables from .env file
Outputs: Config object with validated settings
Dependencies: os, typing
Used By: All modules requiring configuration

Configuration includes:
- LLM provider settings
- Feature flags for pipeline modules
- External API keys
- Application settings
- Security configuration
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """
    Application configuration loaded from environment variables.
    
    Provides safe defaults and validation for all configuration options.
    """
    
    # ========================================================================
    # LLM Provider Configuration
    # ========================================================================
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
    
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    ANTHROPIC_MAX_TOKENS: int = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000"))
    
    # Default LLM provider (openai or anthropic)
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    
    # ========================================================================
    # Feature Flags - Pipeline Modules
    # ========================================================================
    
    # Provider enable/disable flags
    ENABLE_TEXT_PROVIDER: bool = os.getenv("ENABLE_TEXT_PROVIDER", "true").lower() == "true"
    ENABLE_VISION_PROVIDER: bool = os.getenv("ENABLE_VISION_PROVIDER", "true").lower() == "true"
    ENABLE_QUANT_PROVIDER: bool = os.getenv("ENABLE_QUANT_PROVIDER", "true").lower() == "true"
    
    # Pipeline stage enable/disable flags
    ENABLE_EXTRACTION: bool = os.getenv("ENABLE_EXTRACTION", "true").lower() == "true"
    ENABLE_FUSION: bool = os.getenv("ENABLE_FUSION", "true").lower() == "true"
    ENABLE_SCORING: bool = os.getenv("ENABLE_SCORING", "true").lower() == "true"
    ENABLE_ALERTS: bool = os.getenv("ENABLE_ALERTS", "true").lower() == "true"
    ENABLE_VISUALIZATION: bool = os.getenv("ENABLE_VISUALIZATION", "true").lower() == "true"
    
    # Experimental features
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "false").lower() == "true"
    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///disaster.db")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # ========================================================================
    # Cache Configuration
    # ========================================================================
    
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # ========================================================================
    # Application Settings
    # ========================================================================
    
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL).split(",")
    
    # ========================================================================
    # External API Configuration
    # ========================================================================
    
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    WEATHER_API_URL: str = os.getenv("WEATHER_API_URL", "https://api.weather.gov")
    
    MAPS_API_KEY: Optional[str] = os.getenv("MAPS_API_KEY")
    MAPS_API_URL: str = os.getenv("MAPS_API_URL", "https://maps.googleapis.com/maps/api")
    
    EMERGENCY_API_KEY: Optional[str] = os.getenv("EMERGENCY_API_KEY")
    
    # ========================================================================
    # Security Configuration
    # ========================================================================
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "dev-session-secret")
    
    # API rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # ========================================================================
    # Processing Configuration
    # ========================================================================
    
    # Timeouts
    EXTRACTION_TIMEOUT_SECONDS: int = int(os.getenv("EXTRACTION_TIMEOUT_SECONDS", "30"))
    FUSION_TIMEOUT_SECONDS: int = int(os.getenv("FUSION_TIMEOUT_SECONDS", "15"))
    SCORING_TIMEOUT_SECONDS: int = int(os.getenv("SCORING_TIMEOUT_SECONDS", "10"))
    ALERT_TIMEOUT_SECONDS: int = int(os.getenv("ALERT_TIMEOUT_SECONDS", "5"))
    
    # Confidence thresholds
    MIN_CONFIDENCE_THRESHOLD: float = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.5"))
    HIGH_CONFIDENCE_THRESHOLD: float = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.8"))
    
    # Batch processing
    MAX_SIGNALS_PER_REQUEST: int = int(os.getenv("MAX_SIGNALS_PER_REQUEST", "100"))
    MAX_EVENTS_PER_BATCH: int = int(os.getenv("MAX_EVENTS_PER_BATCH", "50"))
    
    # ========================================================================
    # Methods
    # ========================================================================
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        errors = []
        
        # Check LLM configuration
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            errors.append("At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required")
        
        # Check default provider is valid
        if cls.DEFAULT_LLM_PROVIDER not in ["openai", "anthropic"]:
            errors.append(f"DEFAULT_LLM_PROVIDER must be 'openai' or 'anthropic', got: {cls.DEFAULT_LLM_PROVIDER}")
        
        # Check if default provider has API key
        if cls.DEFAULT_LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when DEFAULT_LLM_PROVIDER=openai")
        elif cls.DEFAULT_LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required when DEFAULT_LLM_PROVIDER=anthropic")
        
        # Check log level is valid
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of {valid_log_levels}, got: {cls.LOG_LEVEL}")
        
        # Check JWT secret in production
        if not cls.DEBUG and cls.JWT_SECRET == "dev-secret-change-in-production":
            errors.append("JWT_SECRET must be changed in production (DEBUG=false)")
        
        # Raise if any errors
        if errors:
            raise ValueError("\n".join(errors))
    
    @classmethod
    def print_summary(cls) -> None:
        """Print configuration summary for debugging."""
        print("\n" + "=" * 80)
        print("CONFIGURATION SUMMARY")
        print("=" * 80)
        
        print("\n🔧 Application Settings:")
        print(f"  DEBUG: {cls.DEBUG}")
        print(f"  LOG_LEVEL: {cls.LOG_LEVEL}")
        print(f"  LOG_FORMAT: {cls.LOG_FORMAT}")
        print(f"  PORT: {cls.PORT}")
        print(f"  HOST: {cls.HOST}")
        
        print("\n🤖 LLM Providers:")
        print(f"  DEFAULT_LLM_PROVIDER: {cls.DEFAULT_LLM_PROVIDER}")
        print(f"  OPENAI_API_KEY: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Not set'}")
        print(f"  OPENAI_MODEL: {cls.OPENAI_MODEL}")
        print(f"  ANTHROPIC_API_KEY: {'✓ Set' if cls.ANTHROPIC_API_KEY else '✗ Not set'}")
        print(f"  ANTHROPIC_MODEL: {cls.ANTHROPIC_MODEL}")
        
        print("\n🎚️  Feature Flags - Providers:")
        print(f"  ENABLE_TEXT_PROVIDER: {cls.ENABLE_TEXT_PROVIDER}")
        print(f"  ENABLE_VISION_PROVIDER: {cls.ENABLE_VISION_PROVIDER}")
        print(f"  ENABLE_QUANT_PROVIDER: {cls.ENABLE_QUANT_PROVIDER}")
        
        print("\n🎚️  Feature Flags - Pipeline Stages:")
        print(f"  ENABLE_EXTRACTION: {cls.ENABLE_EXTRACTION}")
        print(f"  ENABLE_FUSION: {cls.ENABLE_FUSION}")
        print(f"  ENABLE_SCORING: {cls.ENABLE_SCORING}")
        print(f"  ENABLE_ALERTS: {cls.ENABLE_ALERTS}")
        print(f"  ENABLE_VISUALIZATION: {cls.ENABLE_VISUALIZATION}")
        
        print("\n🧪 Experimental Features:")
        print(f"  ENABLE_CACHING: {cls.ENABLE_CACHING}")
        print(f"  ENABLE_RATE_LIMITING: {cls.ENABLE_RATE_LIMITING}")
        print(f"  ENABLE_METRICS: {cls.ENABLE_METRICS}")
        
        print("\n🗄️  Database:")
        print(f"  DATABASE_URL: {cls.DATABASE_URL[:30]}...")
        
        print("\n🔒 Security:")
        print(f"  JWT_SECRET: {'✓ Custom' if cls.JWT_SECRET != 'dev-secret-change-in-production' else '⚠️  Default (change in prod!)'}")
        
        print("\n" + "=" * 80 + "\n")
    
    @classmethod
    def is_provider_enabled(cls, provider_type: str) -> bool:
        """
        Check if a provider is enabled.
        
        Args:
            provider_type: Provider type (text, vision, quant)
            
        Returns:
            True if provider is enabled
        """
        provider_map = {
            "text": cls.ENABLE_TEXT_PROVIDER,
            "vision": cls.ENABLE_VISION_PROVIDER,
            "quant": cls.ENABLE_QUANT_PROVIDER,
        }
        return provider_map.get(provider_type.lower(), False)
    
    @classmethod
    def is_stage_enabled(cls, stage: str) -> bool:
        """
        Check if a pipeline stage is enabled.
        
        Args:
            stage: Stage name (extraction, fusion, scoring, alerts, visualization)
            
        Returns:
            True if stage is enabled
        """
        stage_map = {
            "extraction": cls.ENABLE_EXTRACTION,
            "fusion": cls.ENABLE_FUSION,
            "scoring": cls.ENABLE_SCORING,
            "alerts": cls.ENABLE_ALERTS,
            "visualization": cls.ENABLE_VISUALIZATION,
        }
        return stage_map.get(stage.lower(), False)


# ============================================================================
# Auto-validation on import
# ============================================================================

try:
    Config.validate()
    if Config.DEBUG:
        Config.print_summary()
except ValueError as e:
    print("\n" + "=" * 80)
    print("❌ CONFIGURATION ERROR")
    print("=" * 80)
    print(f"\n{e}\n")
    print("💡 Please check your .env file and environment variables")
    print("💡 See .env.example for required configuration\n")
    print("=" * 80 + "\n")
