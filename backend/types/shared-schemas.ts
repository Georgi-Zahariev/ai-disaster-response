/**
 * Shared TypeScript Schemas for Multimodal Disaster Response System
 * 
 * This module defines production-ready, implementation-agnostic types for:
 * - Multimodal signal ingestion (text, vision, quantitative sensors)
 * - Signal fusion and event detection
 * - Disruption assessment and alerting
 * - Dashboard and map visualization outputs
 * 
 * These types power the supply chain disruption detection and situational
 * awareness capabilities during disaster events.
 */

// ============================================================================
// Core Enumerations
// ============================================================================

/**
 * Source types for incoming signals
 */
export enum SourceType {
  TEXT = 'text',
  VISION = 'vision',
  QUANTITATIVE = 'quantitative',
  SOCIAL_MEDIA = 'social_media',
  SENSOR_NETWORK = 'sensor_network',
  SATELLITE = 'satellite',
  HUMAN_REPORT = 'human_report',
  API_FEED = 'api_feed',
}

/**
 * Severity levels for events and disruptions
 */
export enum SeverityLevel {
  CRITICAL = 'critical',
  HIGH = 'high',
  MODERATE = 'moderate',
  LOW = 'low',
  INFORMATIONAL = 'informational',
}

/**
 * Supply chain sectors that may be affected
 */
export enum SupplyChainSector {
  TRANSPORTATION = 'transportation',
  LOGISTICS = 'logistics',
  WAREHOUSING = 'warehousing',
  MANUFACTURING = 'manufacturing',
  ENERGY = 'energy',
  TELECOMMUNICATIONS = 'telecommunications',
  WATER_UTILITIES = 'water_utilities',
  HEALTHCARE = 'healthcare',
  FOOD_SUPPLY = 'food_supply',
  RETAIL = 'retail',
  FUEL_DISTRIBUTION = 'fuel_distribution',
}

/**
 * Types of supply chain assets that can be disrupted
 */
export enum AssetType {
  ROAD = 'road',
  BRIDGE = 'bridge',
  PORT = 'port',
  AIRPORT = 'airport',
  RAIL_LINE = 'rail_line',
  WAREHOUSE = 'warehouse',
  DISTRIBUTION_CENTER = 'distribution_center',
  POWER_GRID = 'power_grid',
  CELL_TOWER = 'cell_tower',
  WATER_TREATMENT = 'water_treatment',
  FUEL_DEPOT = 'fuel_depot',
  HOSPITAL = 'hospital',
  EVACUATION_ROUTE = 'evacuation_route',
}

/**
 * Alert priority levels
 */
export enum AlertPriority {
  URGENT = 'urgent',
  HIGH = 'high',
  NORMAL = 'normal',
  LOW = 'low',
}

// ============================================================================
// Tracing and Error Handling
// ============================================================================

/**
 * Trace context for request tracking and debugging
 */
export interface TraceContext {
  /** Unique request identifier */
  requestId: string;
  
  /** Parent span ID for distributed tracing */
  spanId?: string;
  
  /** Trace ID for end-to-end tracking */
  traceId?: string;
  
  /** Timestamp when request was initiated (ISO 8601) */
  timestamp: string;
  
  /** Originating user or system identifier */
  userId?: string;
  
  /** Session identifier for multi-request workflows */
  sessionId?: string;
}

/**
 * Standardized error response
 */
export interface AppError {
  /** Error code for programmatic handling */
  code: string;
  
  /** Human-readable error message */
  message: string;
  
  /** HTTP status code */
  statusCode: number;
  
  /** Additional error details */
  details?: Record<string, any>;
  
  /** Stack trace (only in development) */
  stack?: string;
  
  /** Timestamp when error occurred (ISO 8601) */
  timestamp: string;
  
  /** Request trace context */
  trace?: TraceContext;
}

// ============================================================================
// Geospatial and Temporal References
// ============================================================================

/**
 * Geographic location reference with uncertainty bounds
 */
export interface LocationReference {
  /** Latitude in decimal degrees */
  latitude: number;
  
  /** Longitude in decimal degrees */
  longitude: number;
  
  /** Optional elevation in meters */
  elevation?: number;
  
  /** Location uncertainty radius in meters */
  uncertaintyRadiusMeters?: number;
  
  /** Human-readable place name or address */
  placeName?: string;
  
  /** Geographic region or administrative area */
  region?: string;
  
  /** Country code (ISO 3166-1 alpha-2) */
  countryCode?: string;
  
  /** GeoJSON geometry for complex shapes */
  geometry?: GeoJSONGeometry;
}

/**
 * Time reference with precision and uncertainty
 */
export interface TimeReference {
  /** Timestamp (ISO 8601) */
  timestamp: string;
  
  /** Start of time range if applicable (ISO 8601) */
  startTime?: string;
  
  /** End of time range if applicable (ISO 8601) */
  endTime?: string;
  
  /** Time precision (e.g., 'minute', 'hour', 'day') */
  precision?: string;
  
  /** Timezone (IANA timezone name) */
  timezone?: string;
  
  /** Confidence in time accuracy (0.0 to 1.0) */
  confidence?: number;
}

/**
 * GeoJSON geometry (simplified, supports common types)
 */
export type GeoJSONGeometry = {
  type: 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon';
  coordinates: number[] | number[][] | number[][][];
};

// ============================================================================
// Source Descriptors
// ============================================================================

/**
 * Metadata describing the source of a signal
 */
export interface SourceDescriptor {
  /** Unique identifier for this source */
  sourceId: string;
  
  /** Type of source */
  sourceType: SourceType;
  
  /** Human-readable source name */
  sourceName?: string;
  
  /** Organization or entity providing the source */
  provider?: string;
  
  /** URL or API endpoint where source was obtained */
  sourceUrl?: string;
  
  /** Reliability score for this source (0.0 to 1.0) */
  reliabilityScore?: number;
  
  /** Historical accuracy metrics */
  metadata?: Record<string, any>;
}

// ============================================================================
// Raw Signals (Multimodal Inputs)
// ============================================================================

/**
 * Base interface for all raw signals
 */
export interface RawSignal {
  /** Unique signal identifier */
  signalId: string;
  
  /** Type of signal */
  signalType: 'text' | 'vision' | 'quantitative';
  
  /** Source descriptor */
  source: SourceDescriptor;
  
  /** When signal was received by system (ISO 8601) */
  receivedAt: string;
  
  /** When signal was originally created (ISO 8601) */
  createdAt: string;
  
  /** Location where signal originated */
  location?: LocationReference;
  
  /** Time reference for the observation */
  timeReference?: TimeReference;
  
  /** Raw signal confidence (0.0 to 1.0) */
  confidence?: number;
  
  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Text-based signal (reports, social media, transcripts)
 */
export interface TextSignal extends RawSignal {
  signalType: 'text';
  
  /** Raw text content */
  content: string;
  
  /** Language code (ISO 639-1) */
  language?: string;
  
  /** Whether text was machine-translated */
  translated?: boolean;
  
  /** Original language if translated */
  originalLanguage?: string;
  
  /** Detected entities (places, organizations, etc.) */
  entities?: Array<{
    text: string;
    type: string;
    confidence: number;
  }>;
  
  /** Sentiment score (-1.0 to 1.0) */
  sentiment?: number;
}

/**
 * Vision-based signal (satellite imagery, camera feeds, photos)
 */
export interface VisionSignal extends RawSignal {
  signalType: 'vision';
  
  /** URL or path to image/video */
  mediaUrl: string;
  
  /** Media type (image/jpeg, video/mp4, etc.) */
  mediaType: string;
  
  /** Image resolution (width x height) */
  resolution?: { width: number; height: number };
  
  /** Camera or sensor specifications */
  sensorInfo?: {
    model?: string;
    fov?: number;
    altitude?: number;
  };
  
  /** Pre-computed image features or embeddings */
  features?: number[];
  
  /** Detected objects in the image */
  detectedObjects?: Array<{
    label: string;
    confidence: number;
    boundingBox?: { x: number; y: number; width: number; height: number };
  }>;
  
  /** Image caption or description */
  caption?: string;
}

/**
 * Quantitative sensor signal (IoT, weather, seismic)
 */
export interface QuantSignal extends RawSignal {
  signalType: 'quantitative';
  
  /** Measurement type (temperature, pressure, flow, etc.) */
  measurementType: string;
  
  /** Measured value */
  value: number;
  
  /** Unit of measurement */
  unit: string;
  
  /** Sensor identifier */
  sensorId?: string;
  
  /** Statistical aggregation if applicable */
  aggregation?: {
    method: 'mean' | 'sum' | 'max' | 'min' | 'count';
    windowSeconds: number;
    sampleCount: number;
  };
  
  /** Normal operating range for comparison */
  normalRange?: {
    min: number;
    max: number;
  };
  
  /** Deviation from normal (if applicable) */
  deviationScore?: number;
  
  /** Related measurements in time series */
  timeSeries?: Array<{
    timestamp: string;
    value: number;
  }>;
}

// ============================================================================
// Processed Observations
// ============================================================================

/**
 * Extracted observation from fused signal analysis
 */
export interface ExtractedObservation {
  /** Unique observation identifier */
  observationId: string;
  
  /** Type of observation */
  observationType: string;
  
  /** Brief description of what was observed */
  description: string;
  
  /** Source signals that contributed to this observation */
  sourceSignalIds: string[];
  
  /** Confidence in this observation (0.0 to 1.0) */
  confidence: number;
  
  /** Location of observation */
  location?: LocationReference;
  
  /** Time of observation */
  timeReference?: TimeReference;
  
  /** Severity if applicable */
  severity?: SeverityLevel;
  
  /** Affected supply chain sectors */
  affectedSectors?: SupplyChainSector[];
  
  /** Affected asset types */
  affectedAssets?: AssetType[];
  
  /** Structured extracted data */
  extractedData?: Record<string, any>;
  
  /** Supporting evidence or reasoning */
  evidence?: string[];
}

// ============================================================================
// Fused Events
// ============================================================================

/**
 * Fused event created by combining multiple signals and observations
 */
export interface FusedEvent {
  /** Unique event identifier */
  eventId: string;
  
  /** Event type/category */
  eventType: string;
  
  /** Event title for display */
  title: string;
  
  /** Detailed event description */
  description: string;
  
  /** Overall event confidence (0.0 to 1.0) */
  confidence: number;
  
  /** Event severity */
  severity: SeverityLevel;
  
  /** Primary location */
  location: LocationReference;
  
  /** Event time reference */
  timeReference: TimeReference;
  
  /** Source signals that contributed */
  sourceSignalIds: string[];
  
  /** Observations that were fused */
  observations: ExtractedObservation[];
  
  /** Affected supply chain sectors */
  affectedSectors: SupplyChainSector[];
  
  /** Affected asset types */
  affectedAssets: AssetType[];
  
  /** Estimated impact radius in meters */
  impactRadiusMeters?: number;
  
  /** Event status (active, resolved, monitoring) */
  status: string;
  
  /** When event was first detected (ISO 8601) */
  detectedAt: string;
  
  /** Last update timestamp (ISO 8601) */
  updatedAt: string;
  
  /** Related event IDs (for clustering) */
  relatedEventIds?: string[];
  
  /** Additional structured metadata */
  metadata?: Record<string, any>;
}

// ============================================================================
// Disruption Assessment
// ============================================================================

/**
 * Assessment of supply chain disruption impact
 */
export interface DisruptionAssessment {
  /** Unique assessment identifier */
  assessmentId: string;
  
  /** Associated event ID */
  eventId: string;
  
  /** Overall disruption severity */
  disruptionSeverity: SeverityLevel;
  
  /** Confidence in this assessment (0.0 to 1.0) */
  confidence: number;
  
  /** Affected supply chain sectors with impact details */
  sectorImpacts: Array<{
    sector: SupplyChainSector;
    severity: SeverityLevel;
    description: string;
    estimatedRecoveryHours?: number;
  }>;
  
  /** Affected assets with status */
  assetImpacts: Array<{
    assetType: AssetType;
    assetId?: string;
    assetName?: string;
    location?: LocationReference;
    status: 'offline' | 'degraded' | 'operational' | 'unknown';
    severity: SeverityLevel;
    description: string;
  }>;
  
  /** Economic impact estimates */
  economicImpact?: {
    estimatedCostUSD?: number;
    economicSectors?: string[];
    affectedBusinessCount?: number;
  };
  
  /** Population impact */
  populationImpact?: {
    affectedPopulation?: number;
    evacuationRequired?: boolean;
    criticalServicesDisrupted?: string[];
  };
  
  /** Cascading effects and dependencies */
  cascadingEffects?: Array<{
    description: string;
    sectors: SupplyChainSector[];
    likelihood: number;
  }>;
  
  /** Recommended actions */
  recommendations?: string[];
  
  /** Assessment timestamp (ISO 8601) */
  assessedAt: string;
  
  /** Assessment validity period */
  validUntil?: string;
  
  /** Analyst or system that created assessment */
  assessedBy?: string;
}

// ============================================================================
// Alert Recommendations
// ============================================================================

/**
 * Alert recommendation for emergency managers
 */
export interface AlertRecommendation {
  /** Unique alert identifier */
  alertId: string;
  
  /** Associated event ID */
  eventId: string;
  
  /** Associated assessment ID */
  assessmentId?: string;
  
  /** Alert priority */
  priority: AlertPriority;
  
  /** Alert title */
  title: string;
  
  /** Alert message body */
  message: string;
  
  /** Target audience for this alert */
  targetAudience?: string[];
  
  /** Geographic area for alert distribution */
  alertArea?: LocationReference;
  
  /** Recommended actions for responders */
  recommendedActions: string[];
  
  /** Resources needed */
  resourcesNeeded?: Array<{
    resourceType: string;
    quantity?: number;
    priority: AlertPriority;
  }>;
  
  /** Time sensitivity information */
  timeConstraints?: {
    issueBy?: string;
    expiresAt?: string;
    responseWindowMinutes?: number;
  };
  
  /** Alert created timestamp (ISO 8601) */
  createdAt: string;
  
  /** Alert status */
  status: 'draft' | 'active' | 'acknowledged' | 'resolved' | 'expired';
  
  /** Related alert IDs */
  relatedAlertIds?: string[];
}

// ============================================================================
// Visualization Outputs
// ============================================================================

/**
 * Map feature payload for GIS visualization
 */
export interface MapFeaturePayload {
  /** Unique feature identifier */
  featureId: string;
  
  /** Feature type for rendering */
  featureType: 'event' | 'disruption' | 'asset' | 'alert' | 'observation';
  
  /** Associated data ID (eventId, alertId, etc.) */
  dataId: string;
  
  /** GeoJSON-compatible geometry */
  geometry: GeoJSONGeometry;
  
  /** Display properties */
  properties: {
    title: string;
    description?: string;
    severity?: SeverityLevel;
    priority?: AlertPriority;
    status?: string;
    color?: string;
    icon?: string;
  };
  
  /** Style overrides for rendering */
  style?: {
    fillColor?: string;
    strokeColor?: string;
    strokeWidth?: number;
    opacity?: number;
    iconUrl?: string;
    iconSize?: [number, number];
  };
  
  /** Popup content (HTML or markdown) */
  popupContent?: string;
  
  /** Layer assignment for map organization */
  layer: string;
  
  /** Feature z-index for rendering order */
  zIndex?: number;
  
  /** Visibility settings */
  visible?: boolean;
  
  /** Feature timestamp (ISO 8601) */
  timestamp: string;
}

/**
 * Dashboard summary for situational awareness
 */
export interface DashboardSummary {
  /** Summary generation timestamp (ISO 8601) */
  generatedAt: string;
  
  /** Time window for this summary */
  timeWindow: {
    startTime: string;
    endTime: string;
  };
  
  /** Overall situation status */
  situationStatus: {
    overallSeverity: SeverityLevel;
    activeEventsCount: number;
    criticalAlertsCount: number;
    affectedRegions: string[];
  };
  
  /** Event breakdown by severity */
  eventsBySeverity: Array<{
    severity: SeverityLevel;
    count: number;
    trend?: 'increasing' | 'decreasing' | 'stable';
  }>;
  
  /** Sector disruption summary */
  sectorDisruptions: Array<{
    sector: SupplyChainSector;
    severity: SeverityLevel;
    affectedAssetsCount: number;
    description?: string;
  }>;
  
  /** Active alerts summary */
  alerts: {
    urgent: number;
    high: number;
    normal: number;
    low: number;
  };
  
  /** Key metrics */
  keyMetrics: Array<{
    label: string;
    value: number | string;
    unit?: string;
    trend?: 'up' | 'down' | 'stable';
    changePercent?: number;
  }>;
  
  /** Recent significant events (top N) */
  recentSignificantEvents: Array<{
    eventId: string;
    title: string;
    severity: SeverityLevel;
    timestamp: string;
  }>;
  
  /** Geographic hotspots */
  hotspots?: Array<{
    location: LocationReference;
    eventCount: number;
    highestSeverity: SeverityLevel;
  }>;
  
  /** System health indicators */
  systemHealth?: {
    signalsProcessedCount: number;
    averageProcessingLatencyMs?: number;
    dataQuality?: number;
    warnings?: string[];
  };
}

// ============================================================================
// API Request and Response
// ============================================================================

/**
 * Incident input request for multimodal signal processing
 */
export interface IncidentInputRequest {
  /** Trace context for request tracking */
  trace: TraceContext;
  
  /** Text signals to process */
  textSignals?: TextSignal[];
  
  /** Vision signals to process */
  visionSignals?: VisionSignal[];
  
  /** Quantitative signals to process */
  quantSignals?: QuantSignal[];
  
  /** Processing options */
  options?: {
    /** Enable/disable specific processing modules */
    enableFusion?: boolean;
    enableDisruptionAssessment?: boolean;
    enableAlertGeneration?: boolean;
    
    /** Minimum confidence threshold for outputs */
    minConfidenceThreshold?: number;
    
    /** Geographic bounds for filtering */
    geographicBounds?: LocationReference;
    
    /** Time window for analysis */
    timeWindow?: {
      startTime: string;
      endTime: string;
    };
    
    /** Sectors to focus analysis on */
    focusSectors?: SupplyChainSector[];
  };
  
  /** User or system making the request */
  requestor?: {
    userId?: string;
    organization?: string;
    role?: string;
  };
}

/**
 * Final API response containing all processed outputs
 */
export interface FinalApiResponse {
  /** Request trace context */
  trace: TraceContext;
  
  /** Processing status */
  status: 'success' | 'partial_success' | 'error';
  
  /** Processing timestamp (ISO 8601) */
  processedAt: string;
  
  /** Processing duration in milliseconds */
  processingDurationMs: number;
  
  /** Fused events detected */
  events: FusedEvent[];
  
  /** Disruption assessments generated */
  disruptions: DisruptionAssessment[];
  
  /** Alert recommendations */
  alerts: AlertRecommendation[];
  
  /** Map features for visualization */
  mapFeatures: MapFeaturePayload[];
  
  /** Dashboard summary */
  dashboardSummary?: DashboardSummary;
  
  /** System warnings (non-fatal issues) */
  warnings?: Array<{
    code: string;
    message: string;
    severity: 'low' | 'medium' | 'high';
  }>;
  
  /** Errors encountered (if status is partial_success or error) */
  errors?: AppError[];
  
  /** Processing metadata */
  metadata?: {
    signalsProcessed: number;
    observationsExtracted: number;
    eventsCreated: number;
    modelVersions?: Record<string, string>;
  };
}

// ============================================================================
// Type Guards (Optional Utilities)
// ============================================================================

/**
 * Type guard to check if a signal is a TextSignal
 */
export function isTextSignal(signal: RawSignal): signal is TextSignal {
  return signal.signalType === 'text';
}

/**
 * Type guard to check if a signal is a VisionSignal
 */
export function isVisionSignal(signal: RawSignal): signal is VisionSignal {
  return signal.signalType === 'vision';
}

/**
 * Type guard to check if a signal is a QuantSignal
 */
export function isQuantSignal(signal: RawSignal): signal is QuantSignal {
  return signal.signalType === 'quantitative';
}
