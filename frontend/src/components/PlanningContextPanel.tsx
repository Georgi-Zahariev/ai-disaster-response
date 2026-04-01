/**
 * Planning Context Panel
 *
 * Shows optional planning enrichment and keeps it visually distinct from live evidence.
 */

import type { PlanningContextView } from '../types/incident';

interface PlanningContextPanelProps {
  planningContext?: PlanningContextView | null;
}

const MAX_MATCHES_PER_CASE = 8;
const MAX_ACTIONS_PER_CASE = 5;
const PANEL_TITLE = 'Planning Baseline';
const PANEL_SUBTITLE = 'Historical and seasonal context for preparedness. Not used as live incident evidence.';
const PANEL_BADGE = 'Non-live planning context';

function normalizeText(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function dedupeMatches(matches: Array<Record<string, any>>): Array<Record<string, any>> {
  const seen = new Set<string>();
  const unique: Array<Record<string, any>> = [];

  for (const match of matches) {
    const concept = normalizeText(match?.concept).toLowerCase();
    const summary = normalizeText(match?.summary);
    const key = `${concept}::${summary.toLowerCase()}`;
    if (!summary || seen.has(key)) {
      continue;
    }
    seen.add(key);
    unique.push(match);
  }

  return unique;
}

function formatCorridor(match: Record<string, any>): string {
  const corridor = normalizeText(match?.corridorRef);
  if (corridor) {
    return corridor.replace(':', ' / ');
  }
  return normalizeText(match?.county) || 'this area';
}

function formatSeason(match: Record<string, any>): string {
  const validity = match?.validity as Record<string, any> | undefined;
  if (!validity || typeof validity !== 'object') {
    return '';
  }

  const season = normalizeText(validity.season).replace(/_/g, ' ');
  const startMonth = validity.startMonth;
  const endMonth = validity.endMonth;
  if (season && typeof startMonth === 'number' && typeof endMonth === 'number') {
    return `${season} (${startMonth}-${endMonth})`;
  }
  if (season) {
    return season;
  }
  return '';
}

function buildCaseActions(entry: PlanningContextView['matchesByCase'][number]): string[] {
  const actions: string[] = [];
  const seen = new Set<string>();

  for (const match of dedupeMatches(entry.matches || [])) {
    const concept = normalizeText(match?.concept).toLowerCase();
    const corridor = formatCorridor(match);
    const season = formatSeason(match);
    const summary = normalizeText(match?.summary);
    let action = '';

    if (concept === 'known_bottleneck') {
      action = `For ${corridor}, pre-stage detour control and keep at least one fuel and one grocery access corridor open.`;
    } else if (concept === 'seasonal_risk') {
      action = `For ${corridor}${season ? ` during ${season}` : ''}, stage crews and pumps early and pre-position route closure signage.`;
    } else if (concept === 'historical_pattern') {
      action = `For ${corridor}, use historical delay behavior to dispatch earlier and assign quick-clear units before peak queue windows.`;
    }

    if (!action) {
      continue;
    }

    const detailed = summary ? `${action} Evidence: ${summary}` : action;
    if (!seen.has(detailed)) {
      seen.add(detailed);
      actions.push(detailed);
    }

    if (actions.length >= MAX_ACTIONS_PER_CASE) {
      break;
    }
  }

  return actions;
}

function PlanningContextPanel({ planningContext }: PlanningContextPanelProps) {
  const matchesByCase = Array.isArray(planningContext?.matchesByCase)
    ? planningContext.matchesByCase
    : [];
  const recordCount = typeof planningContext?.recordCount === 'number'
    ? planningContext.recordCount
    : 0;

  if (!planningContext?.requested) {
    return (
      <div className="panel planning-panel planning-panel-muted">
        <h2>{PANEL_TITLE}</h2>
        <div className="empty-state">
          <p>Planning enrichment was not enabled for this run.</p>
          <p className="empty-state-hint">Enable planning mode to include historical bottlenecks, seasonal route risk, and preparedness context.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel planning-panel">
      <h2>{PANEL_TITLE}</h2>
      <p className="panel-subtitle">{PANEL_SUBTITLE}</p>
      <div className="planning-badge">{PANEL_BADGE}</div>

      <div className="planning-summary">
        <div>Records: {recordCount}</div>
        <div>Matched Cases: {matchesByCase.length}</div>
      </div>

      {matchesByCase.length > 0 && (
        <div className="planning-actions">
          <h3>Case-Specific Planning Actions (from historical baseline)</h3>
          <div className="planning-actions-by-case">
            {matchesByCase.map((entry) => {
              const actions = buildCaseActions(entry);
              if (!actions.length) {
                return null;
              }
              const eventType = normalizeText(entry?.eventType) || 'case';
              const eventId = normalizeText(entry?.eventId) || 'unknown-case';
              return (
                <div key={`actions-${eventId}`} className="planning-action-case">
                  <div className="planning-action-case-header">
                    <strong>{eventType}</strong>
                    <span>{eventId}</span>
                  </div>
                  <ul>
                    {actions.map((action, idx) => (
                      <li key={`plan-action-${eventId}-${idx}`}>{action}</li>
                    ))}
                  </ul>
                  {dedupeMatches(entry.matches || []).length > MAX_MATCHES_PER_CASE && (
                    <p className="empty-state-hint">
                      Evidence basis is condensed for readability.
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {matchesByCase.length === 0 && (
        <div className="empty-state">
          <p>No planning baseline matches for current cases.</p>
          <p className="empty-state-hint">Historical planning context loaded, but no corridor-level matches were found.</p>
        </div>
      )}
    </div>
  );
}

export default PlanningContextPanel;
