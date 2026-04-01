"""Provider modules for incident, route, weather, facility, and planning context data.

Current provider model is hybrid:
- Deterministic/mock providers for testable extraction inputs
- Seed/static providers for baseline/planning context
- Live API adapters for weather and facilities
"""

from .weather_provider import WeatherProvider
from .text_feed_provider import TextFeedProvider
from .vision_feed_provider import VisionFeedProvider
from .quantitative_feed_provider import QuantitativeFeedProvider
from .facility_baseline_provider import FacilityBaselineProvider
from .planning_context_provider import PlanningContextProvider
from .nws_weather_provider import NWSWeatherProvider
from .osm_facility_provider import OSMFacilityProvider

__all__ = [
    "WeatherProvider",
    "TextFeedProvider",
    "VisionFeedProvider",
    "QuantitativeFeedProvider",
    "FacilityBaselineProvider",
    "PlanningContextProvider",
    "NWSWeatherProvider",
    "OSMFacilityProvider",
]
