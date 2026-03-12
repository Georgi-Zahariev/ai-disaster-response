/**
 * Summary Cards Component
 * 
 * Displays key metrics and statistics at a glance.
 */

import type { SummaryCardData } from '../types/ui';
import type { DashboardSummary } from '../types/incident';

interface SummaryCardsProps {
  summary: DashboardSummary | null;
}

function SummaryCards({ summary }: SummaryCardsProps) {
  // Build cards from dashboard summary data
  const cards: SummaryCardData[] = summary ? buildCardsFromSummary(summary) : getEmptyCards();

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
function buildCardsFromSummary(summary: DashboardSummary): SummaryCardData[] {
  // Get total events from eventsBySeverity
  const totalEvents = summary.eventsBySeverity?.reduce((sum, e) => sum + e.count, 0) || 0;
  
  // Get critical and urgent alert counts
  const criticalAlerts = (summary.alerts?.urgent || 0) + (summary.alerts?.high || 0);
  
  // Find affected population from key metrics or calculate from events
  const populationMetric = summary.keyMetrics?.find(m => 
    m.label.toLowerCase().includes('population') || m.label.toLowerCase().includes('affected')
  );
  const affectedPopulation = populationMetric?.value?.toString() || '0';
  
  // Get disrupted sectors count
  const sectorsCount = summary.sectorDisruptions?.length || 0;

  return [
    { 
      label: 'Active Events', 
      value: totalEvents, 
      severity: mapSeverity(summary.situationStatus?.overallSeverity) || 'info',
      trend: getOverallTrend(summary.eventsBySeverity),
    },
    { 
      label: 'Critical Alerts', 
      value: criticalAlerts, 
      severity: criticalAlerts > 0 ? 'critical' : 'info',
    },
    { 
      label: 'Affected Population', 
      value: affectedPopulation, 
      severity: getSeverityFromPopulation(affectedPopulation),
      trend: populationMetric?.trend as 'up' | 'down' | 'stable' | undefined,
    },
    { 
      label: 'Disrupted Sectors', 
      value: sectorsCount, 
      severity: sectorsCount > 2 ? 'high' : 'moderate',
    },
  ];
}

/**
 * Get empty cards for initial state
 */
function getEmptyCards(): SummaryCardData[] {
  return [
    { label: 'Active Events', value: 0, severity: 'info' },
    { label: 'Critical Alerts', value: 0, severity: 'info' },
    { label: 'Affected Population', value: '0', severity: 'info' },
    { label: 'Disrupted Sectors', value: 0, severity: 'info' },
  ];
}

/**
 * Get overall trend from events by severity
 */
function getOverallTrend(events?: Array<{ severity: string; count: number; trend?: string }>): 'up' | 'down' | 'stable' | undefined {
  if (!events || events.length === 0) return undefined;
  
  const criticalEvents = events.find(e => e.severity === 'critical');
  if (criticalEvents?.trend) {
    if (criticalEvents.trend === 'increasing') return 'up';
    if (criticalEvents.trend === 'decreasing') return 'down';
    if (criticalEvents.trend === 'stable') return 'stable';
  }
  
  return undefined;
}

/**
 * Get severity from population value string
 */
function getSeverityFromPopulation(value: string): 'critical' | 'high' | 'moderate' | 'low' | 'info' {
  const numericValue = parseFloat(value.replace(/[^0-9.]/g, ''));
  const multiplier = value.includes('K') ? 1000 : value.includes('M') ? 1000000 : 1;
  const total = numericValue * multiplier;
  
  if (total > 100000) return 'critical';
  if (total > 10000) return 'high';
  if (total > 1000) return 'moderate';
  return 'low';
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
