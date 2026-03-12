/**
 * Activity Log Panel Component
 * 
 * Displays system activity and processing events.
 */

import type { ActivityLogEntry } from '../types/ui';
import type { IncidentAnalysisResponse } from '../types/incident';

interface ActivityLogPanelProps {
  response: IncidentAnalysisResponse | null;
}

function ActivityLogPanel({ response }: ActivityLogPanelProps) {
  // Build activity log from response data
  const activities: ActivityLogEntry[] = response ? buildActivityLog(response) : [];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'event':
        return '🔔';
      case 'alert':
        return '⚠️';
      case 'assessment':
        return '📊';
      case 'system':
        return '⚙️';
      default:
        return '📝';
    }
  };

  const getSeverityClass = (severity?: string) => {
    if (!severity) return '';
    return `activity-severity-${severity}`;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <div className="panel activity-log-panel">
      <h2>Activity Log</h2>
      
      {activities.length === 0 ? (
        <div className="empty-state">
          <p>No recent activity</p>
          <p className="empty-state-hint">
            System events and processing logs will appear here
          </p>
        </div>
      ) : (
        <div className="activity-list">
          {activities.map((activity) => (
            <div 
              key={activity.id} 
              className={`activity-item ${getSeverityClass(activity.severity)}`}
            >
              <span className="activity-icon">{getActivityIcon(activity.type)}</span>
              <div className="activity-content">
                <div className="activity-message">{activity.message}</div>
                <div className="activity-time">{formatTimestamp(activity.timestamp)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Build activity log from response data
 */
function buildActivityLog(response: IncidentAnalysisResponse): ActivityLogEntry[] {
  const activities: ActivityLogEntry[] = [];
  let idCounter = 1;

  // Add system start entry
  if (response.trace?.timestamp) {
    activities.push({
      id: `activity-${idCounter++}`,
      type: 'system',
      message: `Analysis started (trace: ${response.trace.traceId?.slice(0, 12) || 'unknown'}...)`,
      timestamp: response.trace.timestamp,
    });
  }

  // Add event detection entries
  response.events?.forEach((event) => {
    activities.push({
      id: `activity-${idCounter++}`,
      type: 'event',
      message: `Event detected: ${event.title}`,
      timestamp: event.detectedAt || event.timeReference.timestamp,
      severity: mapSeverity(event.severity),
    });
  });

  // Add alert entries
  response.alerts?.forEach((alert) => {
    activities.push({
      id: `activity-${idCounter++}`,
      type: 'alert',
      message: `Alert issued: ${alert.title}`,
      timestamp: alert.createdAt,
      severity: alert.priority === 'urgent' ? 'critical' : 
                alert.priority === 'high' ? 'high' : 'moderate',
    });
  });

  // Add disruption assessment entries
  response.disruptions?.forEach((disruption) => {
    const relatedEvent = response.events?.find(e => e.eventId === disruption.eventId);
    activities.push({
      id: `activity-${idCounter++}`,
      type: 'assessment',
      message: `Disruption assessed: ${relatedEvent?.title || `Event ${disruption.eventId}`}`,
      timestamp: disruption.assessedAt,
      severity: mapSeverity(disruption.disruptionSeverity),
    });
  });

  // Add processing completion entry
  if (response.processedAt) {
    activities.push({
      id: `activity-${idCounter++}`,
      type: 'system',
      message: `Processing complete (${response.processingDurationMs || 0}ms)`,
      timestamp: response.processedAt,
    });
  }

  // Sort by timestamp descending (newest first)
  return activities.sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
}

/**
 * Map severity string to ActivityLogEntry severity type
 */
function mapSeverity(severity: string): 'critical' | 'high' | 'moderate' | 'low' | 'info' | undefined {
  const normalized = severity.toLowerCase();
  if (['critical', 'high', 'moderate', 'low', 'info'].includes(normalized)) {
    return normalized as 'critical' | 'high' | 'moderate' | 'low' | 'info';
  }
  return undefined;
}

export default ActivityLogPanel;
