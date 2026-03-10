"""
Text Feed Provider - Mock implementation.

Provides text-based signals from various sources:
- Social media feeds (Twitter/X, Reddit, etc.)
- Emergency services reports (911, fire dept, police)
- News outlets (local/national news)
- Transportation authorities (DOT, transit agencies)
- Corporate communications (logistics companies)

In production, this will integrate with:
- Twitter/X API for real-time social media
- Emergency services data feeds
- News aggregation APIs
- Transportation authority APIs
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import random
import uuid


class TextFeedProvider:
    """
    Mock provider for text-based signals.
    
    Simulates various text sources reporting disaster events
    and supply chain disruptions.
    """
    
    def __init__(self):
        """Initialize the text feed provider."""
        self.mock_scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> List[Dict[str, Any]]:
        """
        Initialize library of mock disaster scenarios.
        
        Each scenario represents a realistic text report about
        a disaster or supply chain disruption event.
        """
        return [
            # TRANSPORTATION DISRUPTIONS
            {
                "source": "twitter",
                "content": "I-5 completely blocked near Seattle due to multi-vehicle collision. Emergency crews on scene. Expect major delays. #SeattleTraffic #I5Closure",
                "severity": "high",
                "location": {"latitude": 47.6062, "longitude": -122.3321, "address": "I-5, Seattle, WA"},
                "sectors": ["transportation"],
                "assets": ["highway"]
            },
            {
                "source": "emergency_services",
                "content": "ALERT: Bridge collapse on SR-520 eastbound at Mile Post 6. All lanes closed indefinitely. Injuries reported. Alternate routes strongly recommended.",
                "severity": "critical",
                "location": {"latitude": 47.6434, "longitude": -122.2905, "address": "SR-520, Bellevue, WA"},
                "sectors": ["transportation", "infrastructure"],
                "assets": ["bridge", "highway"]
            },
            {
                "source": "dot",
                "content": "I-405 southbound closed between exits 12-15 due to fuel tanker fire. Hazmat crews responding. Estimated closure: 8-12 hours. Use I-5 as alternate.",
                "severity": "high",
                "location": {"latitude": 47.6543, "longitude": -122.1891, "address": "I-405 S, Kirkland, WA"},
                "sectors": ["transportation", "energy"],
                "assets": ["highway"]
            },
            
            # PORT & SHIPPING DISRUPTIONS
            {
                "source": "news",
                "content": "Port of Seattle operations suspended after equipment malfunction in Terminal 5. Over 50 containers stuck mid-transfer. Estimated resumption: 24-48 hours.",
                "severity": "high",
                "location": {"latitude": 47.5768, "longitude": -122.3505, "address": "Port of Seattle, Seattle, WA"},
                "sectors": ["transportation", "logistics"],
                "assets": ["port", "terminal"]
            },
            {
                "source": "corporate",
                "content": "BNSF Railway operations halted on northern corridor due to landslide blocking tracks near Everett. Freight backlog expected. Seeking alternate rail routes.",
                "severity": "high",
                "location": {"latitude": 47.9790, "longitude": -122.2021, "address": "BNSF Railway, Everett, WA"},
                "sectors": ["transportation", "logistics"],
                "assets": ["rail", "tracks"]
            },
            {
                "source": "twitter",
                "content": "Massive cargo ship grounded in Puget Sound entrance. Coast Guard blocking marine traffic. Could affect port operations for days. #ShippingDisaster",
                "severity": "critical",
                "location": {"latitude": 47.6097, "longitude": -122.6319, "address": "Puget Sound, WA"},
                "sectors": ["transportation", "logistics"],
                "assets": ["port", "waterway"]
            },
            
            # WAREHOUSE & DISTRIBUTION DISRUPTIONS
            {
                "source": "emergency_services",
                "content": "Major warehouse fire at Amazon fulfillment center in Kent. Fire crews battling 3-alarm blaze. Facility likely total loss. No injuries reported.",
                "severity": "critical",
                "location": {"latitude": 47.3809, "longitude": -122.2348, "address": "Amazon FC, Kent, WA"},
                "sectors": ["logistics", "retail"],
                "assets": ["warehouse", "distribution_center"]
            },
            {
                "source": "news",
                "content": "Flooding at Costco distribution center in Sumner. Ground floor warehousing submerged. Thousands of pallets compromised. Distribution delayed region-wide.",
                "severity": "high",
                "location": {"latitude": 47.2034, "longitude": -122.2401, "address": "Costco DC, Sumner, WA"},
                "sectors": ["logistics", "retail"],
                "assets": ["warehouse", "distribution_center"]
            },
            {
                "source": "corporate",
                "content": "UPS Pacific Northwest hub experiencing power outage. Backup generators failed. Sorting operations suspended. Delivery delays expected for 2-3 days.",
                "severity": "moderate",
                "location": {"latitude": 47.4473, "longitude": -122.3014, "address": "UPS Hub, SeaTac, WA"},
                "sectors": ["logistics"],
                "assets": ["distribution_center", "hub"]
            },
            
            # ENERGY & FUEL DISRUPTIONS
            {
                "source": "emergency_services",
                "content": "Natural gas pipeline rupture in Bellevue. Evacuation zone established. Service interrupted to industrial areas and major warehouses. ETA for repairs unknown.",
                "severity": "high",
                "location": {"latitude": 47.6101, "longitude": -122.2015, "address": "Bellevue, WA"},
                "sectors": ["energy", "utilities"],
                "assets": ["pipeline", "gas_infrastructure"]
            },
            {
                "source": "news",
                "content": "Fuel shortage crisis: Multiple gas stations across Seattle metro reporting empty tanks. Tanker truck drivers strike affecting deliveries.",
                "severity": "high",
                "location": {"latitude": 47.6062, "longitude": -122.3321, "address": "Seattle Metro Area"},
                "sectors": ["energy", "transportation"],
                "assets": ["fuel_station"]
            },
            {
                "source": "corporate",
                "content": "BP refinery in Cherry Point shutting down due to equipment failure. Capacity reduced 40%. Regional fuel supply will be impacted for 2-3 weeks.",
                "severity": "critical",
                "location": {"latitude": 48.8628, "longitude": -122.7572, "address": "BP Refinery, Cherry Point, WA"},
                "sectors": ["energy", "manufacturing"],
                "assets": ["refinery"]
            },
            
            # WEATHER-RELATED DISRUPTIONS
            {
                "source": "weather_service",
                "content": "Severe winter storm warning: Heavy snow and ice expected. State DOT pre-positioning closure equipment. Mountain passes likely to close. Travel not recommended.",
                "severity": "high",
                "location": {"latitude": 47.4239, "longitude": -121.4147, "address": "Snoqualmie Pass, WA"},
                "sectors": ["transportation"],
                "assets": ["highway", "mountain_pass"]
            },
            {
                "source": "twitter",
                "content": "Unprecedented flooding in Duwamish Valley. Water 4-6 feet deep in industrial area. Multiple businesses evacuated. Boeing facilities affected. #SeattleFlood",
                "severity": "critical",
                "location": {"latitude": 47.5216, "longitude": -122.3540, "address": "Duwamish Valley, Seattle, WA"},
                "sectors": ["manufacturing", "transportation"],
                "assets": ["industrial_area"]
            },
            {
                "source": "emergency_services",
                "content": "Wildfire approaching I-90 corridor east of Seattle. Pre-evacuation notices issued. Highway may close if fire spreads. Air quality hazardous.",
                "severity": "high",
                "location": {"latitude": 47.3977, "longitude": -121.5562, "address": "I-90, North Bend, WA"},
                "sectors": ["transportation"],
                "assets": ["highway", "forest"]
            },
            
            # INFRASTRUCTURE FAILURES
            {
                "source": "dot",
                "content": "Critical sinkhole on I-5 near Tacoma. Northbound lanes compromised. Emergency repairs required. Expect extended closure and severe congestion.",
                "severity": "high",
                "location": {"latitude": 47.2529, "longitude": -122.4443, "address": "I-5, Tacoma, WA"},
                "sectors": ["transportation", "infrastructure"],
                "assets": ["highway"]
            },
            {
                "source": "news",
                "content": "Power grid failure affecting east Seattle industrial corridor. Manufacturing plants shut down. Cold storage facilities at risk. Estimated restoration: 12-24 hours.",
                "severity": "high",
                "location": {"latitude": 47.5937, "longitude": -122.2697, "address": "East Seattle, WA"},
                "sectors": ["utilities", "manufacturing"],
                "assets": ["power_grid", "industrial_area"]
            }
        ]
    
    async def fetch_text_signals(
        self,
        count: int = 5,
        sources: Optional[List[str]] = None,
        severity_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch mock text signals.
        
        In production, this would:
        - Query Twitter/X API with disaster-related keywords
        - Poll emergency services data feeds
        - Fetch from news aggregation APIs
        - Query transportation authority feeds
        
        Args:
            count: Number of signals to return
            sources: Filter by source types (e.g., ["twitter", "emergency_services"])
            severity_filter: Filter by severity ("low", "moderate", "high", "critical")
            
        Returns:
            List of TextSignal objects
        """
        # TODO: Replace with real API calls
        # Example integrations:
        # - Twitter API v2: twitter_client.search_recent_tweets(query="disaster OR accident OR emergency", ...)
        # - Emergency Services: emergency_feed_client.get_active_incidents()
        # - News API: news_client.get_everything(q="traffic accident OR closure", ...)
        
        # Filter scenarios
        available_scenarios = self.mock_scenarios
        
        if sources:
            available_scenarios = [
                s for s in available_scenarios
                if s["source"] in sources
            ]
        
        if severity_filter:
            available_scenarios = [
                s for s in available_scenarios
                if s["severity"] == severity_filter
            ]
        
        # Randomly select scenarios
        selected = random.sample(
            available_scenarios,
            min(count, len(available_scenarios))
        )
        
        # Convert to TextSignal format
        signals = []
        for scenario in selected:
            signals.append(self._create_text_signal(scenario))
        
        return signals
    
    def _create_text_signal(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a TextSignal from a scenario.
        
        Matches the TypeScript TextSignal interface from shared-schemas.ts
        """
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(minutes=random.randint(1, 60))
        
        # Map severity to confidence
        confidence_map = {
            "low": 0.5,
            "moderate": 0.7,
            "high": 0.85,
            "critical": 0.95
        }
        
        return {
            "signalId": f"txt-{uuid.uuid4().hex[:12]}",
            "signalType": "text",
            "source": scenario["source"],
            "content": scenario["content"],
            "contentType": "text/plain",
            "language": "en",
            "confidence": confidence_map.get(scenario["severity"], 0.7),
            "location": scenario["location"],
            "createdAt": created_at.isoformat().replace("+00:00", "Z"),
            "receivedAt": now.isoformat().replace("+00:00", "Z"),
            "metadata": {
                "severity_hint": scenario["severity"],
                "sectors_hint": scenario["sectors"],
                "assets_hint": scenario["assets"],
                "mock": True
            }
        }
    
    async def get_live_feed(
        self,
        sources: Optional[List[str]] = None,
        max_age_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get a continuous stream of text signals (mock).
        
        In production, this would establish WebSocket connections
        or long-polling connections to various real-time feeds.
        
        Args:
            sources: List of sources to monitor
            max_age_minutes: Only return signals newer than this
            
        Returns:
            List of recent TextSignal objects
        """
        # TODO: Implement real-time streaming
        # Example:
        # - WebSocket to Twitter Streaming API
        # - WebSocket to emergency services feed
        # - Server-sent events from news APIs
        
        return await self.fetch_text_signals(
            count=random.randint(3, 8),
            sources=sources
        )
    
    def get_supported_sources(self) -> List[str]:
        """Get list of supported text sources."""
        return [
            "twitter",
            "reddit",
            "emergency_services",
            "news",
            "dot",
            "weather_service",
            "corporate"
        ]
