/**
 * Planning Context Panel
 *
 * Shows optional planning enrichment and keeps it visually distinct from live evidence.
 */

import { useState } from 'react';
import type { PlanningContextView } from '../types/incident';

interface PlanningContextPanelProps {
  planningContext?: PlanningContextView | null;
  selectedCaseId?: string | null;
  isProcessing?: boolean;
}

const DEFAULT_VISIBLE_ACTIONS = 5;
const PANEL_TITLE = 'Planning Baseline';
const PANEL_SUBTITLE = 'Preparatory baseline guidance from historical and seasonal patterns only. This panel is non-live.';
const PANEL_BADGE = 'Non-live baseline (prep use only)';

type PlanningMatch = Record<string, any>;

interface PreparedAction {
  dedupeKey: string;
  actionText: string;
  evidenceText: string;
  reasonTag: string;
  groupKey: string;
  groupLabel: string;
  score: number;
}

function normalizeText(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function normalizeKey(value: unknown): string {
  const text = normalizeText(value).toLowerCase();
  return text.replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
}

function formatScopeLabel(match: PlanningMatch): string {
  const corridorRef = normalizeText(match?.corridorRef);
  const locality = normalizeText(match?.locality);
  const areaRef = normalizeText(match?.areaRef);
  const county = normalizeText(match?.county);

  if (corridorRef) {
    return corridorRef.replace(':', ' / ');
  }
  if (locality) {
    return locality;
  }
  if (areaRef) {
    return areaRef;
  }
  return county || 'operational area';
}

function formatSeason(match: PlanningMatch): string {
  const validity = match?.validity as PlanningMatch | undefined;
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

function toReasonTag(match: PlanningMatch): string {
  const existing = normalizeText(match?.reasonTag);
  if (existing) {
    return existing;
  }

  const concept = normalizeKey(match?.concept);
  const summary = normalizeKey(match?.summary);
  if (summary.includes('evac')) {
    return 'evacuation pressure';
  }
  if (concept === 'known bottleneck') {
    return 'historical bottleneck';
  }
  if (concept === 'seasonal risk') {
    return 'seasonal risk';
  }
  if (concept === 'historical pattern') {
    return 'prior delay pattern';
  }
  return 'planning baseline';
}

function toActionText(match: PlanningMatch): string {
  const existing = normalizeText(match?.action);
  if (existing) {
    return existing;
  }

  const concept = normalizeKey(match?.concept);
  const scope = formatScopeLabel(match);
  const season = formatSeason(match);

  if (concept === 'known bottleneck') {
    return `Pre-stage detour control for ${scope} and preserve one fuel and one grocery access route.`;
  }
  if (concept === 'seasonal risk') {
    return `Pre-position drainage and traffic-control resources for ${scope}${season ? ` during ${season}` : ''}.`;
  }
  if (concept === 'historical pattern') {
    return `Prepare earlier dispatch windows and quick-clear crews around ${scope}.`;
  }
  return `Use planning baseline to prepare route-access contingencies for ${scope}.`;
}

function buildPreparedActions(entry: PlanningContextView['matchesByCase'][number]): PreparedAction[] {
  const eventLink = normalizeText(entry?.eventId) || 'unknown-case';
  const deduped = new Map<string, PreparedAction>();

  for (const match of entry.matches || []) {
    const concept = normalizeKey(match?.concept);
    const county = normalizeKey(match?.county);
    const scope = normalizeKey(match?.corridorRef || match?.locality || match?.areaRef || match?.county);
    const actionText = toActionText(match);
    const evidenceText = normalizeText(match?.summary);
    const actionKey = normalizeKey(actionText);
    const evidenceKey = normalizeKey(evidenceText);
    const dedupeKey = `${normalizeKey(eventLink)}::${concept}::${county}::${scope}::${actionKey}::${evidenceKey}`;

    const groupLabel = formatScopeLabel(match);
    const groupKey = normalizeKey(groupLabel) || 'operational-area';
    const reasonTag = toReasonTag(match);
    const score = typeof match?.relevanceScore === 'number'
      ? match.relevanceScore
      : ((match?.corridorRef ? 2 : 0) + (match?.locality || match?.areaRef ? 1 : 0));

    const candidate: PreparedAction = {
      dedupeKey,
      actionText,
      evidenceText,
      reasonTag,
      groupKey,
      groupLabel,
      score,
    };

    const existing = deduped.get(dedupeKey);
    if (!existing || candidate.score > existing.score) {
      deduped.set(dedupeKey, candidate);
    }
  }

  return [...deduped.values()].sort((a, b) => {
    if (b.score !== a.score) {
      return b.score - a.score;
    }
    return a.actionText.localeCompare(b.actionText);
  });
}

function groupActions(actions: PreparedAction[]): Array<{ groupLabel: string; items: PreparedAction[] }> {
  const groups = new Map<string, { groupLabel: string; items: PreparedAction[] }>();

  for (const action of actions) {
    const existing = groups.get(action.groupKey);
    if (existing) {
      existing.items.push(action);
    } else {
      groups.set(action.groupKey, { groupLabel: action.groupLabel, items: [action] });
    }
  }

  return [...groups.values()]
    .map((group) => ({
      ...group,
      items: group.items.sort((a, b) => b.score - a.score),
    }))
    .sort((a, b) => {
      const topA = a.items[0]?.score || 0;
      const topB = b.items[0]?.score || 0;
      if (topB !== topA) {
        return topB - topA;
      }
      return a.groupLabel.localeCompare(b.groupLabel);
    });
}

function PlanningContextPanel({ planningContext, selectedCaseId = null, isProcessing = false }: PlanningContextPanelProps) {
  const [expandedByCase, setExpandedByCase] = useState<Record<string, boolean>>({});
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
        {isProcessing ? <p className="empty-state-hint">Refreshing planning baseline...</p> : null}
        <div className="empty-state">
          <p>Planning baseline was not enabled for this run.</p>
          <p className="empty-state-hint">Enable planning mode to include historical bottlenecks and seasonal preparedness context.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel planning-panel">
      <h2>{PANEL_TITLE}</h2>
      <p className="panel-subtitle">{PANEL_SUBTITLE}</p>
      <div className="planning-badge">{PANEL_BADGE}</div>
      {selectedCaseId ? <p className="empty-state-hint">Focused planning view: {selectedCaseId}</p> : null}
      {isProcessing ? <p className="empty-state-hint">Refreshing planning matches...</p> : null}

      <div className="planning-summary">
        <div>Records: {recordCount}</div>
        <div>Matched Cases: {matchesByCase.length}</div>
      </div>

      {matchesByCase.length > 0 && (
        <div className="planning-actions">
          <h3>Case-Specific Preparation Actions (non-live baseline)</h3>
          <div className="planning-actions-by-case">
            {matchesByCase.map((entry) => {
              const preparedActions = buildPreparedActions(entry);
              if (!preparedActions.length) {
                return null;
              }

              const eventType = normalizeText(entry?.eventType) || 'case';
              const eventId = normalizeText(entry?.eventId) || 'unknown-case';
              const expanded = Boolean(expandedByCase[eventId]);
              const visibleActions = expanded
                ? preparedActions
                : preparedActions.slice(0, DEFAULT_VISIBLE_ACTIONS);
              const hiddenCount = Math.max(0, preparedActions.length - visibleActions.length);
              const grouped = groupActions(visibleActions);

              return (
                <div key={`actions-${eventId}`} className="planning-action-case">
                  <div className="planning-action-case-header">
                    <strong>{eventType}</strong>
                    <span>{eventId}</span>
                  </div>

                  <p className="planning-item-non-live">Preparation guidance only. Not current observation evidence.</p>

                  {grouped.map((group) => (
                    <div key={`${eventId}-${group.groupLabel}`} className="planning-group-block">
                      <div className="planning-group-title">{group.groupLabel}</div>
                      <ul>
                        {group.items.map((item, idx) => (
                          <li key={`plan-action-${eventId}-${idx}-${item.dedupeKey}`}>
                            <div className="planning-action-line">{item.actionText}</div>
                            <div className="planning-item-meta">
                              <span className="planning-reason-tag">{item.reasonTag}</span>
                              <span className="planning-item-non-live">non-live prep</span>
                            </div>
                            {item.evidenceText ? (
                              <p className="empty-state-hint">Baseline basis: {item.evidenceText}</p>
                            ) : null}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}

                  {hiddenCount > 0 ? (
                    <button
                      type="button"
                      className="btn btn-secondary planning-show-more-btn"
                      onClick={() => {
                        setExpandedByCase((prev) => ({
                          ...prev,
                          [eventId]: !expanded,
                        }));
                      }}
                    >
                      {expanded ? 'Show top planning actions' : `Show ${hiddenCount} more planning actions`}
                    </button>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {matchesByCase.length === 0 && (
        <div className="empty-state">
          <p>No planning baseline matches for the current case selection.</p>
          <p className="empty-state-hint">Baseline data is loaded, but no corridor-level preparatory matches were found.</p>
        </div>
      )}
    </div>
  );
}

export default PlanningContextPanel;
