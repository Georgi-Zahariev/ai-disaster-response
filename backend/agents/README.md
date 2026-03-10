# AI Agents

**Responsibility**: AI/ML-powered analysis agents for signal extraction and reasoning.

## Purpose

Agents are specialized AI modules that analyze specific signal types and extract structured observations. Each agent is an expert in its domain.

## Agent Types

### Text Extraction Agent (`text_extraction_agent.py`)
- **Input**: TextSignal (reports, social media, transcripts)
- **Processing**: NLP, entity extraction, sentiment analysis
- **Output**: ExtractedObservation[] with structured information
- **Capabilities**:
  - Named entity recognition (locations, organizations, events)
  - Event type classification
  - Severity assessment from language
  - Affected sector/asset identification

### Vision Analysis Agent (`vision_analysis_agent.py`)
- **Input**: VisionSignal (satellite imagery, photos, video frames)
- **Processing**: Computer vision, object detection
- **Output**: ExtractedObservation[] with visual findings
- **Capabilities**:
  - Damage detection (buildings, infrastructure)
  - Traffic/congestion analysis
  - Crowd density estimation
  - Environmental hazard detection (fire, flood, smoke)

### Quantitative Analysis Agent (`quantitative_analysis_agent.py`)
- **Input**: QuantSignal (sensors, IoT, time-series data)
- **Processing**: Statistical analysis, anomaly detection
- **Output**: ExtractedObservation[] with quantitative findings
- **Capabilities**:
  - Anomaly detection (deviations from normal)
  - Trend analysis
  - Threshold violation detection
  - Correlation with historical patterns

### Disruption Assessment Agent (`disruption_assessment_agent.py`)
- **Input**: FusedEvent
- **Processing**: Impact reasoning, cascading effects analysis
- **Output**: DisruptionAssessment
- **Capabilities**:
  - Supply chain impact modeling
  - Economic impact estimation
  - Population impact assessment
  - Cascading risk identification

## Design Principles

- **Specialized**: Each agent is expert in one domain
- **Stateless**: Agents don't maintain state between calls
- **Observable**: Agents return confidence scores and reasoning
- **Composable**: Agents can be chained or combined
- **LLM-Powered**: Use LLM service for reasoning tasks

⚠️ **Important**: Agents must not call LLM APIs directly - use `llm_service` abstraction.
