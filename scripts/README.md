# Scripts Folder

## Purpose
Development and deployment scripts

## What Belongs Here
- Database initialization
- Data seeding scripts
- Deployment automation
- Maintenance tasks
- Development utilities

## Example Scripts
```python
# init_db.py
def init_database():
    """Initialize database schema."""
    # Create tables, run migrations
    pass

# seed_data.py  
def seed_test_data():
    """Load test data for development."""
    # Insert sample events
    pass
```

## Usage
```bash
python scripts/init_db.py
python scripts/seed_data.py
```

## What Does NOT Belong Here
- Application code (use appropriate modules)
- Tests (use `tests/`)
- Configuration (use `config/`)

## Guidelines
- Make scripts idempotent
- Add error handling
- Include helpful output
- Document requirements
