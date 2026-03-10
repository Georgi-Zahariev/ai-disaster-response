/**
 * Type definitions for disaster events.
 * 
 * These types are re-exported from the backend shared schemas.
 * For full documentation, see: ../../backend/types/README.md
 * 
 * @see /backend/types/shared-schemas.ts for complete type definitions
 */

// Import types from backend for re-export
import type {
  FusedEvent,
  DisruptionAssessment,
  AlertRecommendation,
  DashboardSummary,
  MapFeaturePayload,
  ExtractedObservation,
  LocationReference,
  TimeReference,
  FinalApiResponse,
  AppError,
  TraceContext
} from '../../../backend/types';

import {
  SeverityLevel,
  SupplyChainSector,
  AssetType,
  AlertPriority,
  SourceType
} from '../../../backend/types';

// Re-export commonly used types from backend
export type {
  FusedEvent,
  DisruptionAssessment,
  AlertRecommendation,
  DashboardSummary,
  MapFeaturePayload,
  ExtractedObservation,
  LocationReference,
  TimeReference,
  FinalApiResponse,
  AppError,
  TraceContext
};

// Re-export enums
export {
  SeverityLevel,
  SupplyChainSector,
  AssetType,
  AlertPriority,
  SourceType
};

// Frontend-specific display types (extend as needed)
export interface EventCardProps {
  event: FusedEvent;
  onSelect?: (eventId: string) => void;
}

export interface DashboardViewState {
  summary?: DashboardSummary;
  selectedEventId?: string;
  filterSeverity?: SeverityLevel[];
  filterSectors?: SupplyChainSector[];
}
