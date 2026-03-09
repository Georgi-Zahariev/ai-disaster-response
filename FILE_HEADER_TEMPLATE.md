# File Header Template

Every source file in this repository must begin with a header comment that follows this standard template.

---

## Standard Template

### Python Files
```python
"""
File: filename.py
Purpose: Brief description of what this file does
Inputs: What data/parameters this file/module expects
Outputs: What this file/module produces or returns
Dependencies: Key imports or external dependencies
Used By: Which modules or components use this file
"""
```

### JavaScript/TypeScript Files
```javascript
/**
 * File: filename.js
 * Purpose: Brief description of what this file does
 * Inputs: What data/parameters this file/module expects
 * Outputs: What this file/module produces or returns
 * Dependencies: Key imports or external dependencies
 * Used By: Which modules or components use this file
 */
```

---

## Field Definitions

### File
The filename including extension (e.g., `llm_service.py`, `Dashboard.jsx`)

### Purpose
A concise 1-2 sentence description of what this file does and why it exists.

**Examples:**
- "Provides abstraction layer for all LLM API interactions"
- "Analyzes disaster events and generates response recommendations"
- "Handles API endpoints for disaster event management"

### Inputs
What this file expects to receive. Can include:
- Function parameters
- API request data
- Environment variables
- Data from other modules

**Examples:**
- "DisasterEvent model, analysis parameters"
- "HTTP requests with event data"
- "OPENAI_API_KEY from environment"

### Outputs
What this file produces or returns. Can include:
- Return values
- API responses
- Side effects (database writes, API calls)
- Rendered UI components

**Examples:**
- "AnalysisResult model with recommendations"
- "JSON responses with event data"
- "React component rendering event dashboard"

### Dependencies
Key external dependencies or internal imports this file relies on.

**List libraries, frameworks, or key internal modules:**
- External: `openai`, `fastapi`, `react`, `pydantic`
- Internal: `services.llm_service`, `models.disaster_event`, `config`

### Used By
Which parts of the system use or depend on this file.

**Examples:**
- "agents/, backend/api/"
- "DisasterAnalyzer agent, ResponsePlanner agent"
- "Dashboard component, EventList component"

---

## Complete Examples

### Example 1: Service File

**File:** `services/llm_service.py`

```python
"""
File: llm_service.py
Purpose: Provides abstraction layer for all LLM API interactions including OpenAI and Anthropic
Inputs: Prompts (str), configuration from config module, optional model parameters
Outputs: LLM responses (str or structured data), token usage metrics
Dependencies: openai, anthropic, config, logging
Used By: agents/disaster_analyzer.py, agents/response_planner.py, services/disaster_service.py
"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Large Language Models."""
    
    @staticmethod
    def generate(prompt: str, model: str = "gpt-4") -> str:
        """
        Generate text response from LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            model: Model identifier (default: gpt-4)
            
        Returns:
            str: Generated response from the LLM
        """
        logger.info(f"Generating LLM response with model: {model}")
        
        try:
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise
```

---

### Example 2: Agent File

**File:** `agents/disaster_analyzer.py`

```python
"""
File: disaster_analyzer.py
Purpose: Analyzes disaster events using AI to assess severity and generate recommendations
Inputs: DisasterEvent model with event details (type, location, description)
Outputs: AnalysisResult model containing severity score, recommendations, and risk factors
Dependencies: services.llm_service, models.disaster_event, models.analysis_result, logging
Used By: services/disaster_service.py, backend/api/routes/analysis.py
"""

import logging
from typing import Dict, Any
from services.llm_service import LLMService
from models.disaster_event import DisasterEvent
from models.analysis_result import AnalysisResult

logger = logging.getLogger(__name__)


class DisasterAnalyzer:
    """Agent for analyzing disaster events using AI."""
    
    @staticmethod
    def analyze(event: DisasterEvent) -> AnalysisResult:
        """
        Analyze a disaster event and generate recommendations.
        
        Args:
            event: DisasterEvent model with event details
            
        Returns:
            AnalysisResult: Analysis with severity, recommendations, and risk factors
        """
        logger.info(f"Analyzing disaster event: {event.event_id}")
        
        # Build analysis prompt
        prompt = f"""Analyze this disaster event:
Type: {event.type}
Location: {event.location}
Description: {event.description}

Provide severity assessment and key recommendations."""
        
        # Get LLM analysis
        try:
            response = LLMService.generate(prompt)
            
            # Parse response into structured result
            # TODO: Implement structured parsing
            return AnalysisResult(
                event_id=event.event_id,
                severity=8,  # Placeholder
                recommendations=response,
                risk_factors=[]
            )
        except Exception as e:
            logger.error(f"Analysis failed for event {event.event_id}: {str(e)}")
            raise
```

---

### Example 3: API Route File

**File:** `backend/api/routes/events.py`

```python
"""
File: events.py
Purpose: Handles REST API endpoints for disaster event management (CRUD operations)
Inputs: HTTP requests with event data, query parameters for filtering
Outputs: JSON responses with event data or operation results
Dependencies: fastapi, services.disaster_service, models.disaster_event, logging
Used By: Frontend application, external API consumers
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from services.disaster_service import DisasterService
from models.disaster_event import DisasterEvent, DisasterEventCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/", response_model=List[DisasterEvent])
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get list of disaster events with optional filtering.
    
    Args:
        event_type: Optional filter by disaster type
        limit: Maximum number of events to return
        
    Returns:
        List of DisasterEvent objects
    """
    logger.info(f"Fetching events (type={event_type}, limit={limit})")
    
    try:
        events = DisasterService.get_events(
            event_type=event_type,
            limit=limit
        )
        return events
    except Exception as e:
        logger.error(f"Failed to fetch events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")


@router.post("/", response_model=DisasterEvent, status_code=201)
async def create_event(event: DisasterEventCreate):
    """
    Create a new disaster event.
    
    Args:
        event: DisasterEventCreate model with event details
        
    Returns:
        Created DisasterEvent object
    """
    logger.info(f"Creating new event: {event.type}")
    
    try:
        new_event = DisasterService.create_event(event)
        return new_event
    except ValueError as e:
        logger.warning(f"Invalid event data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create event")
```

---

### Example 4: Frontend Component

**File:** `frontend/src/components/EventDashboard.jsx`

```javascript
/**
 * File: EventDashboard.jsx
 * Purpose: Main dashboard component displaying disaster events and real-time updates
 * Inputs: Event data from API via EventService, user filters and preferences
 * Outputs: Rendered dashboard UI with event list, map view, and statistics
 * Dependencies: React, EventService, MapComponent, EventCard, hooks/useEvents
 * Used By: pages/Dashboard.jsx, App.jsx
 */

import React, { useState, useEffect } from 'react';
import { useEvents } from '../hooks/useEvents';
import EventService from '../services/EventService';
import MapComponent from './MapComponent';
import EventCard from './EventCard';
import './EventDashboard.css';

/**
 * EventDashboard component
 * 
 * Displays a comprehensive view of disaster events including:
 * - Event list with filters
 * - Geographic map view
 * - Summary statistics
 * - Real-time updates
 */
const EventDashboard = () => {
  const [filters, setFilters] = useState({ type: null, severity: null });
  const { events, loading, error, refetch } = useEvents(filters);

  useEffect(() => {
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      refetch();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [refetch]);

  if (loading) {
    return <div className="loading">Loading events...</div>;
  }

  if (error) {
    return <div className="error">Failed to load events: {error.message}</div>;
  }

  return (
    <div className="event-dashboard">
      <header className="dashboard-header">
        <h1>Disaster Response Dashboard</h1>
        <div className="event-count">
          Active Events: {events.length}
        </div>
      </header>

      <div className="dashboard-content">
        <div className="map-section">
          <MapComponent events={events} />
        </div>

        <div className="event-list">
          {events.map(event => (
            <EventCard key={event.event_id} event={event} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default EventDashboard;
```

---

## Usage Guidelines

### When to Include Each Field

**Always include:**
- File
- Purpose
- Dependencies

**Include when applicable:**
- Inputs (if file processes data)
- Outputs (if file produces results)
- Used By (if known at creation time)

### Tips for Writing Good Headers

1. **Be concise**: Keep each field to 1-2 lines
2. **Be specific**: Mention actual model/component names
3. **Be honest**: Use "TODO" or "TBD" if details aren't clear yet
4. **Update as needed**: Headers should evolve with the code
5. **Think about readers**: Write for someone unfamiliar with the code

### Special Cases

**For utility files:**
```python
"""
File: helpers.py
Purpose: Common helper functions for data formatting and validation
Inputs: Various data types depending on function
Outputs: Formatted or validated data
Dependencies: datetime, typing, re
Used By: All modules (widely shared utilities)
"""
```

**For configuration files:**
```python
"""
File: config.py
Purpose: Load and validate application configuration from environment variables
Inputs: Environment variables (OPENAI_API_KEY, DATABASE_URL, etc.)
Outputs: Config object with validated settings
Dependencies: os, typing, pydantic
Used By: All modules requiring configuration
"""
```

**For test files:**
```python
"""
File: test_disaster_service.py
Purpose: Unit tests for DisasterService functionality
Inputs: Test fixtures and mock data
Outputs: Test results (pass/fail)
Dependencies: pytest, services.disaster_service, fixtures
Used By: Test suite (pytest)
"""
```

---

## Implementation Checklist

Before committing a new file, verify:

- [ ] Header comment is present at the top of the file
- [ ] All required fields are filled in
- [ ] Purpose clearly explains what the file does
- [ ] Dependencies list key imports
- [ ] Header uses correct comment syntax for the language
- [ ] Information is accurate and up-to-date

---

## For AI Assistants

When generating new files:

1. **Always start with the header template**
2. **Fill in all applicable fields** based on the code context
3. **Be specific** about models, services, and dependencies
4. **Reference REPO_MAP.md** to understand "Used By" relationships
5. **Update headers** when making significant changes to existing files

The header helps AI tools understand:
- File purpose and responsibility
- Data flow (inputs/outputs)
- Module relationships
- Where it fits in the architecture

---

**Questions?**

If you're unsure how to fill in a field:
1. Look at similar files in the repository
2. Reference REPO_MAP.md for module relationships
3. Use "TODO" or "TBD" as a placeholder
4. Update the header as the code evolves

---

*Last Updated: March 9, 2026*
