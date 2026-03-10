# Services Layer

**Responsibility**: Business logic orchestration and domain operations.

## Purpose

The services layer contains the core business logic of the disaster response system:
- Orchestrate processing pipelines
- Coordinate between agents and providers
- Implement domain rules and workflows
- Manage data transformations
- Handle cross-cutting business concerns

## Design Principles

- **Domain-focused** - Services implement business capabilities
- **Orchestration** - Services coordinate other components
- **Stateless** - Services should be stateless (state in storage/cache)
- **Testable** - Services should be easily unit tested
- **Type-safe** - Use shared TypeScript-equivalent types

## Structure

### `/orchestrator/`
Main processing orchestrator that coordinates the entire incident processing pipeline.
Entry point for processing multimodal signals → fused events → assessments → alerts.

### `/fusion/`
Signal fusion service - combines multiple observations into coherent events.
Implements multimodal fusion algorithms (text + vision + quant → events).

### `/scoring/`
Confidence scoring and quality assessment.
Evaluates reliability of signals, observations, and fused results.

### `/alerts/`
Alert generation and notification service.
Creates actionable recommendations based on disruption assessments.

### Other Services
- Event management
- Storage/persistence
- Query/search
- Notification dispatch
