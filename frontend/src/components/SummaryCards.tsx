/**
 * Summary Cards Component
 * 
 * Displays key metrics and statistics at a glance.
 */

import type { SummaryCardData } from '../types/ui';
import type { DashboardSummary, MVPSummary } from '../types/incident';

interface SummaryCardsProps {
  summary: MVPSummary | null;
  legacySummary?: DashboardSummary | null;
}

function SummaryCards({ summary, legacySummary = null }: SummaryCardsProps) {
  // Build cards from dashboard summary data
  const cards: SummaryCardData[] = summary
    ? buildCardsFromMVPSummary(summary)
    : legacySummary
      ? buildCardsFromLegacySummary(legacySummary)
      : getEmptyCards();

  const getSeverityClass = (severity?: string) => {
    if (!severity) return '';
    return `card-${severity}`;
  };

  return (
    <div className="summary-cards">
      {cards.map((card, index) => (
        <div 
          key={index} 
          className={`summary-card ${getSeverityClass(card.severity)}`}
        >
          <div className="card-label">{card.label}</div>
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
      ))}
    </div>
  );
}

/**
 * Build summary cards from dashboard summary
 */
function buildCardsFromMVPSummary(summary: MVPSummary): SummaryCardData[] {
  const routeSignals = summary.signals?.routeTrafficSignals ?? 0;
  const weatherSignals = summary.signals?.weatherHazardSignals ?? 0;
  const facilityBaseline = summary.facilities?.baselineCount ?? 0;
  const planningRecords = summary.planningContext?.recordCount ?? 0;

  return [
    {
      label: 'Active Cases',
      value: summary.cases?.total ?? 0,
      severity: getCaseSeverity(summary),
    },
    {
      label: 'Route vs Weather Signals',
      value: `${routeSignals} / ${weatherSignals}`,
      severity: (routeSignals + weatherSignals) > 0 ? 'moderate' : 'info',
    },
    {
      label: 'Active Alerts',
      value: summary.alerts?.active ?? 0,
      severity: (summary.alerts?.active ?? 0) > 0 ? 'high' : 'info',
    },
    {
      label: 'Fuel+Grocery / Planning',
      value: `${facilityBaseline} / ${planningRecords}`,
      severity: planningRecords > 0 ? 'low' : 'info',
    },
  ];
}

function buildCardsFromLegacySummary(summary: DashboardSummary): SummaryCardData[] {
  const totalEvents = summary.eventsBySeverity?.reduce((sum, e) => sum + e.count, 0) || 0;
  const criticalAlerts = (summary.alerts?.urgent || 0) + (summary.alerts?.high || 0);
  const sectorsCount = summary.sectorDisruptions?.length || 0;
  return [
    { label: 'Active Cases', value: totalEvents, severity: mapSeverity(summary.situationStatus?.overallSeverity) || 'info' },
    { label: 'Critical Alerts', value: criticalAlerts, severity: criticalAlerts > 0 ? 'critical' : 'info' },
    { label: 'Affected Regions', value: summary.situationStatus?.affectedRegions?.length || 0, severity: 'low' },
    { label: 'Disrupted Sectors', value: sectorsCount, severity: sectorsCount > 2 ? 'high' : 'moderate' },
  ];
}

/**
 * Get empty cards for initial state
 */
function getEmptyCards(): SummaryCardData[] {
  return [
    { label: 'Active Cases', value: 0, severity: 'info' },
    { label: 'Route vs Weather Signals', value: '0 / 0', severity: 'info' },
    { label: 'Active Alerts', value: 0, severity: 'info' },
    { label: 'Fuel+Grocery / Planning', value: '0 / 0', severity: 'info' },
  ];
}

/**
 * Get overall trend from events by severity
 */
function getCaseSeverity(summary: MVPSummary): 'critical' | 'high' | 'moderate' | 'low' | 'info' {
  const sev = summary.cases?.severity || {};
  if ((sev.critical || 0) > 0) return 'critical';
  if ((sev.high || 0) > 0) return 'high';
  if ((sev.moderate || 0) > 0) return 'moderate';
  if ((sev.low || 0) > 0) return 'low';
  return 'info';
}

/**
 * Map severity string to card severity type
 */
function mapSeverity(severity?: string): 'critical' | 'high' | 'moderate' | 'low' | 'info' | undefined {
  if (!severity) return undefined;
  const normalized = severity.toLowerCase();
  if (['critical', 'high', 'moderate', 'low', 'info'].includes(normalized)) {
    return normalized as 'critical' | 'high' | 'moderate' | 'low' | 'info';
  }
  return 'info';
}

export default SummaryCards;
