# Alert Generation Service

**Responsibility**: Generate actionable alert recommendations from disruption assessments.

## Purpose

The alert service creates prioritized, actionable recommendations for emergency managers:
- Determines alert priority (urgent, high, normal, low)
- Drafts alert messages
- Identifies recommended actions
- Estimates resource requirements
- Sets time constraints

## Alert Generation Logic

### Priority Determination

Priority is based on:
- **Severity**: Critical events → urgent alerts
- **Population Impact**: Large populations → higher priority
- **Time Sensitivity**: Rapidly evolving → urgent
- **Supply Chain Criticality**: Key infrastructure → higher priority

Priority levels:
- **URGENT**: Immediate action required, life-threatening
- **HIGH**: Timely action needed, significant impact
- **NORMAL**: Standard response, moderate impact
- **LOW**: Informational, minor impact

### Recommended Actions

Actions are specific and contextual:
- "Evacuate residents within 2km radius"
- "Close Highway 101 between exits 42-45"
- "Deploy emergency medical teams to coordinates"
- "Activate backup water supply systems"

### Resource Requirements

Identify needed resources:
- Personnel (firefighters, medical, law enforcement)
- Equipment (generators, water trucks, rescue tools)
- Supplies (food, water, medical, shelter)
- Coordination (incident command, communications)

### Target Audiences

Alerts are directed to:
- Emergency managers
- First responders
- Government agencies
- Public (via broadcast systems)
- Supply chain operators

## Output

Produces AlertRecommendation objects with:
- Priority level
- Clear title and message
- List of recommended actions
- Resource requirements
- Time constraints
- Target audiences
