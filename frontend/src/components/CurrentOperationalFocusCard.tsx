import type { AlertRecommendation, EvidenceRecord, FusedCase, PlanningContextView } from '../types/incident';

interface CurrentOperationalFocusCardProps {
  selectedCase: FusedCase | null;
  selectedAlerts: AlertRecommendation[];
  selectedEvidence: EvidenceRecord[];
  planningContext: PlanningContextView | null;
}

function formatTimestamp(timestamp?: string): string {
  if (!timestamp) {
    return '';
  }
  return new Date(timestamp).toLocaleString();
}

function formatRecency(timestamp?: string): string {
  if (!timestamp) {
    return '';
  }

  const deltaMs = Date.now() - new Date(timestamp).getTime();
  const deltaMinutes = Math.max(0, Math.floor(deltaMs / 60000));
  if (deltaMinutes < 1) {
    return 'just now';
  }
  if (deltaMinutes < 60) {
    return `${deltaMinutes}m ago`;
  }
  const deltaHours = Math.floor(deltaMinutes / 60);
  if (deltaHours < 24) {
    return `${deltaHours}h ago`;
  }
  const deltaDays = Math.floor(deltaHours / 24);
  return `${deltaDays}d ago`;
}

function getTopActions(caseItem: FusedCase, alerts: AlertRecommendation[]): string[] {
  const actionsFromAlerts = alerts.flatMap((item) => item.recommendedActions || []);
  const actionsFromAssessment = caseItem.assessment?.recommendations || [];
  const deduped: string[] = [];
  const seen = new Set<string>();

  [...actionsFromAlerts, ...actionsFromAssessment].forEach((action) => {
    const normalized = String(action || '').trim();
    if (!normalized) {
      return;
    }
    const key = normalized.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      deduped.push(normalized);
    }
  });

  return deduped.slice(0, 3);
}

function getPlanningMatchCount(planningContext: PlanningContextView | null, caseId: string): number {
  if (!planningContext || planningContext.isLiveEvidence !== false) {
    return 0;
  }
  const row = (planningContext.matchesByCase || []).find((item) => item.eventId === caseId);
  return row?.matches?.length || 0;
}

function CurrentOperationalFocusCard({
  selectedCase,
  selectedAlerts,
  selectedEvidence,
  planningContext,
}: CurrentOperationalFocusCardProps) {
  if (!selectedCase) {
    return (
      <div className="panel current-focus-panel current-focus-empty">
        <h2>Current Operational Focus</h2>
        <p className="panel-subtitle">Select an active incident to inspect operational details, actions, and supporting evidence.</p>
      </div>
    );
  }

  const event = selectedCase.event;
  const countyOrArea = event.location?.region || event.location?.placeName || event.location?.locationName || 'unknown area';
  const routeCorridors = selectedCase.routeTraffic?.routeIds || [];
  const impactedDimensions: string[] = [];

  if ((selectedCase.facilities?.relatedFuelFacilityIds || []).length > 0) {
    impactedDimensions.push('fuel-access');
  }
  if ((selectedCase.facilities?.relatedGroceryFacilityIds || []).length > 0) {
    impactedDimensions.push('grocery-access');
  }
  if (Object.keys(selectedCase.weatherHazard?.conceptCounts || {}).length > 0) {
    impactedDimensions.push('weather/hazard corroboration');
  }
  if (routeCorridors.length > 0) {
    impactedDimensions.push('route-access');
  }

  const topActions = getTopActions(selectedCase, selectedAlerts);
  const updateTimestamp = event.updatedAt || event.timeReference?.timestamp || event.timeReference?.startTime;
  const hasTimestamp = Boolean(updateTimestamp);
  const planningMatches = getPlanningMatchCount(planningContext, selectedCase.caseId);

  return (
    <div className="panel current-focus-panel">
      <h2>Current Operational Focus</h2>
      <p className="panel-subtitle">Selected incident view for decisions on route, fuel, and grocery continuity.</p>

      <div className={`current-focus-header ${hasTimestamp ? '' : 'no-timestamps'}`}>
        <div>
          <div className="focus-title">{event.title || selectedCase.caseId}</div>
          <div className="focus-meta">Severity: {event.severity} | Confidence: {Math.round((event.confidence || 0) * 100)}%</div>
        </div>
        {hasTimestamp ? (
          <div className="focus-timestamps">
            <div>Updated: {formatTimestamp(updateTimestamp)}</div>
            <div>Recency: {formatRecency(updateTimestamp)}</div>
          </div>
        ) : null}
      </div>

      <div className="current-focus-grid">
        <div><strong>Affected county/area:</strong> {countyOrArea}</div>
        <div><strong>Affected corridor:</strong> {routeCorridors.length ? routeCorridors.join(', ') : 'not specified'}</div>
        <div><strong>Impacted access dimensions:</strong> {impactedDimensions.length ? impactedDimensions.join(', ') : 'under assessment'}</div>
        <div><strong>Supporting evidence:</strong> {selectedEvidence.length} live observations</div>
      </div>

      <div className="current-focus-narrative">
        <h3>Operator Narrative</h3>
        <p><strong>What changed:</strong> {event.description || 'A disruption case is active and requires operational review.'}</p>
        <p><strong>What is at risk:</strong> {impactedDimensions.length ? impactedDimensions.join(', ') : 'route and access continuity in the selected area'}.</p>
        <p><strong>What to do next:</strong> Execute the top response actions below and monitor linked alerts/evidence for escalation.</p>
        <p><strong>Supporting evidence:</strong> {selectedEvidence.length} live observations, {selectedAlerts.length} linked alerts, {planningMatches} planning matches (non-live).</p>
      </div>

      <div className="current-focus-actions">
        <h3>Top 3 Recommended Actions</h3>
        {topActions.length === 0 ? (
          <p className="empty-state-hint">No explicit actions yet. Continue monitoring alerts and evidence for next operational step.</p>
        ) : (
          <ul>
            {topActions.map((action, index) => (
              <li key={`focus-action-${index}`}>{action}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default CurrentOperationalFocusCard;
