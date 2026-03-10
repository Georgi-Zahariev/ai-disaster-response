# Type System Architecture Diagram

## 📋 Type Hierarchy Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DISASTER RESPONSE TYPE SYSTEM                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          INPUT LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │         IncidentInputRequest (API Entry Point)               │ │
│  │  • trace: TraceContext                                       │ │
│  │  • textSignals: TextSignal[]                                 │ │
│  │  • visionSignals: VisionSignal[]                             │ │
│  │  • quantSignals: QuantSignal[]                               │ │
│  │  • options: ProcessingOptions                                │ │
│  └──────────────────────────────────────────────────────────────┘ │
│           │                    │                    │              │
│           ▼                    ▼                    ▼              │
│  ┌──────────────┐    ┌───────────────┐    ┌──────────────┐      │
│  │ TextSignal   │    │ VisionSignal  │    │ QuantSignal  │      │
│  │──────────────│    │───────────────│    │──────────────│      │
│  │ • content    │    │ • mediaUrl    │    │ • value      │      │
│  │ • language   │    │ • mediaType   │    │ • unit       │      │
│  │ • entities   │    │ • detectedObj │    │ • sensorId   │      │
│  │ • sentiment  │    │ • resolution  │    │ • timeSeries │      │
│  └──────────────┘    └───────────────┘    └──────────────┘      │
│           │                    │                    │              │
│           └────────────────────┴────────────────────┘              │
│                              │                                     │
│                    All inherit from RawSignal                      │
│                    All reference SourceDescriptor                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Signals → Observations → Events → Assessments → Alerts            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │            ExtractedObservation (Intermediate)               │ │
│  │  • observationId                                             │ │
│  │  • description                                               │ │
│  │  • sourceSignalIds: string[]                                 │ │
│  │  • confidence: number                                        │ │
│  │  • affectedSectors: SupplyChainSector[]                      │ │
│  │  • affectedAssets: AssetType[]                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              FusedEvent (Primary Output)                     │ │
│  │  • eventId                                                   │ │
│  │  • title, description                                        │ │
│  │  • severity: SeverityLevel                                   │ │
│  │  • location: LocationReference                               │ │
│  │  • timeReference: TimeReference                              │ │
│  │  • observations: ExtractedObservation[]                      │ │
│  │  • affectedSectors: SupplyChainSector[]                      │ │
│  │  • affectedAssets: AssetType[]                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │         DisruptionAssessment (Impact Analysis)               │ │
│  │  • assessmentId                                              │ │
│  │  • eventId (links to FusedEvent)                             │ │
│  │  • disruptionSeverity                                        │ │
│  │  • sectorImpacts[]                                           │ │
│  │  • assetImpacts[]                                            │ │
│  │  • economicImpact                                            │ │
│  │  • populationImpact                                          │ │
│  │  • cascadingEffects[]                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │         AlertRecommendation (Decision Support)               │ │
│  │  • alertId                                                   │ │
│  │  • eventId (links to FusedEvent)                             │ │
│  │  • priority: AlertPriority                                   │ │
│  │  • message                                                   │ │
│  │  • recommendedActions[]                                      │ │
│  │  • resourcesNeeded[]                                         │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     VISUALIZATION LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────┐    ┌─────────────────────────────┐  │
│  │   MapFeaturePayload     │    │   DashboardSummary          │  │
│  │─────────────────────────│    │─────────────────────────────│  │
│  │ • geometry (GeoJSON)    │    │ • situationStatus           │  │
│  │ • properties            │    │ • eventsBySeverity[]        │  │
│  │ • style                 │    │ • sectorDisruptions[]       │  │
│  │ • popupContent          │    │ • alerts breakdown          │  │
│  │ • layer                 │    │ • keyMetrics[]              │  │
│  └─────────────────────────┘    │ • recentSignificantEvents[] │  │
│                                 │ • hotspots[]                │  │
│                                 │ • systemHealth              │  │
│                                 └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │           FinalApiResponse (Complete Output)                 │ │
│  │  • trace: TraceContext                                       │ │
│  │  • status: 'success' | 'partial_success' | 'error'           │ │
│  │  • events: FusedEvent[]                                      │ │
│  │  • disruptions: DisruptionAssessment[]                       │ │
│  │  • alerts: AlertRecommendation[]                             │ │
│  │  • mapFeatures: MapFeaturePayload[]                          │ │
│  │  • dashboardSummary: DashboardSummary                        │ │
│  │  • warnings: Warning[]                                       │ │
│  │  • errors: AppError[]                                        │ │
│  │  • metadata: ProcessingMetadata                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    SUPPORTING TYPES                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │ LocationReference    │  │ TimeReference    │  │ TraceContext ││
│  │──────────────────────│  │──────────────────│  │──────────────││
│  │ • latitude           │  │ • timestamp      │  │ • requestId  ││
│  │ • longitude          │  │ • startTime      │  │ • traceId    ││
│  │ • uncertaintyRadius  │  │ • endTime        │  │ • spanId     ││
│  │ • placeName          │  │ • precision      │  │ • timestamp  ││
│  │ • geometry (GeoJSON) │  │ • confidence     │  │ • userId     ││
│  └──────────────────────┘  └──────────────────┘  └──────────────┘│
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────┐                   │
│  │ SourceDescriptor     │  │ AppError         │                   │
│  │──────────────────────│  │──────────────────│                   │
│  │ • sourceId           │  │ • code           │                   │
│  │ • sourceType         │  │ • message        │                   │
│  │ • sourceName         │  │ • statusCode     │                   │
│  │ • provider           │  │ • details        │                   │
│  │ • reliabilityScore   │  │ • trace          │                   │
│  └──────────────────────┘  └──────────────────┘                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
┌─────────────┐
│   SENSORS   │
│  SATELLITES │  ───┐
│ SOCIAL MEDIA│     │
└─────────────┘     │
                    ▼
         ┌─────────────────────┐
         │  Raw Signals         │
         │  ──────────────      │
         │  • TextSignal        │
         │  • VisionSignal      │
         │  • QuantSignal       │
         └─────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Signal Extraction   │
         │  ─────────────────   │
         │  NLP, CV, Analytics  │
         └─────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ Extracted            │
         │ Observations         │
         └─────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Signal Fusion       │
         │  ─────────────────   │
         │  Multi-modal AI      │
         └─────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Fused Events        │
         └─────────────────────┘
                    │
         ┌──────────┴─────────┐
         │                    │
         ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│   Disruption     │  │      Alert       │
│   Assessment     │  │  Recommendation  │
└──────────────────┘  └──────────────────┘
         │                    │
         └─────────┬──────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   Visualization      │
         │   ───────────────    │
         │   • Map Features     │
         │   • Dashboard        │
         └─────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Final API Response  │
         └─────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Emergency Managers  │
         │  Decision Makers     │
         └─────────────────────┘
```

## 🎯 Type Relationship Matrix

| Type                    | Links To                    | Referenced By           |
|-------------------------|-----------------------------|-------------------------|
| `TextSignal`            | `SourceDescriptor`          | `ExtractedObservation`  |
| `VisionSignal`          | `SourceDescriptor`          | `ExtractedObservation`  |
| `QuantSignal`           | `SourceDescriptor`          | `ExtractedObservation`  |
| `ExtractedObservation`  | `RawSignal` (via IDs)       | `FusedEvent`            |
| `FusedEvent`            | `ExtractedObservation[]`    | `DisruptionAssessment`  |
| `DisruptionAssessment`  | `FusedEvent` (via eventId)  | `AlertRecommendation`   |
| `AlertRecommendation`   | `FusedEvent` (via eventId)  | `FinalApiResponse`      |
| `MapFeaturePayload`     | Any data type (via dataId)  | `FinalApiResponse`      |
| `DashboardSummary`      | Multiple types (aggregated) | `FinalApiResponse`      |
| `FinalApiResponse`      | All output types            | Client applications     |

## 📊 Enumeration Dependencies

```
SupplyChainSector ────────┐
                          │
                          ├─→ ExtractedObservation
                          │
AssetType ────────────────┤     FusedEvent
                          │
                          ├─→ DisruptionAssessment
                          │
SeverityLevel ────────────┘     AlertRecommendation
                          

AlertPriority ─────────────────→ AlertRecommendation


SourceType ─────────────────────→ SourceDescriptor ───→ RawSignal
```

## 🔑 Key Discriminators

### Signal Type Discrimination
```typescript
RawSignal
    └─ signalType: 'text' | 'vision' | 'quantitative'
         │
         ├─ 'text' ────→ TextSignal
         ├─ 'vision' ──→ VisionSignal
         └─ 'quantitative' ──→ QuantSignal
```

### Feature Type Discrimination
```typescript
MapFeaturePayload
    └─ featureType: 'event' | 'disruption' | 'asset' | 'alert' | 'observation'
         │
         └─ dataId: links to respective type instance
```

### Status Discrimination
```typescript
FusedEvent.status: 'active' | 'resolved' | 'monitoring'
AlertRecommendation.status: 'draft' | 'active' | 'acknowledged' | 'resolved' | 'expired'
AssetImpact.status: 'offline' | 'degraded' | 'operational' | 'unknown'
```

## 🌐 Geographic Data Flow

```
LocationReference
    │
    ├─→ Used by all signals (where signal originated)
    │
    ├─→ Used by observations (where observation occurred)
    │
    ├─→ Used by events (primary event location)
    │
    ├─→ Used by alerts (alert area)
    │
    └─→ Converted to GeoJSON for map features
           │
           └─→ MapFeaturePayload.geometry
```

## ⏱️ Temporal Data Flow

```
TimeReference
    │
    ├─→ RawSignal (when signal created/received)
    │
    ├─→ ExtractedObservation (when observation occurred)
    │
    ├─→ FusedEvent (event timeframe)
    │
    └─→ DisruptionAssessment (assessment validity period)
```

## 🔍 Tracing & Observability Flow

```
TraceContext
    │
    ├─→ IncidentInputRequest (request entry)
    │
    ├─→ Propagated through processing pipeline
    │
    ├─→ FinalApiResponse (request completion)
    │
    └─→ AppError (error context)
```

## 💯 Confidence Score Flow

```
Signal Level Confidence
    │
    ├─→ TextSignal.confidence
    ├─→ VisionSignal.confidence
    └─→ QuantSignal.confidence
           │
           ▼
Observation Level Confidence
    │
    └─→ ExtractedObservation.confidence
           │
           ▼
Event Level Confidence
    │
    └─→ FusedEvent.confidence
           │
           ▼
Assessment Level Confidence
    │
    └─→ DisruptionAssessment.confidence
```

## 🏗️ Composition Patterns

### Has-A Relationships
- `FusedEvent` **has** `ExtractedObservation[]`
- `DisruptionAssessment` **has** `sectorImpacts[]` and `assetImpacts[]`
- `DashboardSummary` **has** `recentSignificantEvents[]` and `hotspots[]`
- All signals **have** `SourceDescriptor`
- All geographic entities **have** `LocationReference`

### References-By-ID
- `FusedEvent.sourceSignalIds` → references `RawSignal.signalId`
- `DisruptionAssessment.eventId` → references `FusedEvent.eventId`
- `AlertRecommendation.eventId` → references `FusedEvent.eventId`
- `MapFeaturePayload.dataId` → references any entity ID

## 🔄 Optional vs Required Fields

### Always Required (Core Identity)
- All `*Id` fields (eventId, signalId, assessmentId, etc.)
- `severity` in events and assessments
- `confidence` in events and assessments
- `location` in signals and events
- `timestamp` fields

### Often Optional (Enhancement)
- Extended metadata
- Secondary time references
- Detailed breakdowns
- Related entity IDs
- Display hints and styles

---

This diagram represents the complete type system architecture showing data flow, relationships, and composition patterns across the disaster response system.
