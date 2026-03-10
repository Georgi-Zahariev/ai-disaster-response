# External Data Providers

**Responsibility**: Interface with external data sources and APIs.

## Purpose

Providers abstract external data sources:
- Weather APIs (NOAA, weather.gov, etc.)
- Traffic APIs (Google Maps, Waze, etc.)
- Satellite imagery APIs
- Social media streams
- Government alert systems
- IoT sensor networks

## Design Principles

- **Abstraction**: Hide external API details from domain logic
- **Resilience**: Handle failures gracefully (timeouts, rate limits)
- **Caching**: Cache responses where appropriate
- **Rate Limiting**: Respect provider rate limits
- **Fallback**: Support multiple providers for redundancy

## Provider Types

### Weather Provider (`weather_provider.py`)
- Fetch weather conditions
- Get forecast data
- Check for severe weather alerts
- Used for correlation with disaster events

### Traffic Provider (`traffic_provider.py`)
- Real-time traffic data
- Incident reports
- Road closures
- Used for transportation disruption detection

### Satellite Provider (`satellite_provider.py`)
- Request satellite imagery
- Schedule imaging tasks
- Fetch pre-processed imagery
- Used for visual situation assessment

### Social Media Provider (`social_media_provider.py`)
- Stream social media posts
- Search for keywords/hashtags
- Geolocated posts
- Used for early warning signals

### Alert Provider (`alert_provider.py`)
- Subscribe to government alerts
- Emergency notification systems
- Broadcast alert messages
- Two-way: receive and send alerts

## Error Handling

All providers should:
- Return None or empty results on failure
- Log errors but don't crash
- Implement retry logic with exponential backoff
- Provide circuit breaker protection
- Track availability metrics
