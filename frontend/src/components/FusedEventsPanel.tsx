/**
 * Fused Events Panel Component
 * 
 * Displays detected events from multimodal signal fusion.
 */

import type { FusedCase, FusedEvent } from '../types/incident';

interface FusedEventsPanelProps {
  cases?: FusedCase[];
  events?: FusedEvent[];
}

function FusedEventsPanel({ cases, events = [] }: FusedEventsPanelProps) {
  const shouldUseLegacyFallback = !Array.isArray(cases);
  const normalizedCases = shouldUseLegacyFallback ? events.map((event) => ({
    caseId: event.eventId,
    event,
    assessment: {
      recommendations: [],
    },
    routeTraffic: { routeIds: [], conceptCounts: {} },
    weatherHazard: { conceptCounts: {}, stateCounts: {} },
    facilities: { relatedFacilityIds: [], relatedFuelFacilityIds: [], relatedGroceryFacilityIds: [] },
    planningContext: { requested: false, isLiveEvidence: false as const, matches: [] },
    provenance: { sourceSignalIds: event.sourceSignalIds || [], evidenceRefs: [] },
  })) : cases;

  const getSeverityClass = (severity: string) => {
    return `severity-${severity}`;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getBestTimestamp = (event: FusedEvent): string => {
    return (
      event.timeReference?.timestamp
      || event.timeReference?.startTime
      || event.detectedAt
      || event.updatedAt
      || new Date().toISOString()
    );
  };

  const truncate = (text: string, max = 240): string => {
    if (!text) return '';
    return text.length > max ? `${text.slice(0, max - 1)}...` : text;
  };

  return (
    <div className="panel fused-events-panel">
      <h2>Fused Disruption Cases</h2>
      <p className="panel-subtitle">Operational case view for corridor access, corroborating hazards, and impacted resources.</p>
      
      {normalizedCases.length === 0 ? (
        <div className="empty-state">
          <p>No active disruption cases</p>
          <p className="empty-state-hint">
            Route-access cases will appear after incident analysis
          </p>
        </div>
      ) : (
        <div className="events-list">
          {normalizedCases.map((item) => {
            const event = item.event;
            const weatherSignalCount = Object.values(item.weatherHazard.conceptCounts || {}).reduce<number>(
              (sum, value) => sum + Number(value ?? 0),
              0,
            );
            return (
            <div key={event.eventId} className={`event-item ${getSeverityClass(event.severity)}`}>
              <div className="event-header">
                <span className={`event-severity ${getSeverityClass(event.severity)}`}>
                  {event.severity.toUpperCase()}
                </span>
                <span className="event-type">{event.eventType}</span>
              </div>
              <div className="case-id">Case ID: {item.caseId}</div>
              <div className="event-title">{event.title}</div>
              <div className="event-description">{truncate(event.description || '')}</div>
              <div className="event-meta">
                <div className="event-location">
                  📍 {event.location.placeName || `${event.location.latitude}, ${event.location.longitude}`}
                </div>
                <div className="event-time">
                  🕒 {formatTimestamp(getBestTimestamp(event))}
                </div>
                <div className="event-confidence">
                  Confidence: {(event.confidence * 100).toFixed(0)}%
                </div>
              </div>
              {item.routeTraffic.routeIds.length > 0 && (
                <div className="event-sectors">
                  <strong>Route Corridors:</strong> {item.routeTraffic.routeIds.join(', ')}
                </div>
              )}
              <div className="case-kpis">
                <span className="case-chip">Fuel Access: {item.facilities.relatedFuelFacilityIds.length}</span>
                <span className="case-chip">Grocery Access: {item.facilities.relatedGroceryFacilityIds.length}</span>
                <span className="case-chip">Weather Signals: {weatherSignalCount}</span>
              </div>
              {item.facilities.relatedFuelFacilityIds.length > 0 || item.facilities.relatedGroceryFacilityIds.length > 0 ? (
                <div className="event-sectors">
                  <strong>Access Impact:</strong>{' '}
                  fuel ({item.facilities.relatedFuelFacilityIds.length}), grocery ({item.facilities.relatedGroceryFacilityIds.length})
                </div>
              ) : null}
              {item.weatherHazard.conceptCounts && Object.keys(item.weatherHazard.conceptCounts).length > 0 && (
                <div className="event-sectors">
                  <strong>Weather Evidence:</strong>{' '}
                  {Object.entries(item.weatherHazard.conceptCounts)
                    .map(([k, v]) => `${k} (${v})`)
                    .join(', ')}
                </div>
              )}
              {item.planningContext.requested && (
                <div className="event-sectors planning-note">
                  <strong>Planning Context:</strong> non-live enrichment ({item.planningContext.matches.length} matches)
                </div>
              )}
              {event.affectedSectors && event.affectedSectors.length > 0 && (
                <div className="event-sectors">
                  <strong>Affected Sectors:</strong> {event.affectedSectors.join(', ')}
                </div>
              )}
            </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default FusedEventsPanel;
