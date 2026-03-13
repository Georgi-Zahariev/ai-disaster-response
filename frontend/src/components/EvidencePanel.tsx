/**
 * Evidence Panel
 *
 * Displays live evidence records only.
 */

import type { EvidenceRecord } from '../types/incident';

interface EvidencePanelProps {
  evidence: EvidenceRecord[];
}

function EvidencePanel({ evidence = [] }: EvidencePanelProps) {
  const formatTime = (timestamp?: string): string => {
    if (!timestamp) return 'n/a';
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="panel evidence-panel">
      <h2>Live Evidence</h2>
      <p className="panel-subtitle">Source-backed observations used in live case fusion (planning context excluded).</p>

      {evidence.length === 0 ? (
        <div className="empty-state">
          <p>No live evidence records</p>
          <p className="empty-state-hint">Evidence appears after signal extraction and fusion</p>
        </div>
      ) : (
        <div className="evidence-list">
          {evidence.map((item) => (
            <div key={item.observationId} className="evidence-item">
              <div className="evidence-header">
                <span className="evidence-type">{item.observationType}</span>
                <span className="evidence-confidence">
                  {typeof item.confidence === 'number' ? `${Math.round(item.confidence * 100)}%` : 'n/a'}
                </span>
              </div>
              <div className="evidence-id">Observation: {item.observationId}</div>
              <div className="evidence-description">{item.description}</div>
              <div className="evidence-meta">
                <span>Event: {item.eventId}</span>
                <span>Signals: {item.sourceSignalIds?.length || 0}</span>
                <span>Observed: {formatTime(item.timeReference?.timestamp || item.timeReference?.startTime)}</span>
                {item.location?.placeName ? <span>Location: {item.location.placeName}</span> : null}
                {item.provenance?.sourceRecordId ? <span>Source Record: {item.provenance.sourceRecordId}</span> : null}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default EvidencePanel;
