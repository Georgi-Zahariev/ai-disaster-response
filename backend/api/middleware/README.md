# Middleware

**Responsibility**: Cross-cutting concerns that apply to multiple routes.

## Purpose

Middleware handles concerns that span across all or many endpoints:
- Authentication and authorization
- Request/response logging
- Error handling and formatting
- Rate limiting and throttling
- CORS configuration
- Request tracing
- Performance monitoring

## Design Principles

- **Order matters** - Middleware executes in registration order
- **Early exit** - Auth/validation should fail fast
- **Minimal overhead** - Keep middleware fast
- **Observability** - Log key events for debugging

## Common Middleware

- `auth.py` - Authentication and authorization
- `logging.py` - Request/response logging
- `error_handler.py` - Global error handling
- `tracing.py` - Request tracing and correlation IDs
- `rate_limiter.py` - Rate limiting protection
