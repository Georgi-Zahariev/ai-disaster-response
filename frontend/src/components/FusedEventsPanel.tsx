/**
 * Fused Events Panel Component
 * 
 * Displays detected events from multimodal signal fusion.
 */

import type { FusedCase } from '../types/incident';

interface FusedEventsPanelProps {
  cases?: FusedCase[];
  selectedCaseId?: string | null;
  onSelectCase?: (caseId: string) => void;
  isProcessing?: boolean;
}

function FusedEventsPanel({
  cases = [],
  selectedCaseId = null,
  onSelectCase,
  isProcessing = false,
}: FusedEventsPanelProps) {
  const normalizedCases = cases;

  const getSeverityClass = (severity: string) => {
    return `severity-${severity}`;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getBestTimestamp = (event: FusedCase['event']): string => {
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

  const toSortedWeatherEntries = (conceptCounts: Record<string, number> | undefined): Array<[string, number]> => {
    if (!conceptCounts) {
      return [];
    }
    return Object.entries(conceptCounts).sort(([a], [b]) => a.localeCompare(b));
  };

  return (
    <div className="panel fused-events-panel">
      <h2>Fused Disruption Cases</h2>
      <p className="panel-subtitle">Current disruptions, affected access corridors, and corroborating hazard evidence.</p>
      {selectedCaseId && <p className="empty-state-hint">Focused incident: {selectedCaseId}</p>}
      {isProcessing && <p className="empty-state-hint">Refreshing case fusion...</p>}
      
      {normalizedCases.length === 0 ? (
        <div className="empty-state">
          <p>No active disruption cases</p>
          <p className="empty-state-hint">
            Cases appear after route, weather, and access signals are fused.
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
            const isSelected = selectedCaseId === item.caseId;
            return (
            <div
              key={event.eventId}
              className={`event-item ${getSeverityClass(event.severity)} ${isSelected ? 'selected-case' : ''}`}
              onClick={() => onSelectCase?.(item.caseId)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelectCase?.(item.caseId);
                }
              }}
            >
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
                  Location: {event.location.placeName || `${event.location.latitude}, ${event.location.longitude}`}
                </div>
                <div className="event-time">
                  Updated: {formatTimestamp(getBestTimestamp(event))}
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
                  {toSortedWeatherEntries(item.weatherHazard.conceptCounts)
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
