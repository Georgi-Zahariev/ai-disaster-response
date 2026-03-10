/**
 * Central export for all shared TypeScript types and schemas
 * 
 * Import from this module to access all disaster response types:
 * 
 * @example
 * ```typescript
 * import {
 *   IncidentInputRequest,
 *   FusedEvent,
 *   DisruptionAssessment,
 *   AlertRecommendation,
 *   FinalApiResponse
 * } from './types';
 * ```
 */

// Re-export all types from shared-schemas
export * from './shared-schemas';

// Re-export validation utilities
export * from './validation';

// Examples are available but not auto-exported to avoid clutter
// Import explicitly if needed: import { examples } from './types/examples';
