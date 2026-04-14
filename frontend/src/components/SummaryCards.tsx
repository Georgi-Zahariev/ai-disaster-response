/**
 * Summary Cards Component
 * 
 * Displays key metrics and statistics at a glance.
 */

import type { SummaryCardData } from '../types/ui';
import type { AlertRecommendation, FusedCase, PlanningContextView } from '../types/incident';

interface SummaryCardsProps {
  cases?: FusedCase[];
  alerts?: AlertRecommendation[];
  planningContext?: PlanningContextView | null;
  selectedCaseId?: string | null;
}

/**
 * KPI definitions (operator-facing):
 * - Active incidents: count(cases)
 * - Critical alerts: count(alerts where priority is urgent/high)
 * - Impacted fuel facilities: unique case.facilities.relatedFuelFacilityIds
 * - Impacted grocery facilities: unique case.facilities.relatedGroceryFacilityIds
 * - Active weather/hazard signals: sum(case.weatherHazard.conceptCounts values)
 * - Planning matches (non-live): deduped planningContext.matchesByCase only when isLiveEvidence=false
 */

function SummaryCards({
  cases = [],
  alerts = [],
  planningContext = null,
  selectedCaseId = null,
}: SummaryCardsProps) {
  const cards: SummaryCardData[] = buildKpiCards(cases, alerts, planningContext);

  const getSeverityClass = (severity?: string) => {
    if (!severity) return '';
    return `card-${severity}`;
  };

  return (
    <>
      <p className="panel-subtitle">
        Global operational KPIs across all active incidents.
        {selectedCaseId ? ` Selected incident filters map/evidence/actions only (${selectedCaseId}).` : ''}
      </p>
      <div className="summary-cards">
        {cards.map((card, index) => {
          const isPlanningCard = card.label.toLowerCase().includes('planning matches');
          return (
          <div 
            key={index} 
            className={`summary-card ${getSeverityClass(card.severity)} ${isPlanningCard ? 'summary-card-secondary' : ''}`}
          >
            <div className="card-label" title={card.helpText || card.label}>{card.label}</div>
          <div className="card-value">{card.value}</div>
          {card.trend && (
            <div className={`card-trend trend-${card.trend}`}>
              {card.trend === 'up' && '↑'}
              {card.trend === 'down' && '↓'}
              {card.trend === 'stable' && '→'}
              {card.changePercent && ` ${Math.abs(card.changePercent)}%`}
            </div>
          )}
          </div>
          );
        })}
      </div>
    </>
  );
}

function uniqueCount(values: string[]): number {
  return new Set(values.filter(Boolean)).size;
}

function countPlanningMatches(planningContext?: PlanningContextView | null): number {
  if (!planningContext || planningContext.isLiveEvidence !== false) {
    return 0;
  }

  const deduped = new Set<string>();
  for (const entry of planningContext.matchesByCase || []) {
    for (const match of entry.matches || []) {
      const concept = typeof match?.concept === 'string' ? match.concept.trim().toLowerCase() : '';
      const summary = typeof match?.summary === 'string' ? match.summary.trim().toLowerCase() : '';
      const key = `${entry.eventId || 'unknown'}::${concept}::${summary}`;
      if (concept || summary) {
        deduped.add(key);
      }
    }
  }
  return deduped.size;
}

function buildKpiCards(
  cases: FusedCase[],
  alerts: AlertRecommendation[],
  planningContext?: PlanningContextView | null,
): SummaryCardData[] {
  const activeIncidents = cases.length;
  const criticalAlerts = alerts.filter((item) => {
    const priority = (item.priority || '').toLowerCase();
    return priority === 'urgent' || priority === 'high';
  }).length;
  const impactedFuelFacilities = uniqueCount(
    cases.flatMap((item) => item.facilities?.relatedFuelFacilityIds || [])
  );
  const impactedGroceryFacilities = uniqueCount(
    cases.flatMap((item) => item.facilities?.relatedGroceryFacilityIds || [])
  );
  const activeWeatherSignals = cases.reduce((sum, item) => {
    const counts = item.weatherHazard?.conceptCounts || {};
    return sum + Object.values(counts).reduce<number>((inner, value) => inner + Number(value ?? 0), 0);
  }, 0);
  const planningMatches = countPlanningMatches(planningContext);

  return [
    {
      label: 'Active Incidents',
      value: activeIncidents,
      severity: activeIncidents > 0 ? 'moderate' : 'info',
      helpText: 'Live/derived: total active fused incident cases.',
    },
    {
      label: 'Critical Alerts',
      value: criticalAlerts,
      severity: criticalAlerts > 0 ? 'critical' : 'info',
      helpText: 'Live/derived: active alerts with urgent or high priority.',
    },
    {
      label: 'Impacted Fuel Facilities',
      value: impactedFuelFacilities,
      severity: impactedFuelFacilities > 0 ? 'high' : 'info',
      helpText: 'Live/derived: unique fuel facilities impacted across active incidents.',
    },
    {
      label: 'Impacted Grocery Facilities',
      value: impactedGroceryFacilities,
      severity: impactedGroceryFacilities > 0 ? 'high' : 'info',
      helpText: 'Live/derived: unique grocery facilities impacted across active incidents.',
    },
    {
      label: 'Active Weather/Hazard Signals',
      value: activeWeatherSignals,
      severity: activeWeatherSignals > 0 ? 'moderate' : 'info',
      helpText: 'Live/derived: summed weather/hazard signal counts tied to active incidents.',
    },
    {
      label: 'Planning Matches (Non-live Baseline)',
      value: planningMatches,
      severity: planningMatches > 0 ? 'low' : 'info',
      helpText: 'Non-live/derived: deduped planning baseline matches; excluded from live impact counts.',
    },
  ];
}

export default SummaryCards;
