/**
 * Alerts Panel Component
 * 
 * Displays alert recommendations with priority levels.
 */

import type { AlertRecommendation } from '../types/incident';

interface AlertsPanelProps {
  alerts: AlertRecommendation[];
}

function AlertsPanel({ alerts = [] }: AlertsPanelProps) {

  const getPriorityClass = (priority: string) => {
    return `alert-priority-${priority}`;
  };

  const getPriorityLabel = (priority: string) => {
    return priority.charAt(0).toUpperCase() + priority.slice(1);
  };

  return (
    <div className="panel alerts-panel">
      <h2>Alert Recommendations</h2>
      
      {alerts.length === 0 ? (
        <div className="empty-state">
          <p>No active alerts</p>
          <p className="empty-state-hint">
            Alerts will appear here after incident analysis
          </p>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert) => (
            <div key={alert.alertId} className={`alert-item ${getPriorityClass(alert.priority)}`}>
              <div className="alert-header">
                <span className="alert-priority">{getPriorityLabel(alert.priority)}</span>
                <span className="alert-time">
                  {new Date(alert.createdAt).toLocaleTimeString()}
                </span>
              </div>
              <div className="alert-title">{alert.title}</div>
              <div className="alert-message">{alert.message}</div>
              {alert.recommendedActions && alert.recommendedActions.length > 0 && (
                <div className="alert-actions">
                  <strong>Recommended Actions:</strong>
                  <ul>
                    {alert.recommendedActions.map((action, idx) => (
                      <li key={idx}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AlertsPanel;
