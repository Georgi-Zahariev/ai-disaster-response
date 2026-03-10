"""
Example usage of configuration management and structured logging.

This file demonstrates how to use the new configuration and logging features
in the AI Disaster Response system.
"""

# ============================================================================
# Example 1: Using Feature Flags
# ============================================================================

from config.config import Config

def process_signals_with_flags(signals):
    """Example: Check feature flags before processing signals."""
    results = []
    
    # Check if text provider is enabled
    if Config.is_provider_enabled("text"):
        print("✓ Text provider enabled - processing text signals")
        # results.extend(process_text_signals(signals.text))
    else:
        print("✗ Text provider disabled - skipping text signals")
    
    # Check if vision provider is enabled
    if Config.is_provider_enabled("vision"):
        print("✓ Vision provider enabled - processing vision signals")
        # results.extend(process_vision_signals(signals.vision))
    else:
        print("✗ Vision provider disabled - skipping vision signals")
    
    return results


def process_pipeline_with_flags(request):
    """Example: Check stage flags before each pipeline phase."""
    result = {"observations": [], "events": [], "alerts": []}
    
    # Phase 1: Extraction
    if Config.is_stage_enabled("extraction"):
        print("✓ Extraction stage enabled")
        # result["observations"] = extract_observations(request)
    else:
        print("✗ Extraction stage disabled - skipping")
    
    # Phase 2: Fusion
    if Config.is_stage_enabled("fusion"):
        print("✓ Fusion stage enabled")
        # result["events"] = fuse_events(result["observations"])
    else:
        print("✗ Fusion stage disabled - skipping")
    
    # Phase 3: Scoring
    if Config.is_stage_enabled("scoring"):
        print("✓ Scoring stage enabled")
        # result["disruptions"] = score_disruptions(result["events"])
    else:
        print("✗ Scoring stage disabled - skipping")
    
    return result


# ============================================================================
# Example 2: Using TraceLogger
# ============================================================================

from backend.logging import TraceLogger

def process_request_with_trace_logger(request):
    """Example: Use TraceLogger for automatic trace context."""
    # Extract trace from request
    trace = request.get("trace", {"requestId": "unknown"})
    
    # Create trace logger
    logger = TraceLogger(__name__, trace)
    
    # All log messages will include trace context
    logger.info("Starting request processing")
    
    try:
        # Process request
        logger.debug("Validating request structure")
        # ... validation code ...
        
        logger.info("Request validated successfully")
        
        logger.debug("Calling orchestrator")
        # result = orchestrator.process(request)
        
        logger.info("Request processed successfully", 
                   events_count=5, 
                   alerts_count=2)
        
        return {"status": "success"}
        
    except ValueError as e:
        logger.warning("Request validation failed", 
                      error=str(e), 
                      error_type="validation")
        raise
        
    except Exception as e:
        logger.error("Request processing failed", 
                    error=str(e), 
                    error_type="processing")
        logger.exception("Full exception details")
        raise


# ============================================================================
# Example 3: Using Context Variable (for async)
# ============================================================================

from backend.logging import set_trace_context, get_logger, clear_trace_context

logger = get_logger(__name__)

async def process_request_with_context_var(request):
    """Example: Use context variable for automatic trace propagation."""
    # Set trace context at request entry
    trace = request.get("trace", {"requestId": "unknown"})
    set_trace_context(trace)
    
    try:
        # All logs will automatically include trace context
        logger.info("Starting async request processing")
        
        # Call other functions - they inherit trace context
        await extract_data()
        await process_data()
        await save_results()
        
        logger.info("Async request completed successfully")
        
        return {"status": "success"}
        
    finally:
        # Clean up trace context
        clear_trace_context()


async def extract_data():
    """Called function - inherits trace context."""
    # No need to pass trace explicitly!
    logger.debug("Extracting data from signals")
    # ... extraction code ...
    logger.debug("Extracted 10 observations")


async def process_data():
    """Called function - inherits trace context."""
    # No need to pass trace explicitly!
    logger.debug("Processing extracted data")
    # ... processing code ...
    logger.debug("Processed 5 events")


async def save_results():
    """Called function - inherits trace context."""
    # No need to pass trace explicitly!
    logger.debug("Saving results to database")
    # ... save code ...
    logger.debug("Saved successfully")


# ============================================================================
# Example 4: Controller Integration
# ============================================================================

from fastapi import APIRouter, HTTPException
from backend.logging import set_trace_context, get_logger
from config.config import Config

router = APIRouter()
logger = get_logger(__name__)

@router.post("/api/incidents/analyze")
async def analyze_incident(request_body: dict):
    """
    Example: Full integration in FastAPI controller.
    
    1. Set trace context from request
    2. Check feature flags
    3. Process with trace logging
    4. Return results
    """
    # Set trace context at entry
    trace = request_body.get("trace", {})
    set_trace_context(trace)
    
    try:
        logger.info("Received incident analysis request")
        
        # Check if required features are enabled
        if not Config.is_stage_enabled("extraction"):
            raise HTTPException(
                status_code=503,
                detail="Extraction service currently disabled"
            )
        
        # Process request (all downstream logs include trace)
        # result = orchestrator.process_incident(request_body)
        
        logger.info("Completed incident analysis successfully")
        
        return {
            "status": "success",
            "trace": trace,
            # "data": result
        }
        
    except ValueError as e:
        logger.warning("Request validation failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error("Request processing failed", error=str(e))
        logger.exception("Full stack trace")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    finally:
        clear_trace_context()


# ============================================================================
# Example 5: Configuration Validation
# ============================================================================

def validate_and_print_config():
    """Example: Validate configuration on startup."""
    try:
        # Validate configuration
        Config.validate()
        print("✓ Configuration is valid")
        
        # Print configuration summary (only in DEBUG mode)
        if Config.DEBUG:
            Config.print_summary()
        
        # Check specific settings
        print(f"\nConfiguration Status:")
        print(f"  Debug mode: {Config.DEBUG}")
        print(f"  Log level: {Config.LOG_LEVEL}")
        print(f"  Default LLM: {Config.DEFAULT_LLM_PROVIDER}")
        
        print(f"\nProvider Flags:")
        print(f"  Text provider: {Config.is_provider_enabled('text')}")
        print(f"  Vision provider: {Config.is_provider_enabled('vision')}")
        print(f"  Quant provider: {Config.is_provider_enabled('quant')}")
        
        print(f"\nPipeline Stage Flags:")
        print(f"  Extraction: {Config.is_stage_enabled('extraction')}")
        print(f"  Fusion: {Config.is_stage_enabled('fusion')}")
        print(f"  Scoring: {Config.is_stage_enabled('scoring')}")
        print(f"  Alerts: {Config.is_stage_enabled('alerts')}")
        print(f"  Visualization: {Config.is_stage_enabled('visualization')}")
        
    except ValueError as e:
        print(f"✗ Configuration validation failed:")
        print(f"  {e}")
        exit(1)


# ============================================================================
# Example 6: Different Log Formats
# ============================================================================

from backend.logging import setup_logging

def configure_logging_for_environment():
    """Example: Configure logging based on environment."""
    
    if Config.DEBUG:
        # Development: Human-readable text format
        setup_logging(level="DEBUG", format="text")
        print("Configured logging: DEBUG level, TEXT format")
    else:
        # Production: Structured JSON format
        setup_logging(level="INFO", format="json")
        print("Configured logging: INFO level, JSON format")


# ============================================================================
# Example 7: Testing with Feature Flags
# ============================================================================

import os

def test_with_feature_flag_override():
    """Example: Override feature flags for testing."""
    
    # Save original value
    original = os.environ.get("ENABLE_VISION_PROVIDER")
    
    try:
        # Disable vision provider for this test
        os.environ["ENABLE_VISION_PROVIDER"] = "false"
        
        # Reload config (in practice, restart app)
        # Config would be reloaded here
        
        # Test without vision provider
        print("Testing with vision provider disabled...")
        # run_test()
        
    finally:
        # Restore original value
        if original:
            os.environ["ENABLE_VISION_PROVIDER"] = original
        else:
            os.environ.pop("ENABLE_VISION_PROVIDER", None)


# ============================================================================
# Main - Run Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Configuration Management & Logging Examples")
    print("=" * 70)
    print()
    
    # Example 1: Validate configuration
    print("1. Validating configuration...")
    validate_and_print_config()
    print()
    
    # Example 2: Configure logging
    print("2. Configuring logging...")
    configure_logging_for_environment()
    print()
    
    # Example 3: Check feature flags
    print("3. Checking feature flags...")
    signals = {"text": [], "vision": [], "quant": []}
    process_signals_with_flags(signals)
    print()
    
    # Example 4: Example request with trace logging
    print("4. Processing request with trace logging...")
    request = {
        "trace": {"requestId": "example-123", "userId": "user-456"},
        "signals": {"text": [], "vision": [], "quant": []}
    }
    process_request_with_trace_logger(request)
    print()
    
    print("=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)
