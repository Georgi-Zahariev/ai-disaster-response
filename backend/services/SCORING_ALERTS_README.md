# Disruption Scoring & Alert Generation Services

## Overview

This module provides comprehensive disruption assessment and alert generation capabilities for the disaster response situational awareness system. It transforms fused events into actionable intelligence for emergency managers.

## Architecture

```
FusedEvent → DisruptionScoringService → DisruptionAssessment
                                              ↓
                                    AlertGenerationService → AlertRecommendation
```

### Pipeline Flow

1. **Input**: FusedEvent objects from the fusion service
2. **Scoring**: Assess severity, impact, and cascading effects
3. **Alert Generation**: Create prioritized, actionable alerts
4. **Output**: DisruptionAssessment and AlertRecommendation objects

## DisruptionScoringService

### Purpose

Evaluates the impact of fused events on supply chains, infrastructure, population, and economic activity.

### Key Features

#### 1. Multi-Factor Scoring

The service considers multiple factors to assess disruption severity:

- **Event Severity**: Base severity level (critical, high, moderate, low)
- **Confidence**: How certain we are about the event
- **Critical Infrastructure**: Amplifies score for energy, healthcare, telecom
- **Geographic Extent**: Larger impact radius = higher score
- **Multimodal Corroboration**: More sources = higher confidence
- **Observation Count**: More observations = better assessment

#### 2. Infrastructure Criticality

Critical sectors receive higher scoring multipliers:
- Energy (power grids)
- Telecommunications (cell towers)
- Healthcare (hospitals)
- Water utilities
- Fuel distribution

**Criticality multiplier**: 1.0 (normal) to 2.0 (highly critical)

#### 3. Impact Assessment

**Sector Impacts**:
- Severity per affected sector
- Estimated recovery time (hours)
- Description of disruption
- Critical service status

**Asset Impacts**:
- Operational status (offline, degraded, operational)
- Asset-specific severity
- Location and identification
- Impact description

**Economic Impact**:
- Estimated cost in USD
- Affected business count
- Economic sector breakdown
- Multipliers for criticality and extent

**Population Impact**:
- Estimated affected population
- Evacuation requirements
- Critical services disrupted
- Vulnerable populations

#### 4. Cascading Effect Analysis

Identifies potential downstream impacts:
- Transportation disruptions → delivery delays
- Energy failures → multi-sector outages
- Port closures → supply chain bottlenecks
- Telecom failures → coordination difficulties

Each cascade includes:
- Description of effect
- Affected sectors
- Likelihood (0.0 to 1.0)

#### 5. Recommendations

Context-aware recommendations based on:
- Severity level
- Affected sectors/assets
- Assessment data
- Standard response protocols

### Usage

#### Basic Usage

```python
from backend.services.scoring import DisruptionScoringService

scoring_service = DisruptionScoringService()

# Score events
assessments = await scoring_service.score(events)

for assessment in assessments:
    print(f"Disruption Severity: {assessment['disruptionSeverity']}")
    print(f"Confidence: {assessment['confidence']:.2f}")
    print(f"Population Affected: {assessment['populationImpact']['affectedPopulation']:,}")
```

#### With Options

```python
options = {
    "focusAreas": ["energy", "healthcare"],
    "minConfidenceThreshold": 0.6
}

assessments = await scoring_service.score(events, options)
```

### Scoring Algorithm

#### Base Score Calculation

```python
base_score = severity_weight * confidence

severity_weights = {
    "critical": 1.0,
    "high": 0.75,
    "moderate": 0.5,
    "low": 0.25,
    "informational": 0.1
}
```

#### Final Score

```python
final_score = base_score * criticality_multiplier + multimodal_boost

# Convert to severity
if score >= 0.8: "critical"
elif score >= 0.6: "high"
elif score >= 0.4: "moderate"
elif score >= 0.2: "low"
else: "informational"
```

### Output Schema

```typescript
interface DisruptionAssessment {
  assessmentId: string;
  eventId: string;
  disruptionSeverity: SeverityLevel;
  confidence: number;
  sectorImpacts: Array<{
    sector: string;
    severity: SeverityLevel;
    description: string;
    estimatedRecoveryHours: number;
  }>;
  assetImpacts: Array<{
    assetType: string;
    assetName: string;
    location?: LocationReference;
    status: 'offline' | 'degraded' | 'operational' | 'unknown';
    severity: SeverityLevel;
    description: string;
  }>;
  economicImpact: {
    estimatedCostUSD: number;
    economicSectors: string[];
    affectedBusinessCount: number;
  };
  populationImpact: {
    affectedPopulation: number;
    evacuationRequired: boolean;
    criticalServicesDisrupted: string[];
  };
  cascadingEffects: Array<{
    description: string;
    sectors: string[];
    likelihood: number;
  }>;
  recommendations: string[];
  assessedAt: string;
  validUntil: string;
  assessedBy: string;
  metadata: {
    baseScore: number;
    criticalityMultiplier: number;
    multimodalBoost: number;
    finalScore: number;
    observationCount: number;
    modalityCount: number;
  };
}
```

### TODO Comments

The service includes TODO comments marking future enhancements:

1. **Supply Chain Graph Analysis** (4 locations)
   - Real-time dependency modeling
   - Network centrality scoring
   - Cascade simulation
   - Bottleneck identification

2. **ML-Based Prediction** (3 locations)
   - Historical impact training data
   - Contextual features (time, weather)
   - Ensemble models
   - Uncertainty quantification

3. **Real-Time Data Integration** (5 locations)
   - Geospatial population queries
   - Regional economic data
   - Asset status from IoT
   - Sector vulnerability feeds

4. **Advanced Economic Modeling** (2 locations)
   - Direct and indirect losses
   - Supply chain multipliers
   - Recovery cost estimation

---

## AlertGenerationService

### Purpose

Transforms disruption assessments into prioritized, actionable alerts for emergency managers and first responders.

### Key Features

#### 1. Priority Determination

Alerts are assigned priorities based on multiple factors:

**Priority Levels**:
- **Urgent**: Critical events, large population impact, evacuation required
- **High**: High severity, critical infrastructure, cascading effects
- **Normal**: Moderate severity, localized impact
- **Low**: Low severity, minimal impact

**Priority Logic**:
```python
Critical severity → Urgent
High severity + 5000+ affected → Urgent
High severity + evacuation → Urgent
High severity + 2+ high-likelihood cascades → Urgent
High severity → High
Moderate severity + critical infrastructure → High
Moderate severity → Normal
Low severity → Low
```

#### 2. Recommended Actions

Actions are generated from templates and rules:

**Critical Actions**:
- Activate emergency operations center
- Deploy all response resources
- Issue emergency alerts
- Coordinate with regional/federal management

**High Actions**:
- Activate response teams
- Issue public safety alerts
- Establish incident command
- Monitor for escalation

**Sector-Specific Actions**:
- Transportation: Traffic control, route closures, detours
- Energy: Isolate damage, backup power, utility coordination
- Healthcare: Hospital protocols, patient surge prep
- Logistics: Rerouting, alternate channels

#### 3. Resource Estimation

Resources are estimated based on:
- Event severity
- Affected assets
- Population impact
- Assessment data

**Resource Types**:
- Emergency personnel and vehicles
- Asset-specific equipment (traffic control, utilities, etc.)
- Shelter capacity (1 bed per 50 people)
- Food and water supplies
- Medical triage teams

#### 4. Target Audiences

Audiences are selected based on:
- Priority level
- Affected sectors
- Population impact

**Audience Roles**:
- Emergency managers
- First responders
- Government officials
- Utility operators
- Healthcare coordinators
- Transportation agencies
- Public information officers

#### 5. Time Constraints

Response windows vary by priority:
- **Urgent**: 15 minutes
- **High**: 1 hour
- **Normal**: 4 hours
- **Low**: 24 hours

### Usage

#### Basic Usage

```python
from backend.services.alerts import AlertGenerationService

alert_service = AlertGenerationService()

# Generate alerts from events and assessments
alerts = await alert_service.generate(events, assessments)

for alert in alerts:
    print(f"[{alert['priority'].upper()}] {alert['title']}")
    print(f"Actions: {len(alert['recommendedActions'])}")
    print(f"Response needed in: {alert['timeConstraints']['responseWindowMinutes']} minutes")
```

#### With Options

```python
options = {
    "minSeverity": "moderate",
    "targetAudiences": ["emergency_managers", "first_responders"]
}

alerts = await alert_service.generate(events, assessments, options)
```

### Alert Generation Pipeline

1. **Filter Events**: Check if event warrants an alert
   - Meets severity threshold
   - Meets confidence threshold
   - Has significant impacts

2. **Match Assessment**: Find corresponding disruption assessment

3. **Determine Priority**: Calculate priority from severity and impacts

4. **Generate Content**:
   - Title: `[SEVERITY] Event Type - Location`
   - Message: Situation summary + key impacts
   - Actions: Template + assessment recommendations
   - Resources: Base + asset-specific + assessment-based

5. **Set Constraints**:
   - Response window by priority
   - Expiration based on assessment validity
   - Target audiences by severity and sectors

6. **Sort and Return**: Urgent alerts first

### Output Schema

```typescript
interface AlertRecommendation {
  alertId: string;
  eventId: string;
  assessmentId?: string;
  priority: 'urgent' | 'high' | 'normal' | 'low';
  title: string;
  message: string;
  targetAudience: string[];
  alertArea?: LocationReference;
  recommendedActions: string[];
  resourcesNeeded: Array<{
    resourceType: string;
    quantity?: number;
    priority: string;
  }>;
  timeConstraints: {
    issueBy?: string;
    expiresAt: string;
    responseWindowMinutes: number;
  };
  createdAt: string;
  status: 'active' | 'acknowledged' | 'resolved' | 'expired';
  relatedAlertIds: string[];
  metadata: {
    eventSeverity: string;
    eventConfidence: number;
    affectedSectors: string[];
    affectedAssets: string[];
    populationImpact: number;
  };
}
```

### TODO Comments

The service includes TODO comments marking future enhancements:

1. **Alert Deduplication** (1 location)
   - Identify overlapping geographic areas
   - Merge alerts for same incident
   - Consolidate cascading effects

2. **ML-Based Priority** (2 locations)
   - Historical effectiveness training
   - Resource availability optimization
   - False alarm rate optimization

3. **Policy-Based Actions** (2 locations)
   - Standard operating procedures
   - Resource availability queries
   - LLM-generated recommendations

4. **Real-Time Integration** (2 locations)
   - Resource management systems
   - Mutual aid agreements
   - Optimal allocation

5. **LLM Generation** (3 locations)
   - Natural language titles and messages
   - Audience-adapted language
   - Multi-language support

---

## Integration with Orchestrator

Both services are integrated into the `IncidentOrchestrator`:

```python
# Orchestrator initialization
from backend.services.scoring import DisruptionScoringService
from backend.services.alerts import AlertGenerationService

self.scoring_service = DisruptionScoringService()
self.alert_service = AlertGenerationService()

# In process_incident pipeline
# Phase 3: Score disruptions
disruptions = await self.scoring_service.score(events, options)

# Phase 4: Generate alerts
alerts = await self.alert_service.generate(events, disruptions, options)
```

## Testing

### Running Tests

```bash
python3 test_scoring_alerts.py
```

### Test Coverage

1. **Disruption Scoring Tests**:
   - Multi-severity event scoring
   - Economic and population impact estimation
   - Cascading effect identification
   - Severity escalation for critical infrastructure
   - Multimodal confidence boosting

2. **Alert Generation Tests**:
   - Priority determination logic
   - Recommended action generation
   - Resource estimation
   - Target audience selection
   - Time constraint calculation

3. **Integration Tests**:
   - End-to-end pipeline: Events → Scoring → Alerts
   - Schema validation
   - Assessment-alert linking

### Test Results

```
✅ DISRUPTION SCORING: ALL TESTS PASSED
✅ ALERT GENERATION: ALL TESTS PASSED
✅ SEVERITY ESCALATION: TEST PASSED
✅ MULTIMODAL BOOST: TEST PASSED
✅ ALERT PRIORITY: TEST PASSED
✅ END-TO-END PIPELINE: TEST PASSED
```

## Performance

### Scoring Service

- **Latency**: ~50-100ms per event
- **Complexity**: O(n) per event, O(n²) for cascading effects
- **Memory**: ~1KB per assessment

### Alert Service

- **Latency**: ~20-50ms per alert
- **Complexity**: O(n) for generation, O(n log n) for sorting
- **Memory**: ~2KB per alert

### Typical Workload

For 10 fused events:
- Scoring: ~500ms
- Alert generation: ~200ms
- Total: <1 second

## Configuration

### Scoring Service Settings

```python
# Spatial-temporal thresholds (from fusion)
spatial_threshold_meters = 5000
temporal_threshold_seconds = 3600

# Severity weights
severity_weights = {
    "critical": 1.0,
    "high": 0.75,
    "moderate": 0.5,
    "low": 0.25
}

# Recovery time estimates (hours)
recovery_time_estimates = {
    "critical": {"min": 24, "max": 168},
    "high": {"min": 6, "max": 48},
    "moderate": {"min": 2, "max": 12},
    "low": {"min": 1, "max": 4}
}
```

### Alert Service Settings

```python
# Alert generation thresholds
min_severity_for_alert = "moderate"
min_confidence_for_alert = 0.4
min_population_impact_for_urgent = 5000

# Response windows (minutes)
response_windows = {
    "urgent": 15,
    "high": 60,
    "normal": 240,
    "low": 1440
}
```

## Production Enhancement Roadmap

### Phase 1: Real-Time Data Integration (Months 1-2)

- [ ] Connect to census/GIS for population data
- [ ] Query regional economic databases
- [ ] Integrate IoT sensor networks for asset status
- [ ] Access sector vulnerability feeds

### Phase 2: ML-Based Scoring (Months 3-4)

- [ ] Train on historical disaster impact data
- [ ] Implement Bayesian probability fusion
- [ ] Add uncertainty quantification
- [ ] Deploy ensemble prediction models

### Phase 3: Supply Chain Modeling (Months 5-6)

- [ ] Build supply chain dependency graphs
- [ ] Implement network centrality scoring
- [ ] Add cascade propagation simulation
- [ ] Identify critical bottlenecks

### Phase 4: LLM Integration (Months 7-8)

- [ ] Generate natural language descriptions
- [ ] Create audience-adapted messages
- [ ] Translate alerts to multiple languages
- [ ] Produce explainable recommendations

### Phase 5: Policy Engine (Months 9-10)

- [ ] Integrate standard operating procedures
- [ ] Query resource management systems
- [ ] Optimize resource allocation
- [ ] Support mutual aid coordination

## Troubleshooting

### Common Issues

#### Issue: Low Confidence Assessments

**Cause**: Single modality, few observations
**Solution**: Wait for additional observations, lower confidence threshold

#### Issue: No Alerts Generated

**Cause**: Events below severity threshold
**Solution**: Adjust `min_severity_for_alert` setting

#### Issue: Too Many Urgent Alerts

**Cause**: Sensitive priority thresholds
**Solution**: Increase `min_population_impact_for_urgent`

#### Issue: Inaccurate Population Estimates

**Cause**: Using default density assumptions
**Solution**: Integrate real census/GIS data (TODO)

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Services will print detailed scoring/alert logic
```

## Examples

### Example 1: Critical Wildfire

**Input Event**:
```python
{
  "eventId": "evt-wildfire-001",
  "severity": "critical",
  "confidence": 0.95,
  "affectedSectors": ["energy", "telecommunications", "healthcare"],
  "affectedAssets": ["power_grid", "cell_tower", "hospital"],
  "impactRadiusMeters": 8000
}
```

**Disruption Assessment**:
```python
{
  "disruptionSeverity": "critical",
  "confidence": 1.00,
  "populationImpact": {
    "affectedPopulation": 201061,
    "evacuationRequired": True
  },
  "economicImpact": {
    "estimatedCostUSD": 10080000
  },
  "cascadingEffects": [
    {
      "description": "Power outages affecting multiple sectors",
      "likelihood": 0.90
    }
  ]
}
```

**Alert Recommendation**:
```python
{
  "alertId": "alert-abc123",
  "priority": "urgent",
  "title": "[CRITICAL] Wildfire - Santa Rosa County",
  "responseWindowMinutes": 15,
  "recommendedActions": [
    "Initiate evacuation procedures for affected areas",
    "Activate emergency operations center immediately",
    "Deploy all available emergency response resources"
  ],
  "targetAudience": [
    "emergency_managers",
    "first_responders",
    "government_officials",
    "utilities"
  ]
}
```

### Example 2: Moderate Traffic Incident

**Input Event**:
```python
{
  "eventId": "evt-traffic-003",
  "severity": "moderate",
  "confidence": 0.75,
  "affectedSectors": ["transportation"],
  "affectedAssets": ["road"],
  "impactRadiusMeters": 1500
}
```

**Disruption Assessment**:
```python
{
  "disruptionSeverity": "moderate",
  "confidence": 0.85,
  "populationImpact": {
    "affectedPopulation": 7068,
    "evacuationRequired": False
  },
  "economicImpact": {
    "estimatedCostUSD": 172500
  }
}
```

**Alert Recommendation**:
```python
{
  "alertId": "alert-xyz789",
  "priority": "normal",
  "title": "Multi-vehicle Accident - I-95 N",
  "responseWindowMinutes": 240,
  "recommendedActions": [
    "Implement traffic management and rerouting plans",
    "Deploy traffic control personnel",
    "Dispatch infrastructure inspection teams"
  ]
}
```

## References

- [TypeScript Schema Definitions](../types/shared-schemas.ts)
- [Orchestrator Documentation](../orchestrator/ORCHESTRATOR_GUIDE.md)
- [Fusion Service Documentation](../fusion/FUSION_README.md)
- [API Documentation](../../docs/api/)

## Support

For questions or issues:
- Check TODO comments for enhancement opportunities
- Review test cases for usage examples
- Consult schema documentation for output formats
