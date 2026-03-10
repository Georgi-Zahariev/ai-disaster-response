# Utilities

**Responsibility**: Shared utility functions used across the backend.

## Purpose

Common utilities that don't belong to a specific domain:
- String manipulation
- Date/time formatting
- Data validation
- Serialization/deserialization
- ID generation
- Constants

## Design Principles

- **Pure Functions**: Utilities should be stateless
- **Well-Tested**: High test coverage for utilities
- **Documented**: Clear docstrings with examples
- **Reusable**: Generic, not tied to specific use case

## Utility Modules

### `id_generator.py`
Generate unique identifiers:
- Event IDs
- Signal IDs
- Request IDs
- Transaction IDs

### `validators.py`
Data validation functions:
- Coordinate validation
- Confidence score validation
- Timestamp validation
- Data completeness checks

### `formatters.py`
Formatting utilities:
- Timestamp formatting
- Number formatting
- Text truncation
- Pretty printing

### `constants.py`
Application constants:
- Severity levels
- Asset types
- Sector types
- Configuration defaults

### `helpers.py`
Miscellaneous helper functions:
- Safe dict access
- Type conversion
- List operations
- String utilities
