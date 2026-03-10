"""
Test script for provider modules.

Tests all three provider implementations:
- TextFeedProvider
- VisionFeedProvider
- QuantitativeFeedProvider

Verifies signal format, filtering, and schema compliance.
"""

import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backend.providers import (
    TextFeedProvider,
    VisionFeedProvider,
    QuantitativeFeedProvider
)


async def test_text_provider():
    """Test TextFeedProvider."""
    print("\n" + "="*80)
    print("TESTING TEXT FEED PROVIDER")
    print("="*80)
    
    provider = TextFeedProvider()
    
    # Test 1: Fetch signals
    print("\n[Test 1] Fetching 5 text signals...")
    signals = await provider.fetch_text_signals(count=5)
    print(f"✓ Received {len(signals)} signals")
    
    # Validate structure
    for i, signal in enumerate(signals):
        assert "signalId" in signal, f"Signal {i} missing signalId"
        assert "signalType" in signal, f"Signal {i} missing signalType"
        assert signal["signalType"] == "text", f"Signal {i} has wrong type"
        assert "source" in signal, f"Signal {i} missing source"
        assert "content" in signal, f"Signal {i} missing content"
        assert "confidence" in signal, f"Signal {i} missing confidence"
        assert "location" in signal, f"Signal {i} missing location"
        assert "createdAt" in signal, f"Signal {i} missing createdAt"
    
    print("✓ All signals have valid structure")
    
    # Display sample signal
    print("\n[Sample Signal]")
    print(json.dumps(signals[0], indent=2))
    
    # Test 2: Filter by source
    print("\n[Test 2] Filtering by source (emergency_services)...")
    filtered = await provider.fetch_text_signals(
        count=3,
        sources=["emergency_services"]
    )
    for signal in filtered:
        assert signal["source"] == "emergency_services"
    print(f"✓ All {len(filtered)} signals from emergency_services")
    
    # Test 3: Filter by severity
    print("\n[Test 3] Filtering by severity (critical)...")
    critical_signals = await provider.fetch_text_signals(
        count=2,
        severity_filter="critical"
    )
    for signal in critical_signals:
        assert signal["metadata"]["severity_hint"] == "critical"
    print(f"✓ All {len(critical_signals)} signals have critical severity")
    
    # Test 4: Get supported sources
    print("\n[Test 4] Getting supported sources...")
    sources = provider.get_supported_sources()
    print(f"✓ {len(sources)} sources supported: {', '.join(sources)}")
    
    print("\n✅ TEXT PROVIDER: ALL TESTS PASSED")


async def test_vision_provider():
    """Test VisionFeedProvider."""
    print("\n" + "="*80)
    print("TESTING VISION FEED PROVIDER")
    print("="*80)
    
    provider = VisionFeedProvider()
    
    # Test 1: Fetch signals
    print("\n[Test 1] Fetching 4 vision signals...")
    signals = await provider.fetch_vision_signals(count=4)
    print(f"✓ Received {len(signals)} signals")
    
    # Validate structure
    for i, signal in enumerate(signals):
        assert "signalId" in signal, f"Signal {i} missing signalId"
        assert "signalType" in signal, f"Signal {i} missing signalType"
        assert signal["signalType"] == "vision", f"Signal {i} has wrong type"
        assert "source" in signal, f"Signal {i} missing source"
        assert "imageUrl" in signal, f"Signal {i} missing imageUrl"
        assert "detectedObjects" in signal, f"Signal {i} missing detectedObjects"
        assert "sceneClassification" in signal, f"Signal {i} missing sceneClassification"
        assert "confidence" in signal, f"Signal {i} missing confidence"
        assert "location" in signal, f"Signal {i} missing location"
        
        # Validate detected objects
        for obj in signal["detectedObjects"]:
            assert "label" in obj
            assert "confidence" in obj
            assert "bbox" in obj
            assert len(obj["bbox"]) == 4, "bbox should have 4 coordinates"
    
    print("✓ All signals have valid structure")
    print("✓ All detected objects have valid bounding boxes")
    
    # Display sample signal
    print("\n[Sample Signal]")
    sample = signals[0].copy()
    # Truncate detected objects for display
    if len(sample["detectedObjects"]) > 3:
        sample["detectedObjects"] = sample["detectedObjects"][:3]
    print(json.dumps(sample, indent=2))
    
    # Test 2: Filter by source
    print("\n[Test 2] Filtering by source (satellite)...")
    filtered = await provider.fetch_vision_signals(
        count=2,
        sources=["satellite"]
    )
    for signal in filtered:
        assert signal["source"] == "satellite"
    print(f"✓ All {len(filtered)} signals from satellite")
    
    # Test 3: Analyze image (mock CV analysis)
    print("\n[Test 3] Analyzing image...")
    analysis = await provider.analyze_image(
        image_url="https://example.com/image.jpg",
        analysis_type="damage_assessment"
    )
    assert "detectedObjects" in analysis
    assert "sceneAnalysis" in analysis
    print(f"✓ Analysis returned {len(analysis['detectedObjects'])} objects")
    print(f"  Damage level: {analysis['sceneAnalysis'].get('damage_level', 'unknown')}")
    
    # Test 4: Get supported sources
    print("\n[Test 4] Getting supported sources...")
    sources = provider.get_supported_sources()
    print(f"✓ {len(sources)} sources supported: {', '.join(sources)}")
    
    print("\n✅ VISION PROVIDER: ALL TESTS PASSED")


async def test_quantitative_provider():
    """Test QuantitativeFeedProvider."""
    print("\n" + "="*80)
    print("TESTING QUANTITATIVE FEED PROVIDER")
    print("="*80)
    
    provider = QuantitativeFeedProvider()
    
    # Test 1: Fetch signals
    print("\n[Test 1] Fetching 5 quantitative signals...")
    signals = await provider.fetch_quantitative_signals(count=5)
    print(f"✓ Received {len(signals)} signals")
    
    # Validate structure
    for i, signal in enumerate(signals):
        assert "signalId" in signal, f"Signal {i} missing signalId"
        assert "signalType" in signal, f"Signal {i} missing signalType"
        assert signal["signalType"] == "quantitative", f"Signal {i} has wrong type"
        assert "source" in signal, f"Signal {i} missing source"
        assert "measurementType" in signal, f"Signal {i} missing measurementType"
        assert "value" in signal, f"Signal {i} missing value"
        assert "units" in signal, f"Signal {i} missing units"
        assert "baselineValue" in signal, f"Signal {i} missing baselineValue"
        assert "deviationScore" in signal, f"Signal {i} missing deviationScore"
        assert "confidence" in signal, f"Signal {i} missing confidence"
        assert "location" in signal, f"Signal {i} missing location"
        
        # Validate deviation score range
        assert 0 <= signal["deviationScore"] <= 1, "deviationScore should be 0-1"
    
    print("✓ All signals have valid structure")
    print("✓ All deviation scores in valid range")
    
    # Display sample signal
    print("\n[Sample Signal]")
    print(json.dumps(signals[0], indent=2))
    
    # Test 2: Filter by measurement type
    print("\n[Test 2] Filtering by measurement type (traffic_flow)...")
    filtered = await provider.fetch_quantitative_signals(
        count=2,
        measurement_types=["traffic_flow", "average_speed"]
    )
    for signal in filtered:
        assert signal["measurementType"] in ["traffic_flow", "average_speed"]
    print(f"✓ All {len(filtered)} signals match requested measurement types")
    
    # Test 3: Filter by severity
    print("\n[Test 3] Filtering by severity (critical)...")
    critical_signals = await provider.fetch_quantitative_signals(
        count=3,
        severity_filter="critical"
    )
    for signal in critical_signals:
        assert signal["metadata"]["severity_hint"] == "critical"
    print(f"✓ All {len(critical_signals)} signals have critical severity")
    
    # Test 4: Get time series (mock)
    print("\n[Test 4] Getting time series data...")
    time_series = await provider.get_time_series(
        source="wsdot_traffic_sensor",
        measurement_type="traffic_flow",
        location={"latitude": 47.6062, "longitude": -122.3321},
        hours=6
    )
    assert len(time_series) == 6
    print(f"✓ Retrieved {len(time_series)} hours of time series data")
    
    # Test 5: Get supported sources and measurement types
    print("\n[Test 5] Getting supported sources and measurement types...")
    sources = provider.get_supported_sources()
    measurement_types = provider.get_supported_measurement_types()
    print(f"✓ {len(sources)} sources supported")
    print(f"✓ {len(measurement_types)} measurement types supported")
    
    print("\n✅ QUANTITATIVE PROVIDER: ALL TESTS PASSED")


async def test_cross_provider_integration():
    """Test integration across all providers."""
    print("\n" + "="*80)
    print("TESTING CROSS-PROVIDER INTEGRATION")
    print("="*80)
    
    text_provider = TextFeedProvider()
    vision_provider = VisionFeedProvider()
    quant_provider = QuantitativeFeedProvider()
    
    print("\n[Test] Fetching signals from all providers...")
    
    # Fetch from all providers concurrently
    text_signals, vision_signals, quant_signals = await asyncio.gather(
        text_provider.fetch_text_signals(count=3),
        vision_provider.fetch_vision_signals(count=3),
        quant_provider.fetch_quantitative_signals(count=3)
    )
    
    total_signals = len(text_signals) + len(vision_signals) + len(quant_signals)
    print(f"✓ Received total of {total_signals} signals")
    print(f"  - Text: {len(text_signals)}")
    print(f"  - Vision: {len(vision_signals)}")
    print(f"  - Quantitative: {len(quant_signals)}")
    
    # Verify all have unique IDs
    all_ids = (
        [s["signalId"] for s in text_signals] +
        [s["signalId"] for s in vision_signals] +
        [s["signalId"] for s in quant_signals]
    )
    unique_ids = set(all_ids)
    assert len(unique_ids) == len(all_ids), "Signal IDs should be unique"
    print("✓ All signal IDs are unique")
    
    # Verify all have timestamps
    for i, signal in enumerate(text_signals + vision_signals + quant_signals):
        assert "createdAt" in signal, f"Signal {i} missing createdAt"
        # Validate ISO 8601 format
        try:
            datetime.fromisoformat(signal["createdAt"].replace("Z", "+00:00"))
        except ValueError as e:
            raise AssertionError(f"Signal {i} invalid timestamp format: {signal['createdAt']} - {e}")
    print("✓ All signals have valid ISO 8601 timestamps")
    
    # Verify all have location data
    for i, signal in enumerate(text_signals + vision_signals + quant_signals):
        assert "location" in signal, f"Signal {i} missing location"
        assert "latitude" in signal["location"], f"Signal {i} missing latitude"
        assert "longitude" in signal["location"], f"Signal {i} missing longitude"
        # Validate coordinates are in Washington State range
        lat = signal["location"]["latitude"]
        lon = signal["location"]["longitude"]
        assert 45 < lat < 49, f"Signal {i}: Latitude {lat} out of WA range"
        assert -125 < lon < -116, f"Signal {i}: Longitude {lon} out of WA range"
    print("✓ All signals have valid location data (Washington State)")
    
    print("\n✅ CROSS-PROVIDER INTEGRATION: ALL TESTS PASSED")


async def main():
    """Run all provider tests."""
    print("\n" + "="*80)
    print("PROVIDER TEST SUITE")
    print("="*80)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        # Test individual providers
        await test_text_provider()
        await test_vision_provider()
        await test_quantitative_provider()
        
        # Test cross-provider integration
        await test_cross_provider_integration()
        
        # Final summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED SUCCESSFULLY")
        print("="*80)
        print(f"Test completed at: {datetime.now().isoformat()}")
        print("\nAll three providers are working correctly:")
        print("  ✓ TextFeedProvider - 16 disaster scenarios")
        print("  ✓ VisionFeedProvider - 14 visual observation scenarios")
        print("  ✓ QuantitativeFeedProvider - 24 sensor/metrics scenarios")
        print("\nProviders are ready for integration with the orchestrator.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
