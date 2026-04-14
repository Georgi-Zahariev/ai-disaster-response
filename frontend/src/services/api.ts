/**
 * API client for backend communication.
 * 
 * Base URL is configured via Vite proxy to forward /api requests to http://localhost:8000
 * See vite.config.ts for proxy configuration.
 */

import type {
  ContextGuideResponse,
  FacilitiesResponse,
  IncidentAnalysisRequest,
  IncidentAnalysisResponse,
  ReadinessSnapshotResponse,
} from '../types/incident';

const API_BASE_URL = '/api';

/**
 * Submit incident analysis request to backend
 * 
 * Endpoint: POST /api/incidents/analyze
 * 
 * @param request - Incident analysis request with signals and options
 * @returns Incident analysis response using preferred Tampa MVP fields:
 * summary, cases, alerts, evidence, map, dashboard, planningContext
 * with legacy fallbacks still available.
 * @throws APIError with status code and details
 */
export async function analyzeIncident(
  request: IncidentAnalysisRequest
): Promise<IncidentAnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/incidents/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    // Handle non-2xx responses
    if (!response.ok) {
      let errorMessage = `Request failed: ${response.status} ${response.statusText}`;
      let errorDetails: any = null;

      try {
        errorDetails = await response.json();
        errorMessage = errorDetails.message || errorDetails.detail || errorMessage;
      } catch {
        // If error response is not JSON, use status text
      }

      throw new APIError(errorMessage, response.status, errorDetails);
    }

    // Parse successful response
    try {
      const data: IncidentAnalysisResponse = await response.json();
      return data;
    } catch (parseError) {
      throw new APIError(
        'Failed to parse response: Invalid JSON format',
        response.status,
        { parseError: parseError instanceof Error ? parseError.message : 'Unknown parse error' }
      );
    }
  } catch (error) {
    // Re-throw APIError as-is
    if (error instanceof APIError) {
      throw error;
    }

    // Wrap network errors or other unexpected errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError('Network error: Unable to reach backend server', undefined, { originalError: error.message });
    }

    throw new APIError(
      error instanceof Error ? error.message : 'An unexpected error occurred',
      undefined,
      { originalError: error }
    );
  }
}

/**
 * Fetch app-facing facility records for map marker rendering.
 */
export async function fetchFacilities(
  limit: number
): Promise<FacilitiesResponse> {
  const safeSize = Math.max(1, Math.min(limit, 5000));
  const response = await fetch(`${API_BASE_URL}/facilities?limit=${safeSize}`);

  if (!response.ok) {
    throw new APIError(
      `Facility request failed: ${response.status} ${response.statusText}`,
      response.status
    );
  }

  const data = await response.json();
  return data as FacilitiesResponse;
}

/**
 * Fetch demo readiness snapshot for live-vs-staged data modes.
 */
export async function fetchReadinessSnapshot(
  sampleSize = 2
): Promise<ReadinessSnapshotResponse> {
  const response = await fetch(`${API_BASE_URL}/incidents/readiness?sample_size=${sampleSize}`);

  if (!response.ok) {
    throw new APIError(
      `Readiness request failed: ${response.status} ${response.statusText}`,
      response.status
    );
  }

  return await response.json() as ReadinessSnapshotResponse;
}

/**
 * Request AI context guidance for incident form enrichment.
 */
export async function fetchIncidentContextGuide(payload: {
  description: string;
  location?: string;
  county?: string;
}): Promise<ContextGuideResponse> {
  const response = await fetch(`${API_BASE_URL}/incidents/context-guide`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = `Context guide request failed: ${response.status} ${response.statusText}`;
    try {
      const details = await response.json();
      message = details?.message || details?.detail?.message || details?.detail || message;
    } catch {
      // Keep default message.
    }

    throw new APIError(message, response.status);
  }

  return await response.json() as ContextGuideResponse;
}

/**
 * Error handling helper
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}
