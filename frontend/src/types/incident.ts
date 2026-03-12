/**
 * TypeScript types for Incident Analysis API
 * 
 * These types match the backend response from POST /api/incidents/analyze
 * Based on backend/types/shared-schemas.ts and actual API responses
 * 
 * UI Component Usage:
 * - IncidentForm: IncidentAnalysisRequest
 * - Dashboard: IncidentAnalysisResponse
 * - FusedEventsPanel: FusedEvent[]
 * - AlertsPanel: AlertRecommendation[]
 * - SourcesPanel: (derived from signal metadata)
 * - ActivityLogPanel: (derived from events/alerts)
 * - MapPlaceholder: MapFeaturePayload[]
 * - SummaryCards: DashboardSummary
 */

// ============================================================================
// Re-export shared enums from event.ts
// ============================================================================

export { SeverityLevel, AlertPriority, SupplyChainSector, SourceType } from './event';

// ============================================================================
// Trace Context
// ============================================================================

/**
 * Trace context for request tracking
 * Used in: Request/Response metadata
 */
export interface TraceContext {
  requestId: string;
  traceId?: string | null;
  spanId?: string | null;
  timestamp: string;
  userId?: string | null;
  sessionId?: string | null;
}

// ============================================================================
// Location & Time References
// ============================================================================

/**
 * Geographic location with uncertainty
 * Used in: Events, Observations, Alerts, MapFeatures
 */
export interface LocationReference {
  latitude: number;
  longitude: number;
  uncertainty?: number;
  placeName?: string;
  region?: string;
  address?: string | null;
  locationName?: string | null;
  radiusMeters?: number;
}

/**
 * Time reference with precision
 * Used in: Events, Observations
 */
export interface TimeReference {
  timestamp: string;
  precision?: string;
  startTime?: string;
  endTime?: string;
}

// ============================================================================
// Observations
// ============================================================================

/**
 * Extracted observation from signal analysis
 * Used in: FusedEvent.observations
 */
export interface ExtractedObservation {
  observationId: string;
  observationType: string;
  description: string;
  sourceSignalIds: string[];
  confidence: number;
  location?: LocationReference;
  timeReference?: TimeReference;
  severity?: string;
  affectedSectors?: string[];
  affectedAssets?: string[];
  extractedData?: Record<string, any>;
}

// ============================================================================
// Fused Events
// ============================================================================

/**
 * Fused event from multimodal signal fusion
 * Used in: FusedEventsPanel, MapFeatures
 */
export interface FusedEvent {
  eventId: string;
  eventType: string;
  title: string;
  description: string;
  confidence: number;
  severity: string;
  location: LocationReference;
  timeReference: TimeReference;
  sourceSignalIds: string[];
  observations: ExtractedObservation[];
  affectedSectors: string[];
  affectedAssets: string[];
  impactRadiusMeters?: number;
  status: string;
  detectedAt: string;
  updatedAt: string;
  relatedEventIds?: string[];
  metadata?: Record<string, any>;
}

// ============================================================================
// Disruption Assessment
// ============================================================================

/**
 * Sector impact details
 * Used in: DisruptionAssessment.sectorImpacts
 */
export interface SectorImpact {
  sector: string;
  severity: string;
  description: string;
  estimatedRecoveryHours?: number;
  impactScore?: number;
}

/**
 * Asset impact details
 * Used in: DisruptionAssessment.assetImpacts
 */
export interface AssetImpact {
  assetType: string;
  assetId?: string | null;
  assetName?: string;
  location?: LocationReference;
  status: 'offline' | 'degraded' | 'operational' | 'unknown';
  severity: string;
  description: string;
}

/**
 * Economic impact estimate
 * Used in: DisruptionAssessment.economicImpact
 */
export interface EconomicImpact {
  estimatedCostUSD?: number;
  estimatedLossUSD?: number;
  economicSectors?: string[];
  affectedBusinessCount?: number;
  confidence?: number;
}

/**
 * Population impact details
 * Used in: DisruptionAssessment.populationImpact
 */
export interface PopulationImpact {
  affectedPopulation?: number;
  affectedCount?: number;
  evacuationRequired?: boolean;
  evacuationRecommended?: boolean;
  criticalServicesDisrupted?: string[];
}

/**
 * Cascading effect prediction
 * Used in: DisruptionAssessment.cascadingEffects
 */
export interface CascadingEffect {
  description: string;
  sectors: string[];
  likelihood: number;
}

/**
 * Complete disruption assessment
 * Used in: Dashboard summary, disruption details
 */
export interface DisruptionAssessment {
  assessmentId: string;
  eventId: string;
  disruptionSeverity: string;
  confidence: number;
  sectorImpacts: SectorImpact[];
  assetImpacts: AssetImpact[];
  economicImpact?: EconomicImpact;
  populationImpact?: PopulationImpact;
  cascadingEffects?: CascadingEffect[];
  recommendations?: string[];
  assessedAt: string;
  validUntil?: string;
  assessedBy?: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// Alert Recommendations
// ============================================================================

/**
 * Resource needed for response
 * Used in: AlertRecommendation.resourcesNeeded
 */
export interface ResourceNeeded {
  resourceType: string;
  quantity?: number | null;
  priority: string;
}

/**
 * Time constraints for alert
 * Used in: AlertRecommendation.timeConstraints
 */
export interface TimeConstraints {
  issueBy?: string | null;
  expiresAt?: string;
  responseWindowMinutes?: number;
}

/**
 * Alert recommendation for emergency response
 * Used in: AlertsPanel
 */
export interface AlertRecommendation {
  alertId: string;
  eventId: string;
  assessmentId?: string;
  priority: string;
  title: string;
  message: string;
  targetAudience?: string[];
  alertArea?: LocationReference;
  recommendedActions: string[];
  resourcesNeeded?: ResourceNeeded[];
  timeConstraints?: TimeConstraints;
  createdAt: string;
  status: string;
  relatedAlertIds?: string[];
  metadata?: Record<string, any>;
}

// ============================================================================
// Map Features
// ============================================================================

/**
 * GeoJSON geometry
 * Used in: MapFeaturePayload.geometry
 */
export interface GeoJSONGeometry {
  type: 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon';
  coordinates: number[] | number[][] | number[][][];
}

/**
 * Map feature properties
 * Used in: MapFeaturePayload.properties
 */
export interface MapFeatureProperties {
  title: string;
  description?: string;
  severity?: string;
  priority?: string;
  status?: string;
  color?: string;
  icon?: string;
}

/**
 * Map feature styling
 * Used in: MapFeaturePayload.style
 */
export interface MapFeatureStyle {
  fillColor?: string;
  strokeColor?: string;
  strokeWidth?: number;
  opacity?: number;
  iconUrl?: string;
  iconSize?: [number, number];
}

/**
 * Map feature for visualization
 * Used in: MapPlaceholder component
 */
export interface MapFeaturePayload {
  featureId: string;
  featureType: 'event' | 'disruption' | 'asset' | 'alert' | 'observation';
  dataId: string;
  geometry: GeoJSONGeometry;
  properties: MapFeatureProperties;
  style?: MapFeatureStyle;
  layer: string;
  zIndex?: number;
  visible?: boolean;
  timestamp: string;
  popupContent?: string;
}

// ============================================================================
// Dashboard Summary
// ============================================================================

/**
 * Time window for dashboard data
 * Used in: DashboardSummary.timeWindow
 */
export interface TimeWindow {
  startTime: string;
  endTime: string;
}

/**
 * Overall situation status
 * Used in: DashboardSummary.situationStatus, SummaryCards
 */
export interface SituationStatus {
  overallSeverity: string;
  activeEventsCount: number;
  criticalAlertsCount: number;
  affectedRegions: string[];
}

/**
 * Event count by severity
 * Used in: DashboardSummary.eventsBySeverity
 */
export interface EventsBySeverity {
  severity: string;
  count: number;
  trend?: 'increasing' | 'decreasing' | 'stable';
}

/**
 * Sector disruption summary
 * Used in: DashboardSummary.sectorDisruptions
 */
export interface SectorDisruptionSummary {
  sector: string;
  severity: string;
  affectedAssetsCount: number;
  description?: string;
}

/**
 * Alert counts by priority
 * Used in: DashboardSummary.alerts, SummaryCards
 */
export interface AlertCounts {
  urgent: number;
  high: number;
  normal: number;
  low: number;
}

/**
 * Key metric for dashboard
 * Used in: DashboardSummary.keyMetrics, SummaryCards
 */
export interface KeyMetric {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  changePercent?: number;
}

/**
 * Recent significant event summary
 * Used in: DashboardSummary.recentSignificantEvents
 */
export interface RecentEvent {
  eventId: string;
  title: string;
  severity: string;
  timestamp: string;
}

/**
 * Geographic hotspot
 * Used in: DashboardSummary.hotspots, MapPlaceholder
 */
export interface Hotspot {
  location: LocationReference & {
    region?: string;
  };
  eventCount: number;
  highestSeverity: string;
}

/**
 * Complete dashboard summary
 * Used in: SummaryCards, Dashboard overview
 */
export interface DashboardSummary {
  generatedAt: string;
  timeWindow: TimeWindow;
  situationStatus: SituationStatus;
  eventsBySeverity: EventsBySeverity[];
  sectorDisruptions: SectorDisruptionSummary[];
  alerts: AlertCounts;
  keyMetrics: KeyMetric[];
  recentSignificantEvents: RecentEvent[];
  hotspots?: Hotspot[];
  systemHealth?: {
    signalsProcessedCount: number;
    averageProcessingLatencyMs?: number;
    dataQuality?: number;
    warnings?: string[];
  };
}

// ============================================================================
// Warnings & Errors
// ============================================================================

/**
 * Warning message
 * Used in: Response.warnings
 */
export interface Warning {
  code: string;
  message: string;
  severity: 'low' | 'medium' | 'high';
}

/**
 * Error message
 * Used in: Response.errors
 */
export interface ErrorMessage {
  code: string;
  message: string;
  statusCode?: number;
  details?: Record<string, any>;
  timestamp?: string;
  trace?: TraceContext;
}

// ============================================================================
// Processing Metadata
// ============================================================================

/**
 * Processing metadata
 * Used in: Response.metadata
 */
export interface ProcessingMetadata {
  signalsProcessed: number;
  observationsExtracted: number;
  eventsCreated: number;
  disruptionsAssessed: number;
  alertsGenerated: number;
  pipeline: string;
  version: string;
  modelVersions?: Record<string, string>;
}

// ============================================================================
// Main Request/Response Types
// ============================================================================

/**
 * Incident analysis request
 * Used in: IncidentForm submission
 */
export interface IncidentAnalysisRequest {
  trace: TraceContext;
  textSignals?: any[];
  visionSignals?: any[];
  quantSignals?: any[];
  options?: {
    enableFusion?: boolean;
    enableDisruptionAssessment?: boolean;
    enableAlertGeneration?: boolean;
    minConfidenceThreshold?: number;
    geographicBounds?: LocationReference;
    timeWindow?: TimeWindow;
    focusSectors?: string[];
  };
  requestor?: {
    userId?: string;
    organization?: string;
    role?: string;
  };
}

/**
 * Complete incident analysis response
 * Used in: Dashboard main state, all panels
 */
export interface IncidentAnalysisResponse {
  trace: TraceContext;
  status: 'success' | 'partial_success' | 'error';
  processedAt: string;
  processingDurationMs: number;
  events: FusedEvent[];
  disruptions: DisruptionAssessment[];
  alerts: AlertRecommendation[];
  mapFeatures: MapFeaturePayload[];
  dashboardSummary?: DashboardSummary;
  warnings?: Warning[];
  errors?: ErrorMessage[];
  metadata?: ProcessingMetadata;
}

// ============================================================================
// Simplified Request Helper (for simple text incident input)
// ============================================================================

/**
 * Simplified incident input from form
 * Used in: IncidentForm component
 */
export interface SimpleIncidentInput {
  description: string;
  location?: string;
}

/**
 * Helper to convert SimpleIncidentInput to full IncidentAnalysisRequest
 */
export function createIncidentRequest(
  input: SimpleIncidentInput,
  requestId?: string
): IncidentAnalysisRequest {
  return {
    trace: {
      requestId: requestId || `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
    },
    textSignals: [
      {
        signalId: `text-${Date.now()}`,
        sourceType: 'human_report',
        collectedAt: new Date().toISOString(),
        rawText: input.description,
        language: 'en',
        ...(input.location && {
          location: {
            placeName: input.location,
          },
        }),
        confidence: 0.9,
      },
    ],
    options: {
      enableFusion: true,
      enableDisruptionAssessment: true,
      enableAlertGeneration: true,
      minConfidenceThreshold: 0.5,
    },
  };
}
