"""
Quantitative Feed Provider - Mock implementation.

Provides quantitative/sensor-based signals from various sources:
- Traffic sensors (flow, speed, volume)
- Weather stations (temperature, precipitation, wind)
- Port throughput sensors (container counts, dwell time)
- Fuel level monitors (gas stations, storage facilities)
- Rail counters (freight volume, delays)
- Environmental sensors (air quality, water levels)

In production, this will integrate with:
- WSDOT traffic sensor APIs
- NOAA weather APIs
- Port authority data feeds
- Energy/fuel monitoring systems
- Rail tracking systems
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import random
import uuid


class QuantitativeFeedProvider:
    """
    Mock provider for quantitative/sensor signals.
    
    Simulates various sensor readings that indicate disaster events
    and supply chain disruptions through numerical deviations.
    """
    
    def __init__(self):
        """Initialize the quantitative feed provider."""
        self.mock_scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> List[Dict[str, Any]]:
        """
        Initialize library of mock quantitative scenarios.
        
        Each scenario represents a sensor reading with anomalous
        values indicating a disruption.
        """
        return [
            # TRAFFIC FLOW SENSORS
            {
                "source": "wsdot_traffic_sensor",
                "measurement_type": "traffic_flow",
                "description": "Severe traffic flow reduction indicating major blockage",
                "value": 8,
                "units": "vehicles_per_minute",
                "baseline_value": 45,
                "deviation_score": 0.95,
                "severity": "high",
                "location": {"latitude": 47.6062, "longitude": -122.3321, "address": "I-5 N, Seattle, WA"},
                "sectors": ["transportation"],
                "assets": ["highway"]
            },
            {
                "source": "traffic_loop_detector",
                "measurement_type": "average_speed",
                "description": "Average speed dropped to near-zero indicating complete stoppage",
                "value": 3,
                "units": "mph",
                "baseline_value": 55,
                "deviation_score": 0.98,
                "severity": "critical",
                "location": {"latitude": 47.6543, "longitude": -122.1891, "address": "I-405 S, Kirkland, WA"},
                "sectors": ["transportation"],
                "assets": ["highway"]
            },
            {
                "source": "traffic_count_station",
                "measurement_type": "hourly_volume",
                "description": "Traffic volume spike indicating diversion from primary route",
                "value": 8500,
                "units": "vehicles_per_hour",
                "baseline_value": 3200,
                "deviation_score": 0.87,
                "severity": "moderate",
                "location": {"latitude": 47.5932, "longitude": -122.2788, "address": "I-90 E, Bellevue, WA"},
                "sectors": ["transportation"],
                "assets": ["highway"]
            },
            
            # PORT THROUGHPUT SENSORS
            {
                "source": "port_terminal_system",
                "measurement_type": "container_moves_per_hour",
                "description": "Container processing rate dropped to zero",
                "value": 0,
                "units": "containers_per_hour",
                "baseline_value": 42,
                "deviation_score": 1.0,
                "severity": "critical",
                "location": {"latitude": 47.5768, "longitude": -122.3505, "address": "Port of Seattle, Terminal 5"},
                "sectors": ["transportation", "logistics"],
                "assets": ["port", "terminal"]
            },
            {
                "source": "port_monitoring",
                "measurement_type": "container_dwell_time",
                "description": "Container dwell time increased significantly",
                "value": 8.5,
                "units": "days",
                "baseline_value": 2.1,
                "deviation_score": 0.82,
                "severity": "high",
                "location": {"latitude": 47.5768, "longitude": -122.3505, "address": "Port of Seattle"},
                "sectors": ["logistics"],
                "assets": ["port"]
            },
            {
                "source": "vessel_tracking",
                "measurement_type": "ships_in_queue",
                "description": "Vessel queue length increased dramatically",
                "value": 23,
                "units": "vessels",
                "baseline_value": 4,
                "deviation_score": 0.89,
                "severity": "high",
                "location": {"latitude": 47.6097, "longitude": -122.6319, "address": "Puget Sound"},
                "sectors": ["transportation", "logistics"],
                "assets": ["port", "waterway"]
            },
            
            # RAIL MONITORING
            {
                "source": "rail_counter",
                "measurement_type": "freight_trains_per_day",
                "description": "Rail freight volume dropped to zero",
                "value": 0,
                "units": "trains_per_day",
                "baseline_value": 18,
                "deviation_score": 1.0,
                "severity": "critical",
                "location": {"latitude": 47.9790, "longitude": -122.2021, "address": "BNSF Railway, Everett, WA"},
                "sectors": ["transportation", "logistics"],
                "assets": ["rail", "tracks"]
            },
            {
                "source": "rail_delay_tracker",
                "measurement_type": "average_delay",
                "description": "Freight train delays increased dramatically",
                "value": 12.5,
                "units": "hours",
                "baseline_value": 1.2,
                "deviation_score": 0.91,
                "severity": "high",
                "location": {"latitude": 47.9790, "longitude": -122.2021, "address": "BNSF Railway Network"},
                "sectors": ["transportation", "logistics"],
                "assets": ["rail"]
            },
            
            # FUEL & ENERGY SENSORS
            {
                "source": "fuel_level_monitor",
                "measurement_type": "fuel_inventory",
                "description": "Gas station fuel levels critically low",
                "value": 8,
                "units": "percent",
                "baseline_value": 65,
                "deviation_score": 0.94,
                "severity": "high",
                "location": {"latitude": 47.6062, "longitude": -122.3321, "address": "Seattle Metro Area"},
                "sectors": ["energy", "transportation"],
                "assets": ["fuel_station"]
            },
            {
                "source": "refinery_output_monitor",
                "measurement_type": "daily_production",
                "description": "Refinery production dropped by 40%",
                "value": 60000,
                "units": "barrels_per_day",
                "baseline_value": 100000,
                "deviation_score": 0.88,
                "severity": "high",
                "location": {"latitude": 48.8628, "longitude": -122.7572, "address": "BP Refinery, Cherry Point, WA"},
                "sectors": ["energy", "manufacturing"],
                "assets": ["refinery"]
            },
            {
                "source": "pipeline_pressure_sensor",
                "measurement_type": "pipeline_pressure",
                "description": "Natural gas pipeline pressure dropped suddenly",
                "value": 120,
                "units": "psi",
                "baseline_value": 800,
                "deviation_score": 0.96,
                "severity": "critical",
                "location": {"latitude": 47.6101, "longitude": -122.2015, "address": "Bellevue, WA"},
                "sectors": ["energy", "utilities"],
                "assets": ["pipeline"]
            },
            {
                "source": "power_grid_monitor",
                "measurement_type": "grid_load",
                "description": "Power grid load in industrial area dropped to near zero",
                "value": 15,
                "units": "megawatts",
                "baseline_value": 150,
                "deviation_score": 0.93,
                "severity": "high",
                "location": {"latitude": 47.5937, "longitude": -122.2697, "address": "East Seattle Industrial"},
                "sectors": ["utilities", "manufacturing"],
                "assets": ["power_grid", "industrial_area"]
            },
            
            # WAREHOUSE & DISTRIBUTION SENSORS
            {
                "source": "warehouse_throughput",
                "measurement_type": "packages_per_hour",
                "description": "Package processing stopped completely",
                "value": 0,
                "units": "packages_per_hour",
                "baseline_value": 12000,
                "deviation_score": 1.0,
                "severity": "critical",
                "location": {"latitude": 47.3809, "longitude": -122.2348, "address": "Amazon FC, Kent, WA"},
                "sectors": ["logistics", "retail"],
                "assets": ["warehouse", "distribution_center"]
            },
            {
                "source": "temperature_monitor",
                "measurement_type": "cold_storage_temp",
                "description": "Cold storage temperature rising above safe threshold",
                "value": 45,
                "units": "fahrenheit",
                "baseline_value": 35,
                "deviation_score": 0.79,
                "severity": "moderate",
                "location": {"latitude": 47.2034, "longitude": -122.2401, "address": "Costco DC, Sumner, WA"},
                "sectors": ["logistics", "retail"],
                "assets": ["warehouse", "cold_storage"]
            },
            {
                "source": "inventory_system",
                "measurement_type": "daily_shipments",
                "description": "Outbound shipments reduced by 80%",
                "value": 120,
                "units": "shipments_per_day",
                "baseline_value": 600,
                "deviation_score": 0.86,
                "severity": "high",
                "location": {"latitude": 47.4473, "longitude": -122.3014, "address": "UPS Hub, SeaTac, WA"},
                "sectors": ["logistics"],
                "assets": ["distribution_center", "hub"]
            },
            
            # WEATHER SENSORS
            {
                "source": "weather_station",
                "measurement_type": "precipitation",
                "description": "Extreme precipitation indicating flooding conditions",
                "value": 4.8,
                "units": "inches_per_hour",
                "baseline_value": 0.2,
                "deviation_score": 0.92,
                "severity": "critical",
                "location": {"latitude": 47.5216, "longitude": -122.3540, "address": "Duwamish Valley, Seattle, WA"},
                "sectors": ["transportation", "manufacturing"],
                "assets": ["industrial_area"]
            },
            {
                "source": "snow_depth_sensor",
                "measurement_type": "snow_depth",
                "description": "Rapid snow accumulation on mountain pass",
                "value": 36,
                "units": "inches",
                "baseline_value": 4,
                "deviation_score": 0.89,
                "severity": "high",
                "location": {"latitude": 47.4239, "longitude": -121.4147, "address": "Snoqualmie Pass, WA"},
                "sectors": ["transportation"],
                "assets": ["highway", "mountain_pass"]
            },
            {
                "source": "wind_sensor",
                "measurement_type": "wind_speed",
                "description": "High winds potentially dangerous for high-profile vehicles",
                "value": 65,
                "units": "mph",
                "baseline_value": 12,
                "deviation_score": 0.84,
                "severity": "moderate",
                "location": {"latitude": 47.2529, "longitude": -122.4443, "address": "I-5 Corridor, Tacoma, WA"},
                "sectors": ["transportation"],
                "assets": ["highway"]
            },
            
            # ENVIRONMENTAL SENSORS
            {
                "source": "air_quality_monitor",
                "measurement_type": "aqi",
                "description": "Air quality index hazardous due to wildfire smoke",
                "value": 285,
                "units": "aqi",
                "baseline_value": 45,
                "deviation_score": 0.93,
                "severity": "high",
                "location": {"latitude": 47.3977, "longitude": -121.5562, "address": "I-90 Corridor, North Bend, WA"},
                "sectors": ["transportation"],
                "assets": ["highway"]
            },
            {
                "source": "water_level_sensor",
                "measurement_type": "flood_stage",
                "description": "River at flood stage, industrial area threatened",
                "value": 9.2,
                "units": "feet_above_flood_stage",
                "baseline_value": -2.5,
                "deviation_score": 0.97,
                "severity": "critical",
                "location": {"latitude": 47.5216, "longitude": -122.3540, "address": "Duwamish River, Seattle, WA"},
                "sectors": ["manufacturing", "transportation"],
                "assets": ["industrial_area", "waterway"]
            },
            {
                "source": "seismic_sensor",
                "measurement_type": "shake_intensity",
                "description": "Moderate earthquake detected, infrastructure may be damaged",
                "value": 5.2,
                "units": "magnitude",
                "baseline_value": 0.0,
                "deviation_score": 0.88,
                "severity": "high",
                "location": {"latitude": 47.6062, "longitude": -122.3321, "address": "Seattle, WA"},
                "sectors": ["infrastructure", "transportation"],
                "assets": ["bridge", "highway", "building"]
            },
            
            # SUPPLY CHAIN TIMING
            {
                "source": "delivery_tracking",
                "measurement_type": "average_delivery_delay",
                "description": "Delivery delays increased dramatically across region",
                "value": 18,
                "units": "hours",
                "baseline_value": 2,
                "deviation_score": 0.91,
                "severity": "high",
                "location": {"latitude": 47.6062, "longitude": -122.3321, "address": "Seattle Metro Area"},
                "sectors": ["logistics"],
                "assets": ["distribution_network"]
            },
            {
                "source": "truck_gps_aggregator",
                "measurement_type": "active_trucks",
                "description": "Number of active delivery trucks dropped significantly",
                "value": 45,
                "units": "trucks",
                "baseline_value": 250,
                "deviation_score": 0.86,
                "severity": "high",
                "location": {"latitude": 47.6062, "longitude": -122.3321, "address": "Seattle Metro Area"},
                "sectors": ["logistics", "transportation"],
                "assets": ["fleet"]
            }
        ]
    
    async def fetch_quantitative_signals(
        self,
        count: int = 5,
        sources: Optional[List[str]] = None,
        measurement_types: Optional[List[str]] = None,
        severity_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch mock quantitative signals.
        
        In production, this would:
        - Query WSDOT traffic sensor APIs
        - Poll NOAA weather station data
        - Fetch port authority throughput metrics
        - Query fuel level monitoring systems
        - Access rail tracking data feeds
        
        Args:
            count: Number of signals to return
            sources: Filter by source types
            measurement_types: Filter by measurement types
            severity_filter: Filter by severity
            
        Returns:
            List of QuantSignal objects
        """
        # TODO: Replace with real API calls
        # Example integrations:
        # - WSDOT: wsdot_client.get_traffic_flow(station_id=...)
        # - NOAA: noaa_client.get_weather_observations(station=...)
        # - Port: port_client.get_throughput_metrics(terminal=...)
        # - Energy: fuel_monitor_client.get_inventory_levels(region=...)
        
        # Filter scenarios
        available_scenarios = self.mock_scenarios
        
        if sources:
            available_scenarios = [
                s for s in available_scenarios
                if s["source"] in sources
            ]
        
        if measurement_types:
            available_scenarios = [
                s for s in available_scenarios
                if s["measurement_type"] in measurement_types
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
        
        # Convert to QuantSignal format
        signals = []
        for scenario in selected:
            signals.append(self._create_quantitative_signal(scenario))
        
        return signals
    
    def _create_quantitative_signal(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a QuantSignal from a scenario.
        
        Matches the TypeScript QuantSignal interface from shared-schemas.ts
        """
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(minutes=random.randint(1, 30))
        
        # Map severity to confidence (sensor data is typically high confidence)
        confidence_map = {
            "low": 0.85,
            "moderate": 0.90,
            "high": 0.94,
            "critical": 0.98
        }
        
        return {
            "signalId": f"qnt-{uuid.uuid4().hex[:12]}",
            "signalType": "quantitative",
            "source": scenario["source"],
            "measurementType": scenario["measurement_type"],
            "value": scenario["value"],
            "units": scenario["units"],
            "baselineValue": scenario["baseline_value"],
            "deviationScore": scenario["deviation_score"],
            "confidence": confidence_map.get(scenario["severity"], 0.90),
            "location": scenario["location"],
            "createdAt": created_at.isoformat().replace("+00:00", "Z"),
            "receivedAt": now.isoformat().replace("+00:00", "Z"),
            "metadata": {
                "severity_hint": scenario["severity"],
                "description": scenario["description"],
                "sectors_hint": scenario["sectors"],
                "assets_hint": scenario["assets"],
                "anomaly_type": "deviation",
                "mock": True
            }
        }
    
    async def get_time_series(
        self,
        source: str,
        measurement_type: str,
        location: Dict[str, Any],
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get historical time series data for a sensor (mock).
        
        In production, this would query historical sensor data
        to show trends and patterns over time.
        
        Args:
            source: Sensor source identifier
            measurement_type: Type of measurement
            location: Geographic location
            hours: Number of hours of history to retrieve
            
        Returns:
            List of time series data points
        """
        # TODO: Implement historical data retrieval
        # Example:
        # - time_series_db.query(source, measurement_type, time_range=...)
        # - influxdb_client.query(from=hours_ago, to=now, ...)
        
        # Return mock time series
        time_series = []
        for i in range(hours):
            timestamp = datetime.now(timezone.utc) - timedelta(hours=hours-i)
            
            # Simulate normal values trending toward anomaly
            if i < hours - 2:
                value = 45 + random.uniform(-5, 5)  # Baseline with noise
            else:
                value = 45 - (hours - i) * 15  # Sharp drop
            
            time_series.append({
                "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
                "value": max(0, value),
                "units": "vehicles_per_minute"
            })
        
        return time_series
    
    def get_supported_sources(self) -> List[str]:
        """Get list of supported quantitative sources."""
        return [
            "wsdot_traffic_sensor",
            "traffic_loop_detector",
            "traffic_count_station",
            "port_terminal_system",
            "port_monitoring",
            "vessel_tracking",
            "rail_counter",
            "rail_delay_tracker",
            "fuel_level_monitor",
            "refinery_output_monitor",
            "pipeline_pressure_sensor",
            "power_grid_monitor",
            "warehouse_throughput",
            "temperature_monitor",
            "inventory_system",
            "weather_station",
            "snow_depth_sensor",
            "wind_sensor",
            "air_quality_monitor",
            "water_level_sensor",
            "seismic_sensor",
            "delivery_tracking",
            "truck_gps_aggregator"
        ]
    
    def get_supported_measurement_types(self) -> List[str]:
        """Get list of supported measurement types."""
        return [
            "traffic_flow",
            "average_speed",
            "hourly_volume",
            "container_moves_per_hour",
            "container_dwell_time",
            "ships_in_queue",
            "freight_trains_per_day",
            "average_delay",
            "fuel_inventory",
            "daily_production",
            "pipeline_pressure",
            "grid_load",
            "packages_per_hour",
            "cold_storage_temp",
            "daily_shipments",
            "precipitation",
            "snow_depth",
            "wind_speed",
            "aqi",
            "flood_stage",
            "shake_intensity",
            "average_delivery_delay",
            "active_trucks"
        ]
