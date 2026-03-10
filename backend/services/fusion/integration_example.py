"""
Integration example: Using the fusion service in the orchestrator.

This file demonstrates how to integrate the real SignalFusionService
with the IncidentOrchestrator to replace the mock fusion implementation.
"""

from typing import Dict, Any, List, Tuple

# Example: Modified IncidentOrchestrator with real fusion service
class IncidentOrchestratorWithFusion:
    """
    Example orchestrator using the real fusion service.
    
    This shows how to integrate SignalFusionService into the
    incident processing pipeline.
    """
    
    def __init__(self):
        """Initialize orchestrator with real services."""
        
        # Import real services
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
        from backend.services.fusion import SignalFusionService
        
        # Initialize providers
        self.text_provider = TextFeedProvider()
        self.vision_provider = VisionFeedProvider()
        self.quant_provider = QuantitativeFeedProvider()
        
        # Initialize analyzers
        self.text_analyzer = TextAnalyzer()
        self.vision_analyzer = VisionAnalyzer()
        self.quant_analyzer = QuantitativeAnalyzer()
        
        # Initialize fusion service ✅ REAL SERVICE
        self.fusion_service = SignalFusionService()
        
        # TODO: Initialize other services
        self.scoring_service = None  # DisruptionScoringService()
        self.alert_service = None  # AlertGenerationService()
        self.visualization_mapper = None  # VisualizationMapper()
    
    async def _extract_observations(
        self,
        request: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Phase 1: Extract structured observations from raw signals.
        
        ✅ Uses real analyzers (TextAnalyzer, VisionAnalyzer, QuantitativeAnalyzer)
        """
        observations = []
        warnings = []
        
        # Extract from text signals
        text_signals = request.get("textSignals", [])
        for i, signal in enumerate(text_signals):
            try:
                obs = await self.text_analyzer.analyze(signal)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to extract from text signal {i}: {str(e)}"
                warnings.append(warning)
                print(f"[Orchestrator] Warning: {warning}")
        
        # Extract from vision signals
        vision_signals = request.get("visionSignals", [])
        for i, signal in enumerate(vision_signals):
            try:
                obs = await self.vision_analyzer.analyze(signal)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to analyze vision signal {i}: {str(e)}"
                warnings.append(warning)
                print(f"[Orchestrator] Warning: {warning}")
        
        # Extract from quantitative signals
        quant_signals = request.get("quantSignals", [])
        for i, signal in enumerate(quant_signals):
            try:
                obs = await self.quant_analyzer.analyze(signal)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to analyze quantitative signal {i}: {str(e)}"
                warnings.append(warning)
                print(f"[Orchestrator] Warning: {warning}")
        
        return observations, warnings
    
    async def _fuse_observations(
        self,
        observations: List[Dict[str, Any]],
        request: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Phase 2: Fuse observations into coherent events.
        
        ✅ Uses real SignalFusionService (not mock)
        """
        warnings = []
        
        if not observations:
            warnings.append("No observations to fuse")
            return [], warnings
        
        try:
            # Extract fusion options from request
            options = request.get("fusionOptions", {})
            
            # Use REAL fusion service ✅
            events = await self.fusion_service.fuse(observations, options)
            
            return events, warnings
            
        except Exception as e:
            error_msg = f"Fusion failed: {str(e)}"
            warnings.append(error_msg)
            print(f"[Orchestrator] Warning: {error_msg}")
            return [], warnings


# Example usage
async def example_integration():
    """
    Example: End-to-end pipeline with real fusion service.
    """
    
    # Initialize orchestrator with real services
    orchestrator = IncidentOrchestratorWithFusion()
    
    # Fetch signals from providers
    text_signals = await orchestrator.text_provider.fetch_text_signals(count=5)
    vision_signals = await orchestrator.vision_provider.fetch_vision_signals(count=3)
    quant_signals = await orchestrator.quant_provider.fetch_quantitative_signals(count=2)
    
    # Build request
    request = {
        "textSignals": text_signals,
        "visionSignals": vision_signals,
        "quantSignals": quant_signals,
        "fusionOptions": {
            "minConfidenceThreshold": 0.5  # Optional: custom threshold
        }
    }
    
    # Phase 1: Extract observations
    observations, extraction_warnings = await orchestrator._extract_observations(request)
    print(f"Extracted {len(observations)} observations")
    
    # Phase 2: Fuse observations
    events, fusion_warnings = await orchestrator._fuse_observations(observations, request)
    print(f"Created {len(events)} fused events")
    
    # Display results
    for event in events:
        print(f"\n{event['eventType']}: {event['title']}")
        print(f"  Confidence: {event['confidence']:.2f}")
        print(f"  Severity: {event['severity']}")
        print(f"  Observations: {len(event['observations'])}")
        print(f"  Modalities: {event['metadata']['modalities']}")
        print(f"  Affected sectors: {', '.join(event['affectedSectors'])}")


# Example: Configuring fusion service for specific scenarios
async def example_custom_thresholds():
    """
    Example: Custom fusion thresholds for specific use cases.
    """
    
    from backend.services.fusion import SignalFusionService
    
    # Scenario 1: Urban traffic monitoring (tight spatial clustering)
    urban_fusion = SignalFusionService()
    urban_fusion.spatial_threshold_meters = 1000  # 1km for dense urban area
    urban_fusion.temporal_threshold_seconds = 900  # 15 min for fast-moving events
    
    # Scenario 2: Regional weather events (broad spatial clustering)
    weather_fusion = SignalFusionService()
    weather_fusion.spatial_threshold_meters = 20000  # 20km for regional events
    weather_fusion.temporal_threshold_seconds = 7200  # 2 hours for slow weather
    
    # Scenario 3: High-confidence critical alerts only
    critical_fusion = SignalFusionService()
    critical_fusion.min_confidence_threshold = 0.8
    critical_fusion.multimodal_confidence_boost = 0.15  # Higher boost for agreement
    
    # Use appropriate fusion service based on request type
    request_type = "urban_traffic"
    
    if request_type == "urban_traffic":
        fusion_service = urban_fusion
    elif request_type == "weather":
        fusion_service = weather_fusion
    elif request_type == "critical_alert":
        fusion_service = critical_fusion
    else:
        fusion_service = SignalFusionService()  # Default
    
    # Use configured service
    observations = [...]  # From analyzers
    events = await fusion_service.fuse(observations)
    
    return events


# Example: Monitoring fusion performance
async def example_fusion_monitoring():
    """
    Example: Monitor fusion service performance and quality.
    """
    
    from backend.services.fusion import SignalFusionService
    import time
    
    fusion_service = SignalFusionService()
    observations = [...]  # From analyzers
    
    # Time the fusion
    start_time = time.time()
    events = await fusion_service.fuse(observations)
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Calculate metrics
    total_observations = len(observations)
    total_events = len(events)
    compression_ratio = total_observations / total_events if total_events > 0 else 0
    
    # Count multimodal events
    multimodal_events = sum(
        1 for event in events 
        if len(event['metadata']['modalities']) > 1
    )
    
    # Average confidence
    avg_confidence = sum(event['confidence'] for event in events) / len(events) if events else 0
    
    print(f"\n[Fusion Performance Metrics]")
    print(f"  Observations: {total_observations}")
    print(f"  Events: {total_events}")
    print(f"  Compression ratio: {compression_ratio:.2f}x")
    print(f"  Multimodal events: {multimodal_events} ({multimodal_events/total_events*100:.1f}%)")
    print(f"  Average confidence: {avg_confidence:.2f}")
    print(f"  Processing time: {elapsed_ms:.1f}ms")
    
    return {
        "observations": total_observations,
        "events": total_events,
        "compression_ratio": compression_ratio,
        "multimodal_events": multimodal_events,
        "avg_confidence": avg_confidence,
        "processing_time_ms": elapsed_ms
    }


if __name__ == "__main__":
    import asyncio
    import sys
    from pathlib import Path
    
    # Add project root to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    
    print("Running fusion integration example...")
    asyncio.run(example_integration())
