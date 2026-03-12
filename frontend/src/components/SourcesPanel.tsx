/**
 * Sources Panel Component
 * 
 * Displays active data sources and their status.
 */

import type { SourceCardData } from '../types/ui';
import type { IncidentAnalysisResponse } from '../types/incident';

interface SourcesPanelProps {
  response: IncidentAnalysisResponse | null;
}

function SourcesPanel({ response }: SourcesPanelProps) {
  // Build sources from response metadata and events
  const sources: SourceCardData[] = response ? buildSourcesFromResponse(response) : [];

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'text':
        return '📝';
      case 'vision':
        return '📷';
      case 'quantitative':
        return '📊';
      default:
        return '📡';
    }
  };

  const getStatusClass = (status: string) => {
    return `source-status-${status}`;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="panel sources-panel">
      <h2>Data Sources</h2>
      
      {sources.length === 0 ? (
        <div className="empty-state">
          <p>No active sources</p>
          <p className="empty-state-hint">
            Data source feeds will appear here
          </p>
        </div>
      ) : (
        <div className="sources-list">
          {sources.map((source) => (
            <div key={source.sourceId} className="source-item">
              <div className="source-header">
                <span className="source-icon">{getSourceIcon(source.sourceType)}</span>
                <span className="source-name">{source.sourceName}</span>
                <span className={`source-status ${getStatusClass(source.status)}`}>
                  {source.status}
                </span>
              </div>
              <div className="source-meta">
                <span className="source-type">{source.sourceType}</span>
                {source.signalCount !== undefined && (
                  <span className="source-count">{source.signalCount} signals</span>
                )}
                <span className="source-update">
                  {formatTimestamp(source.lastUpdate)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Build source cards from response data
 */
function buildSourcesFromResponse(response: IncidentAnalysisResponse): SourceCardData[] {
  const sources: SourceCardData[] = [];
  const sourceMap = new Map<string, { signalCount: number; latestTime: string }>();

  // Extract unique source types from events' source signal IDs
  response.events?.forEach((event) => {
    event.sourceSignalIds?.forEach((signalId) => {
      // Extract source type from signal ID pattern (e.g., "text-001" -> "text", "vision-001" -> "vision")
      const match = signalId.match(/^(\w+)-/);
      if (match) {
        const sourceType = match[1];
        const existing = sourceMap.get(sourceType);
        const timestamp = event.detectedAt || event.timeReference?.timestamp || new Date().toISOString();
        
        if (existing) {
          existing.signalCount++;
          // Keep the latest timestamp
          if (new Date(timestamp) > new Date(existing.latestTime)) {
            existing.latestTime = timestamp;
          }
        } else {
          sourceMap.set(sourceType, { signalCount: 1, latestTime: timestamp });
        }
      }
    });
  });

  // Convert to SourceCardData array
  let index = 0;
  sourceMap.forEach((data, sourceName) => {
    sources.push({
      sourceId: `source-${index++}`,
      sourceName: formatSourceName(sourceName),
      sourceType: mapToSourceType(sourceName),
      status: 'active',
      lastUpdate: data.latestTime,
      signalCount: data.signalCount,
    });
  });

  // Sort by signal count descending
  return sources.sort((a, b) => (b.signalCount || 0) - (a.signalCount || 0));
}

/**
 * Format source name for display
 */
function formatSourceName(rawName: string): string {
  const nameMap: Record<string, string> = {
    'text': 'Text Feeds',
    'vision': 'Vision/Satellite',
    'quant': 'Quantitative Data',
    'quantitative': 'Quantitative Data',
  };
  
  return nameMap[rawName.toLowerCase()] || rawName
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Infer source type from name and map to specific type
 */
function mapToSourceType(sourceName: string): 'text' | 'vision' | 'quantitative' {
  const lower = sourceName.toLowerCase();
  if (lower.includes('vision') || lower.includes('satellite') || lower.includes('image')) return 'vision';
  if (lower.includes('quant') || lower.includes('data') || lower.includes('sensor')) return 'quantitative';
  return 'text'; // default
}

export default SourcesPanel;
