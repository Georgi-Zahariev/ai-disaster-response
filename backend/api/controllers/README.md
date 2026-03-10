# Controllers

**Responsibility**: Request/response handling - translates HTTP requests into service calls.

## Purpose

Controllers are the glue between HTTP routes and domain services:
- Parse and validate request payloads
- Extract authentication context
- Call appropriate services
- Handle service errors and map to HTTP responses
- Format responses according to API contracts

## Design Principles

- **Thin layer** - No business logic, just orchestration
- **Type conversion** - Convert HTTP payloads to domain types
- **Error mapping** - Map service exceptions to HTTP status codes
- **Response formatting** - Ensure consistent API responses

## Naming Convention

Controllers are named after the domain they handle:
- `incident_controller.py` - Incident processing
- `alert_controller.py` - Alert management
- `dashboard_controller.py` - Dashboard and visualization
