/**
 * Validation utilities for disaster response types
 * 
 * These utilities provide runtime validation and type checking for the
 * shared schemas. Use these when you need to validate data from external
 * sources or ensure type safety at runtime.
 */

import {
  LocationReference,
  TimeReference,
  TextSignal,
  VisionSignal,
  QuantSignal,
  FusedEvent,
  DisruptionAssessment,
  AlertRecommendation,
  SeverityLevel,
  AlertPriority
} from './index';

// ============================================================================
// Core Validation Functions
// ============================================================================

/**
 * Validates that a confidence score is within valid range [0.0, 1.0]
 */
export function isValidConfidence(value: number): boolean {
  return typeof value === 'number' && value >= 0.0 && value <= 1.0;
}

/**
 * Validates latitude is within valid range [-90, 90]
 */
export function isValidLatitude(lat: number): boolean {
  return typeof lat === 'number' && lat >= -90 && lat <= 90;
}

/**
 * Validates longitude is within valid range [-180, 180]
 */
export function isValidLongitude(lon: number): boolean {
  return typeof lon === 'number' && lon >= -180 && lon <= 180;
}

/**
 * Validates that a timestamp string is in ISO 8601 format
 */
export function isValidISOTimestamp(timestamp: string): boolean {
  if (typeof timestamp !== 'string') return false;
  const date = new Date(timestamp);
  return !isNaN(date.getTime()) && date.toISOString() === timestamp;
}

/**
 * Validates a LocationReference object
 */
export function isValidLocation(location: Partial<LocationReference>): location is LocationReference {
  if (!location || typeof location !== 'object') return false;
  
  if (!isValidLatitude(location.latitude!) || !isValidLongitude(location.longitude!)) {
    return false;
  }
  
  if (location.elevation !== undefined && typeof location.elevation !== 'number') {
    return false;
  }
  
  if (location.uncertaintyRadiusMeters !== undefined) {
    if (typeof location.uncertaintyRadiusMeters !== 'number' || location.uncertaintyRadiusMeters < 0) {
      return false;
    }
  }
  
  return true;
}

/**
 * Validates a TimeReference object
 */
export function isValidTimeReference(timeRef: Partial<TimeReference>): timeRef is TimeReference {
  if (!timeRef || typeof timeRef !== 'object') return false;
  
  if (!isValidISOTimestamp(timeRef.timestamp!)) {
    return false;
  }
  
  if (timeRef.startTime && !isValidISOTimestamp(timeRef.startTime)) {
    return false;
  }
  
  if (timeRef.endTime && !isValidISOTimestamp(timeRef.endTime)) {
    return false;
  }
  
  if (timeRef.confidence !== undefined && !isValidConfidence(timeRef.confidence)) {
    return false;
  }
  
  return true;
}

// ============================================================================
// Signal Validation
// ============================================================================

/**
 * Validates common signal fields
 */
function validateBaseSignal(signal: any): boolean {
  if (!signal || typeof signal !== 'object') return false;
  
  if (!signal.signalId || typeof signal.signalId !== 'string') return false;
  if (!signal.signalType || typeof signal.signalType !== 'string') return false;
  if (!signal.source || typeof signal.source !== 'object') return false;
  if (!isValidISOTimestamp(signal.receivedAt)) return false;
  if (!isValidISOTimestamp(signal.createdAt)) return false;
  
  if (signal.location && !isValidLocation(signal.location)) return false;
  if (signal.timeReference && !isValidTimeReference(signal.timeReference)) return false;
  if (signal.confidence !== undefined && !isValidConfidence(signal.confidence)) return false;
  
  return true;
}

/**
 * Validates a TextSignal
 */
export function isValidTextSignal(signal: any): signal is TextSignal {
  if (!validateBaseSignal(signal)) return false;
  if (signal.signalType !== 'text') return false;
  if (!signal.content || typeof signal.content !== 'string') return false;
  
  if (signal.entities && !Array.isArray(signal.entities)) return false;
  if (signal.sentiment !== undefined) {
    if (typeof signal.sentiment !== 'number' || signal.sentiment < -1.0 || signal.sentiment > 1.0) {
      return false;
    }
  }
  
  return true;
}

/**
 * Validates a VisionSignal
 */
export function isValidVisionSignal(signal: any): signal is VisionSignal {
  if (!validateBaseSignal(signal)) return false;
  if (signal.signalType !== 'vision') return false;
  if (!signal.mediaUrl || typeof signal.mediaUrl !== 'string') return false;
  if (!signal.mediaType || typeof signal.mediaType !== 'string') return false;
  
  if (signal.resolution) {
    if (typeof signal.resolution.width !== 'number' || typeof signal.resolution.height !== 'number') {
      return false;
    }
  }
  
  if (signal.detectedObjects && !Array.isArray(signal.detectedObjects)) return false;
  
  return true;
}

/**
 * Validates a QuantSignal
 */
export function isValidQuantSignal(signal: any): signal is QuantSignal {
  if (!validateBaseSignal(signal)) return false;
  if (signal.signalType !== 'quantitative') return false;
  if (!signal.measurementType || typeof signal.measurementType !== 'string') return false;
  if (typeof signal.value !== 'number') return false;
  if (!signal.unit || typeof signal.unit !== 'string') return false;
  
  if (signal.normalRange) {
    if (typeof signal.normalRange.min !== 'number' || typeof signal.normalRange.max !== 'number') {
      return false;
    }
  }
  
  if (signal.deviationScore !== undefined && typeof signal.deviationScore !== 'number') {
    return false;
  }
  
  return true;
}

// ============================================================================
// Event Validation
// ============================================================================

/**
 * Validates a FusedEvent
 */
export function isValidFusedEvent(event: any): event is FusedEvent {
  if (!event || typeof event !== 'object') return false;
  
  if (!event.eventId || typeof event.eventId !== 'string') return false;
  if (!event.eventType || typeof event.eventType !== 'string') return false;
  if (!event.title || typeof event.title !== 'string') return false;
  if (!event.description || typeof event.description !== 'string') return false;
  
  if (!isValidConfidence(event.confidence)) return false;
  if (!Object.values(SeverityLevel).includes(event.severity)) return false;
  if (!isValidLocation(event.location)) return false;
  if (!isValidTimeReference(event.timeReference)) return false;
  
  if (!Array.isArray(event.sourceSignalIds)) return false;
  if (!Array.isArray(event.observations)) return false;
  if (!Array.isArray(event.affectedSectors)) return false;
  if (!Array.isArray(event.affectedAssets)) return false;
  
  if (!event.status || typeof event.status !== 'string') return false;
  if (!isValidISOTimestamp(event.detectedAt)) return false;
  if (!isValidISOTimestamp(event.updatedAt)) return false;
  
  return true;
}

/**
 * Validates a DisruptionAssessment
 */
export function isValidDisruptionAssessment(assessment: any): assessment is DisruptionAssessment {
  if (!assessment || typeof assessment !== 'object') return false;
  
  if (!assessment.assessmentId || typeof assessment.assessmentId !== 'string') return false;
  if (!assessment.eventId || typeof assessment.eventId !== 'string') return false;
  if (!Object.values(SeverityLevel).includes(assessment.disruptionSeverity)) return false;
  if (!isValidConfidence(assessment.confidence)) return false;
  
  if (!Array.isArray(assessment.sectorImpacts)) return false;
  if (!Array.isArray(assessment.assetImpacts)) return false;
  
  if (!isValidISOTimestamp(assessment.assessedAt)) return false;
  
  return true;
}

/**
 * Validates an AlertRecommendation
 */
export function isValidAlertRecommendation(alert: any): alert is AlertRecommendation {
  if (!alert || typeof alert !== 'object') return false;
  
  if (!alert.alertId || typeof alert.alertId !== 'string') return false;
  if (!alert.eventId || typeof alert.eventId !== 'string') return false;
  if (!Object.values(AlertPriority).includes(alert.priority)) return false;
  if (!alert.title || typeof alert.title !== 'string') return false;
  if (!alert.message || typeof alert.message !== 'string') return false;
  
  if (!Array.isArray(alert.recommendedActions)) return false;
  
  if (!isValidISOTimestamp(alert.createdAt)) return false;
  if (!alert.status || typeof alert.status !== 'string') return false;
  
  return true;
}

// ============================================================================
// Sanitization Functions
// ============================================================================

/**
 * Sanitizes and clamps a confidence value to [0.0, 1.0]
 */
export function sanitizeConfidence(value: number): number {
  return Math.max(0.0, Math.min(1.0, value));
}

/**
 * Sanitizes a latitude value to [-90, 90]
 */
export function sanitizeLatitude(lat: number): number {
  return Math.max(-90, Math.min(90, lat));
}

/**
 * Sanitizes a longitude value to [-180, 180]
 */
export function sanitizeLongitude(lon: number): number {
  // Handle wrapping for longitude
  while (lon > 180) lon -= 360;
  while (lon < -180) lon += 360;
  return lon;
}

/**
 * Ensures a timestamp string is in ISO 8601 format
 * Returns current time if invalid
 */
export function sanitizeTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      return new Date().toISOString();
    }
    return date.toISOString();
  } catch {
    return new Date().toISOString();
  }
}

// ============================================================================
// Comparison and Sorting Utilities
// ============================================================================

/**
 * Compares two events by severity (critical > high > moderate > low)
 */
export function compareBySeverity(a: { severity: SeverityLevel }, b: { severity: SeverityLevel }): number {
  const severityOrder = {
    [SeverityLevel.CRITICAL]: 4,
    [SeverityLevel.HIGH]: 3,
    [SeverityLevel.MODERATE]: 2,
    [SeverityLevel.LOW]: 1,
    [SeverityLevel.INFORMATIONAL]: 0
  };
  
  return severityOrder[b.severity] - severityOrder[a.severity];
}

/**
 * Compares two alerts by priority (urgent > high > normal > low)
 */
export function compareByPriority(a: { priority: AlertPriority }, b: { priority: AlertPriority }): number {
  const priorityOrder = {
    [AlertPriority.URGENT]: 4,
    [AlertPriority.HIGH]: 3,
    [AlertPriority.NORMAL]: 2,
    [AlertPriority.LOW]: 1
  };
  
  return priorityOrder[b.priority] - priorityOrder[a.priority];
}

/**
 * Compares two items by timestamp (newest first)
 */
export function compareByTimestamp(
  a: { timestamp?: string; createdAt?: string },
  b: { timestamp?: string; createdAt?: string }
): number {
  const timeA = new Date(a.timestamp || a.createdAt || 0).getTime();
  const timeB = new Date(b.timestamp || b.createdAt || 0).getTime();
  return timeB - timeA;
}

/**
 * Compares two items by confidence (highest first)
 */
export function compareByConfidence(a: { confidence: number }, b: { confidence: number }): number {
  return b.confidence - a.confidence;
}

// ============================================================================
// Distance Calculations
// ============================================================================

/**
 * Calculates the Haversine distance between two geographic points in meters
 */
export function calculateDistance(
  loc1: { latitude: number; longitude: number },
  loc2: { latitude: number; longitude: number }
): number {
  const R = 6371000; // Earth's radius in meters
  const lat1Rad = (loc1.latitude * Math.PI) / 180;
  const lat2Rad = (loc2.latitude * Math.PI) / 180;
  const deltaLat = ((loc2.latitude - loc1.latitude) * Math.PI) / 180;
  const deltaLon = ((loc2.longitude - loc1.longitude) * Math.PI) / 180;
  
  const a =
    Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
    Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
}

/**
 * Checks if a location is within a given radius of another location
 */
export function isWithinRadius(
  center: { latitude: number; longitude: number },
  point: { latitude: number; longitude: number },
  radiusMeters: number
): boolean {
  return calculateDistance(center, point) <= radiusMeters;
}

// ============================================================================
// Time Utilities
// ============================================================================

/**
 * Calculates the time difference in milliseconds between two timestamps
 */
export function getTimeDifferenceMs(timestamp1: string, timestamp2: string): number {
  return Math.abs(new Date(timestamp1).getTime() - new Date(timestamp2).getTime());
}

/**
 * Checks if a timestamp is within a given time window
 */
export function isWithinTimeWindow(
  timestamp: string,
  windowStart: string,
  windowEnd: string
): boolean {
  const time = new Date(timestamp).getTime();
  const start = new Date(windowStart).getTime();
  const end = new Date(windowEnd).getTime();
  return time >= start && time <= end;
}

/**
 * Checks if a timestamp is recent (within the last N milliseconds)
 */
export function isRecent(timestamp: string, maxAgeMs: number): boolean {
  const age = Date.now() - new Date(timestamp).getTime();
  return age >= 0 && age <= maxAgeMs;
}

// ============================================================================
// Validation Result Type
// ============================================================================

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Comprehensive validation of a signal with detailed error messages
 */
export function validateSignal(signal: any): ValidationResult {
  const result: ValidationResult = {
    valid: true,
    errors: [],
    warnings: []
  };
  
  if (!signal || typeof signal !== 'object') {
    result.valid = false;
    result.errors.push('Signal must be an object');
    return result;
  }
  
  if (!signal.signalId) {
    result.valid = false;
    result.errors.push('Signal ID is required');
  }
  
  if (!signal.signalType) {
    result.valid = false;
    result.errors.push('Signal type is required');
  }
  
  if (signal.confidence !== undefined && !isValidConfidence(signal.confidence)) {
    result.valid = false;
    result.errors.push('Confidence must be between 0.0 and 1.0');
  }
  
  if (signal.location && !isValidLocation(signal.location)) {
    result.valid = false;
    result.errors.push('Invalid location data');
  }
  
  // Add warnings for best practices
  if (signal.confidence && signal.confidence < 0.5) {
    result.warnings.push('Low confidence signal (< 0.5)');
  }
  
  if (!signal.source || !signal.source.reliabilityScore) {
    result.warnings.push('Source reliability score not provided');
  }
  
  return result;
}

/**
 * Batch validation of multiple signals
 */
export function validateSignals(signals: any[]): ValidationResult {
  const result: ValidationResult = {
    valid: true,
    errors: [],
    warnings: []
  };
  
  if (!Array.isArray(signals)) {
    result.valid = false;
    result.errors.push('Signals must be an array');
    return result;
  }
  
  signals.forEach((signal, index) => {
    const signalResult = validateSignal(signal);
    if (!signalResult.valid) {
      result.valid = false;
      signalResult.errors.forEach(err => {
        result.errors.push(`Signal ${index}: ${err}`);
      });
    }
    signalResult.warnings.forEach(warn => {
      result.warnings.push(`Signal ${index}: ${warn}`);
    });
  });
  
  return result;
}
