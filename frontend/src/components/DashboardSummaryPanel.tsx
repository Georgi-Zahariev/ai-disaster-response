/**
 * Dashboard Summary Panel
 *
 * Renders backend dashboard summary payload in a compact typed block.
 */

import type { DashboardSummary } from '../types/incident';

interface DashboardSummaryPanelProps {
  dashboardSummary?: DashboardSummary | null;
  isProcessing?: boolean;
}

function DashboardSummaryPanel({ dashboardSummary, isProcessing = false }: DashboardSummaryPanelProps) {
  return (
    <div className="panel dashboard-summary-panel">
      <h2>Operational Snapshot</h2>
      <p className="panel-subtitle">Global indicators from backend computation (not filtered by selected incident).</p>

      {isProcessing ? <p className="empty-state-hint">Refreshing global snapshot...</p> : null}

      {!dashboardSummary ? (
        <div className="empty-state">
          <p>No global snapshot available yet</p>
          <p className="empty-state-hint">Summary metrics appear after analysis completes.</p>
        </div>
      ) : (
        <div className="dashboard-summary-grid">
          <div>
            <strong>Overall Severity:</strong> {dashboardSummary.situationStatus?.overallSeverity || 'unknown'}
          </div>
          <div>
            <strong>Active Events:</strong> {dashboardSummary.situationStatus?.activeEventsCount ?? 0}
          </div>
          <div>
            <strong>Critical Alerts:</strong> {dashboardSummary.situationStatus?.criticalAlertsCount ?? 0}
          </div>
          <div>
            <strong>Affected Regions:</strong> {(dashboardSummary.situationStatus?.affectedRegions || []).join(', ') || 'n/a'}
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardSummaryPanel;
