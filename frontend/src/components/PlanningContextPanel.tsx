/**
 * Planning Context Panel
 *
 * Shows optional planning enrichment and keeps it visually distinct from live evidence.
 */

import type { PlanningContextView } from '../types/incident';

interface PlanningContextPanelProps {
  planningContext?: PlanningContextView | null;
}

function PlanningContextPanel({ planningContext }: PlanningContextPanelProps) {
  if (!planningContext?.requested) {
    return (
      <div className="panel planning-panel planning-panel-muted">
        <h2>Planning Baseline (Non-Live)</h2>
        <div className="empty-state">
          <p>Planning context is not enabled for this run</p>
          <p className="empty-state-hint">Enable planning mode to include historical bottlenecks and seasonal route risk context</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel planning-panel">
      <h2>Planning Baseline (Non-Live)</h2>
      <p className="panel-subtitle">Historical and seasonal context for preparedness. Not used as live incident evidence.</p>
      <div className="planning-badge">Non-live baseline context</div>

      <div className="planning-summary">
        <div>Records: {planningContext.recordCount}</div>
        <div>Matched Cases: {planningContext.matchesByCase.length}</div>
      </div>

      {planningContext.matchesByCase.length === 0 ? (
        <div className="empty-state">
          <p>No case-specific planning matches</p>
          <p className="empty-state-hint">Planning baseline loaded without corridor-level case matches</p>
        </div>
      ) : (
        <div className="planning-matches">
          {planningContext.matchesByCase.map((entry) => (
            <div key={entry.eventId} className="planning-item">
              <div className="planning-item-header">
                <strong>{entry.eventType}</strong>
                <span>{entry.eventId}</span>
              </div>
              <ul>
                {entry.matches.map((m, idx) => (
                  <li key={`${entry.eventId}-${idx}`}>
                    {m.concept}: {m.summary}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PlanningContextPanel;
