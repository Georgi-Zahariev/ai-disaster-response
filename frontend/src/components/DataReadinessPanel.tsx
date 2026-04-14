/**
 * Data Readiness Panel
 *
 * Shows effective live vs staged provider modes and deterministic fallback state.
 */

import type { ReadinessSnapshotResponse } from '../types/incident';

interface DataReadinessPanelProps {
  readiness: ReadinessSnapshotResponse | null;
  loading: boolean;
  error: string | null;
}

function boolLabel(value: boolean): string {
  return value ? 'on' : 'off';
}

function DataReadinessPanel({ readiness, loading, error }: DataReadinessPanelProps) {
  return (
    <div className="panel dashboard-summary-panel">
      <h2>Data Readiness</h2>
      <p className="panel-subtitle">Live/degraded provider status for route, weather, and facility context.</p>

      {loading && <p>Checking provider readiness...</p>}
      {!loading && error && <p className="helper-text">Readiness status unavailable. Core incident workflow remains available.</p>}

      {!loading && !error && readiness && (
        <div className="dashboard-summary-grid">
          <div>
            <strong>Weather:</strong> {readiness.providers.weather.configuredMode} ({readiness.providers.weather.effectiveSource})
          </div>
          <div>
            <strong>Facilities:</strong> {readiness.providers.facilities.configuredMode} ({readiness.providers.facilities.effectiveSource})
          </div>
          <div>
            <strong>Weather Fallback:</strong> {readiness.providers.weather.fallbackUsed ? 'yes' : 'no'}
          </div>
          <div>
            <strong>Facility Fallback:</strong> {readiness.providers.facilities.fallbackUsed ? 'yes' : 'no'}
          </div>
          <div>
            <strong>Extraction (text/vision/quant):</strong>
            {' '}
            {boolLabel(readiness.providers.extraction.textRealEnabled)} /
            {boolLabel(readiness.providers.extraction.visionRealEnabled)} /
            {boolLabel(readiness.providers.extraction.quantRealEnabled)}
          </div>
          <div>
            <strong>Decision Guide:</strong> {readiness.providers.llm.enabled ? 'AI-assisted' : 'deterministic fallback'} ({readiness.providers.llm.defaultProvider})
          </div>
          <div>
            <strong>Planning Baseline:</strong> non-live only (kept separate from live evidence)
          </div>
        </div>
      )}
    </div>
  );
}

export default DataReadinessPanel;
