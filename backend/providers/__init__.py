"""
Provider modules for multimodal disaster-response signals.

This package contains mock providers for:
- Text feeds (social media, emergency services, news)
- Vision feeds (satellite, cameras, drones)
- Quantitative feeds (sensors, metrics)
- Weather data (existing provider)

Each provider returns normalized signals matching TypeScript schemas.
In production, these mocks will be replaced with real API integrations.
"""

from .weather_provider import WeatherProvider
from .text_feed_provider import TextFeedProvider
from .vision_feed_provider import VisionFeedProvider
from .quantitative_feed_provider import QuantitativeFeedProvider
from .facility_baseline_provider import FacilityBaselineProvider
from .planning_context_provider import PlanningContextProvider

__all__ = [
    "WeatherProvider",
    "TextFeedProvider",
    "VisionFeedProvider",
    "QuantitativeFeedProvider",
    "FacilityBaselineProvider",
    "PlanningContextProvider",
]
