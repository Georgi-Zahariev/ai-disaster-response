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
    const map: Record<string, string> = {
      urgent: 'Urgent',
      high: 'High',
      normal: 'Moderate',
      low: 'Low',
    };
    return map[priority] || (priority.charAt(0).toUpperCase() + priority.slice(1));
  };

  return (
    <div className="panel alerts-panel">
      <h2>Active Alerts</h2>
      <p className="panel-subtitle">Immediate operational actions for route, fuel, and grocery access continuity.</p>
      
      {alerts.length === 0 ? (
        <div className="empty-state">
          <p>No active alerts</p>
          <p className="empty-state-hint">
            Route, fuel, and grocery access alerts will appear after analysis
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
                    {alert.recommendedActions.slice(0, 4).map((action, idx) => (
                      <li key={idx}>{action}</li>
                    ))}
                  </ul>
                  {alert.recommendedActions.length > 4 && (
                    <p className="empty-state-hint">+ {alert.recommendedActions.length - 4} more actions</p>
                  )}
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
