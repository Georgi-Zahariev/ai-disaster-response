"""
Test script for analyzer agents.

Tests text, vision, and quantitative analyzers with signals from providers.
Validates ExtractedObservation format and integration.
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
from backend.agents import (
    TextAnalyzer,
    VisionAnalyzer,
    QuantitativeAnalyzer
)


async def test_text_analyzer():
    """Test TextAnalyzer with text signals."""
    print("\n" + "="*80)
    print("TESTING TEXT ANALYZER")
    print("="*80)
    
    # Initialize provider and analyzer
    provider = TextFeedProvider()
    analyzer = TextAnalyzer()
    
    print("\n[Test 1] Fetching text signals and analyzing...")
    signals = await provider.fetch_text_signals(count=3)
    print(f"✓ Fetched {len(signals)} text signals")
    
    observations = []
    for signal in signals:
        obs_list = await analyzer.analyze(signal)
        observations.extend(obs_list)
    
    print(f"✓ Extracted {len(observations)} observations")
    
    # Validate observation structure
    print("\n[Test 2] Validating observation structure...")
    for i, obs in enumerate(observations):
        # Required fields
        assert "observationId" in obs, f"Observation {i} missing observationId"
        assert "observationType" in obs, f"Observation {i} missing observationType"
        assert "description" in obs, f"Observation {i} missing description"
        assert "sourceSignalIds" in obs, f"Observation {i} missing sourceSignalIds"
        assert "confidence" in obs, f"Observation {i} missing confidence"
        assert "severity" in obs, f"Observation {i} missing severity"
        assert "affectedSectors" in obs, f"Observation {i} missing affectedSectors"
        assert "affectedAssets" in obs, f"Observation {i} missing affectedAssets"
        assert "extractedData" in obs, f"Observation {i} missing extractedData"
        assert "evidence" in obs, f"Observation {i} missing evidence"
        
        # Validate types
        assert isinstance(obs["sourceSignalIds"], list), "sourceSignalIds must be list"
        assert isinstance(obs["affectedSectors"], list), "affectedSectors must be list"
        assert isinstance(obs["affectedAssets"], list), "affectedAssets must be list"
        assert isinstance(obs["extractedData"], dict), "extractedData must be dict"
        assert isinstance(obs["evidence"], list), "evidence must be list"
        
        # Validate confidence range
        assert 0.0 <= obs["confidence"] <= 1.0, f"Confidence {obs['confidence']} out of range"
        
        # Validate severity values
        assert obs["severity"] in ["low", "moderate", "high", "critical"], \
            f"Invalid severity: {obs['severity']}"
    
    print("✓ All observations have valid structure")
    print("✓ All field types are correct")
    print("✓ All confidence scores in valid range")
    print("✓ All severity levels valid")
    
    # Display sample observation
    print("\n[Sample Observation]")
    sample = observations[0].copy()
    # Truncate long fields for display
    if len(sample.get("description", "")) > 150:
        sample["description"] = sample["description"][:147] + "..."
    if len(sample.get("evidence", [])) > 2:
        sample["evidence"] = sample["evidence"][:2]
    print(json.dumps(sample, indent=2))
    
    print("\n✅ TEXT ANALYZER: ALL TESTS PASSED")
    return observations


async def test_vision_analyzer():
    """Test VisionAnalyzer with vision signals."""
    print("\n" + "="*80)
    print("TESTING VISION ANALYZER")
    print("="*80)
    
    # Initialize provider and analyzer
    provider = VisionFeedProvider()
    analyzer = VisionAnalyzer()
    
    print("\n[Test 1] Fetching vision signals and analyzing...")
    signals = await provider.fetch_vision_signals(count=3)
    print(f"✓ Fetched {len(signals)} vision signals")
    
    observations = []
    for signal in signals:
        obs_list = await analyzer.analyze(signal)
        observations.extend(obs_list)
    
    print(f"✓ Extracted {len(observations)} observations")
    
    # Validate observation structure
    print("\n[Test 2] Validating observation structure...")
    for i, obs in enumerate(observations):
        # Required fields
        assert "observationId" in obs, f"Observation {i} missing observationId"
        assert "observationType" in obs, f"Observation {i} missing observationType"
        assert "description" in obs, f"Observation {i} missing description"
        assert "sourceSignalIds" in obs, f"Observation {i} missing sourceSignalIds"
        assert "confidence" in obs, f"Observation {i} missing confidence"
        assert "severity" in obs, f"Observation {i} missing severity"
        assert "affectedSectors" in obs, f"Observation {i} missing affectedSectors"
        assert "affectedAssets" in obs, f"Observation {i} missing affectedAssets"
        assert "extractedData" in obs, f"Observation {i} missing extractedData"
        assert "evidence" in obs, f"Observation {i} missing evidence"
        
        # Vision-specific extracted data
        extracted_data = obs["extractedData"]
        assert "imageUrl" in extracted_data, "Missing imageUrl in extractedData"
        assert "detectedObjects" in extracted_data, "Missing detectedObjects in extractedData"
        assert "objectCounts" in extracted_data, "Missing objectCounts in extractedData"
        
        # Validate confidence range
        assert 0.0 <= obs["confidence"] <= 1.0, f"Confidence {obs['confidence']} out of range"
    
    print("✓ All observations have valid structure")
    print("✓ Vision-specific fields present")
    print("✓ All confidence scores in valid range")
    
    # Display sample observation
    print("\n[Sample Observation]")
    sample = observations[0].copy()
    # Truncate detected objects for display
    if "detectedObjects" in sample["extractedData"]:
        if len(sample["extractedData"]["detectedObjects"]) > 3:
            sample["extractedData"]["detectedObjects"] = \
                sample["extractedData"]["detectedObjects"][:3]
    if len(sample.get("evidence", [])) > 2:
        sample["evidence"] = sample["evidence"][:2]
    print(json.dumps(sample, indent=2))
    
    print("\n✅ VISION ANALYZER: ALL TESTS PASSED")
    return observations


async def test_quantitative_analyzer():
    """Test QuantitativeAnalyzer with quantitative signals."""
    print("\n" + "="*80)
    print("TESTING QUANTITATIVE ANALYZER")
    print("="*80)
    
    # Initialize provider and analyzer
    provider = QuantitativeFeedProvider()
    analyzer = QuantitativeAnalyzer()
    
    print("\n[Test 1] Fetching quantitative signals and analyzing...")
    signals = await provider.fetch_quantitative_signals(count=3)
    print(f"✓ Fetched {len(signals)} quantitative signals")
    
    observations = []
    for signal in signals:
        obs_list = await analyzer.analyze(signal)
        observations.extend(obs_list)
    
    print(f"✓ Extracted {len(observations)} observations")
    
    # Validate observation structure
    print("\n[Test 2] Validating observation structure...")
    for i, obs in enumerate(observations):
        # Required fields
        assert "observationId" in obs, f"Observation {i} missing observationId"
        assert "observationType" in obs, f"Observation {i} missing observationType"
        assert "description" in obs, f"Observation {i} missing description"
        assert "sourceSignalIds" in obs, f"Observation {i} missing sourceSignalIds"
        assert "confidence" in obs, f"Observation {i} missing confidence"
        assert "severity" in obs, f"Observation {i} missing severity"
        assert "affectedSectors" in obs, f"Observation {i} missing affectedSectors"
        assert "affectedAssets" in obs, f"Observation {i} missing affectedAssets"
        assert "extractedData" in obs, f"Observation {i} missing extractedData"
        assert "evidence" in obs, f"Observation {i} missing evidence"
        
        # Quantitative-specific extracted data
        extracted_data = obs["extractedData"]
        assert "measurementType" in extracted_data, "Missing measurementType in extractedData"
        assert "currentValue" in extracted_data, "Missing currentValue in extractedData"
        assert "deviationScore" in extracted_data, "Missing deviationScore in extractedData"
        assert "anomalyInfo" in extracted_data, "Missing anomalyInfo in extractedData"
        
        # Validate deviation score range
        assert 0.0 <= extracted_data["deviationScore"] <= 1.0, \
            f"Deviation score {extracted_data['deviationScore']} out of range"
        
        # Validate confidence range
        assert 0.0 <= obs["confidence"] <= 1.0, f"Confidence {obs['confidence']} out of range"
    
    print("✓ All observations have valid structure")
    print("✓ Quantitative-specific fields present")
    print("✓ All confidence scores in valid range")
    print("✓ All deviation scores in valid range")
    
    # Display sample observation
    print("\n[Sample Observation]")
    sample = observations[0].copy()
    if len(sample.get("evidence", [])) > 2:
        sample["evidence"] = sample["evidence"][:2]
    print(json.dumps(sample, indent=2))
    
    print("\n✅ QUANTITATIVE ANALYZER: ALL TESTS PASSED")
    return observations


async def test_cross_analyzer_integration():
    """Test integration across all analyzers."""
    print("\n" + "="*80)
    print("TESTING CROSS-ANALYZER INTEGRATION")
    print("="*80)
    
    # Initialize providers and analyzers
    text_provider = TextFeedProvider()
    vision_provider = VisionFeedProvider()
    quant_provider = QuantitativeFeedProvider()
    
    text_analyzer = TextAnalyzer()
    vision_analyzer = VisionAnalyzer()
    quant_analyzer = QuantitativeAnalyzer()
    
    print("\n[Test] Fetching signals and analyzing across all modalities...")
    
    # Fetch signals concurrently
    text_signals, vision_signals, quant_signals = await asyncio.gather(
        text_provider.fetch_text_signals(count=2),
        vision_provider.fetch_vision_signals(count=2),
        quant_provider.fetch_quantitative_signals(count=2)
    )
    
    print(f"✓ Fetched signals: {len(text_signals)} text, {len(vision_signals)} vision, {len(quant_signals)} quant")
    
    # Analyze signals
    text_obs = []
    for signal in text_signals:
        text_obs.extend(await text_analyzer.analyze(signal))
    
    vision_obs = []
    for signal in vision_signals:
        vision_obs.extend(await vision_analyzer.analyze(signal))
    
    quant_obs = []
    for signal in quant_signals:
        quant_obs.extend(await quant_analyzer.analyze(signal))
    
    all_observations = text_obs + vision_obs + quant_obs
    
    print(f"✓ Extracted total of {len(all_observations)} observations")
    print(f"  - Text: {len(text_obs)}")
    print(f"  - Vision: {len(vision_obs)}")
    print(f"  - Quantitative: {len(quant_obs)}")
    
    # Verify all have unique IDs
    all_ids = [obs["observationId"] for obs in all_observations]
    unique_ids = set(all_ids)
    assert len(unique_ids) == len(all_ids), "Observation IDs should be unique"
    print("✓ All observation IDs are unique")
    
    # Verify consistent structure across all observations
    for obs in all_observations:
        assert "observationId" in obs
        assert "observationType" in obs
        assert "description" in obs
        assert "confidence" in obs
        assert "severity" in obs
        assert 0.0 <= obs["confidence"] <= 1.0
    print("✓ All observations have consistent structure")
    
    # Check observation type distribution
    obs_types = [obs["observationType"] for obs in all_observations]
    type_counts = {}
    for obs_type in obs_types:
        type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
    
    print(f"\n[Observation Type Distribution]")
    for obs_type, count in sorted(type_counts.items()):
        print(f"  {obs_type}: {count}")
    
    # Check severity distribution
    severity_counts = {}
    for obs in all_observations:
        severity = obs["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"\n[Severity Distribution]")
    for severity in ["low", "moderate", "high", "critical"]:
        count = severity_counts.get(severity, 0)
        if count > 0:
            print(f"  {severity}: {count}")
    
    # Check sector coverage
    all_sectors = set()
    for obs in all_observations:
        all_sectors.update(obs.get("affectedSectors", []))
    
    print(f"\n[Affected Sectors] {len(all_sectors)} unique sectors:")
    for sector in sorted(all_sectors):
        print(f"  - {sector}")
    
    print("\n✅ CROSS-ANALYZER INTEGRATION: ALL TESTS PASSED")


async def test_observation_quality():
    """Test quality and completeness of extracted observations."""
    print("\n" + "="*80)
    print("TESTING OBSERVATION QUALITY")
    print("="*80)
    
    # Get sample observations from each analyzer
    text_provider = TextFeedProvider()
    vision_provider = VisionFeedProvider()
    quant_provider = QuantitativeFeedProvider()
    
    text_analyzer = TextAnalyzer()
    vision_analyzer = VisionAnalyzer()
    quant_analyzer = QuantitativeAnalyzer()
    
    # Get one observation from each
    text_signal = (await text_provider.fetch_text_signals(count=1))[0]
    vision_signal = (await vision_provider.fetch_vision_signals(count=1))[0]
    quant_signal = (await quant_provider.fetch_quantitative_signals(count=1))[0]
    
    text_obs = (await text_analyzer.analyze(text_signal))[0]
    vision_obs = (await vision_analyzer.analyze(vision_signal))[0]
    quant_obs = (await quant_analyzer.analyze(quant_signal))[0]
    
    print("\n[Test 1] Checking description quality...")
    for obs, name in [(text_obs, "Text"), (vision_obs, "Vision"), (quant_obs, "Quantitative")]:
        desc = obs["description"]
        assert len(desc) > 0, f"{name} observation has empty description"
        assert len(desc) >= 20, f"{name} observation description too short"
        print(f"✓ {name} observation has valid description ({len(desc)} chars)")
    
    print("\n[Test 2] Checking evidence quality...")
    for obs, name in [(text_obs, "Text"), (vision_obs, "Vision"), (quant_obs, "Quantitative")]:
        evidence = obs["evidence"]
        assert len(evidence) > 0, f"{name} observation has no evidence"
        assert len(evidence) >= 2, f"{name} observation has insufficient evidence"
        print(f"✓ {name} observation has {len(evidence)} evidence items")
    
    print("\n[Test 3] Checking location data...")
    for obs, name in [(text_obs, "Text"), (vision_obs, "Vision"), (quant_obs, "Quantitative")]:
        location = obs.get("location")
        if location:
            assert "latitude" in location, f"{name} location missing latitude"
            assert "longitude" in location, f"{name} location missing longitude"
            print(f"✓ {name} observation has valid location")
    
    print("\n[Test 4] Checking time references...")
    for obs, name in [(text_obs, "Text"), (vision_obs, "Vision"), (quant_obs, "Quantitative")]:
        time_ref = obs.get("timeReference")
        if time_ref:
            assert "observedAt" in time_ref or "reportedAt" in time_ref, \
                f"{name} timeReference missing timestamps"
            print(f"✓ {name} observation has valid time reference")
    
    print("\n[Test 5] Checking extracted data completeness...")
    # Text observations should have text content
    assert "rawText" in text_obs["extractedData"], "Text observation missing rawText"
    assert "keywords" in text_obs["extractedData"], "Text observation missing keywords"
    print("✓ Text observation has complete extractedData")
    
    # Vision observations should have object info
    assert "detectedObjects" in vision_obs["extractedData"], "Vision observation missing detectedObjects"
    assert "objectCounts" in vision_obs["extractedData"], "Vision observation missing objectCounts"
    print("✓ Vision observation has complete extractedData")
    
    # Quantitative observations should have measurement info
    assert "currentValue" in quant_obs["extractedData"], "Quant observation missing currentValue"
    assert "deviationScore" in quant_obs["extractedData"], "Quant observation missing deviationScore"
    assert "anomalyInfo" in quant_obs["extractedData"], "Quant observation missing anomalyInfo"
    print("✓ Quantitative observation has complete extractedData")
    
    print("\n✅ OBSERVATION QUALITY: ALL TESTS PASSED")


async def main():
    """Run all analyzer tests."""
    print("\n" + "="*80)
    print("ANALYZER TEST SUITE")
    print("="*80)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        # Test individual analyzers
        text_observations = await test_text_analyzer()
        vision_observations = await test_vision_analyzer()
        quant_observations = await test_quantitative_analyzer()
        
        # Test cross-analyzer integration
        await test_cross_analyzer_integration()
        
        # Test observation quality
        await test_observation_quality()
        
        # Final summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED SUCCESSFULLY")
        print("="*80)
        print(f"Test completed at: {datetime.now().isoformat()}")
        print("\nAll three analyzers are working correctly:")
        print("  ✓ TextAnalyzer - Extracts observations from text signals")
        print("  ✓ VisionAnalyzer - Extracts observations from vision signals")
        print("  ✓ QuantitativeAnalyzer - Extracts observations from sensor signals")
        print("\nObservations are properly formatted and ready for fusion.")
        
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
