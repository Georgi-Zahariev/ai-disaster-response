/**
 * Frontend-specific type definitions for UI components.
 * 
 * These types are simplified versions for display purposes.
 * For backend integration, use types from './incident.ts' for API data.
 */

// Re-export main incident types
export type {
  IncidentAnalysisRequest,
  IncidentAnalysisResponse,
  FusedEvent,
  AlertRecommendation,
  DisruptionAssessment,
  DashboardSummary,
  MapFeaturePayload,
  ExtractedObservation,
  LocationReference,
  TimeReference,
  SimpleIncidentInput,
} from './incident';

export {
  SeverityLevel,
  AlertPriority,
  SupplyChainSector,
  SourceType,
} from './event';

export { createIncidentRequest } from './incident';

// For convenience, import types for use in this file
import type { IncidentAnalysisResponse } from './incident';

// ============================================================================
// Component Props Types (UI-specific, not from backend)
// ============================================================================

/**
 * Incident form input data
 * Used in: IncidentForm component
 */
export interface IncidentInputData {
  description: string;
  location?: string;
  county?: 'hillsborough' | 'pinellas' | 'pasco';
  enablePlanningContext?: boolean;
}

/**
 * Summary card display data
 * Used in: SummaryCards component
 */
export interface SummaryCardData {
  label: string;
  value: number | string;
  severity?: 'critical' | 'high' | 'moderate' | 'low' | 'info';
  trend?: 'up' | 'down' | 'stable';
  changePercent?: number;
}

/**
 * Activity log entry
 * Used in: ActivityLogPanel component
 */
export interface ActivityLogEntry {
  id: string;
  timestamp: string;
  type: 'event' | 'alert' | 'assessment' | 'system';
  message: string;
  severity?: 'critical' | 'high' | 'moderate' | 'low' | 'info';
}

/**
 * Source/feed card data
 * Used in: SourcesPanel component
 */
export interface SourceCardData {
  sourceId: string;
  sourceName: string;
  sourceType: 'text' | 'vision' | 'quantitative';
  status: 'active' | 'inactive' | 'error';
  lastUpdate: string;
  signalCount?: number;
}

// ============================================================================
// UI State Types
// ============================================================================

/**
 * Dashboard application state
 * Used in: Dashboard page component
 */
export interface DashboardState {
  isLoading: boolean;
  hasData: boolean;
  error?: string;
  lastUpdate?: string;
  currentResponse?: IncidentAnalysisResponse;
}

/**
 * Filter options for dashboard
 * Used in: Dashboard filtering (future implementation)
 */
export interface DashboardFilters {
  severityLevels?: string[];
  sectors?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
}
