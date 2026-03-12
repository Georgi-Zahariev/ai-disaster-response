/**
 * Fused Events Panel Component
 * 
 * Displays detected events from multimodal signal fusion.
 */

import type { FusedEvent } from '../types/incident';

interface FusedEventsPanelProps {
  events: FusedEvent[];
}

function FusedEventsPanel({ events = [] }: FusedEventsPanelProps) {

  const getSeverityClass = (severity: string) => {
    return `severity-${severity}`;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="panel fused-events-panel">
      <h2>Fused Events</h2>
      
      {events.length === 0 ? (
        <div className="empty-state">
          <p>No detected events</p>
          <p className="empty-state-hint">
            Events from multimodal signal fusion will appear here
          </p>
        </div>
      ) : (
        <div className="events-list">
          {events.map((event) => (
            <div key={event.eventId} className={`event-item ${getSeverityClass(event.severity)}`}>
              <div className="event-header">
                <span className={`event-severity ${getSeverityClass(event.severity)}`}>
                  {event.severity.toUpperCase()}
                </span>
                <span className="event-type">{event.eventType}</span>
              </div>
              <div className="event-title">{event.title}</div>
              <div className="event-description">{event.description}</div>
              <div className="event-meta">
                <div className="event-location">
                  📍 {event.location.placeName || `${event.location.latitude}, ${event.location.longitude}`}
                </div>
                <div className="event-time">
                  🕒 {formatTimestamp(event.timeReference.timestamp)}
                </div>
                <div className="event-confidence">
                  Confidence: {(event.confidence * 100).toFixed(0)}%
                </div>
              </div>
              {event.affectedSectors && event.affectedSectors.length > 0 && (
                <div className="event-sectors">
                  <strong>Affected Sectors:</strong> {event.affectedSectors.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FusedEventsPanel;
