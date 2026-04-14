/**
 * Main Dashboard Page
 * 
 * Displays the disaster response dashboard with:
 * - Incident input form
 * - Summary cards
 * - Alerts panel
 * - Fused events panel
 * - Sources panel
 * - Activity log
 * - Map placeholder
 */

import { useEffect, useState } from 'react';
import IncidentForm from '../components/IncidentForm';
import SummaryCards from '../components/SummaryCards';
import AlertsPanel from '../components/AlertsPanel';
import FusedEventsPanel from '../components/FusedEventsPanel';
import EvidencePanel from '../components/EvidencePanel';
import PlanningContextPanel from '../components/PlanningContextPanel';
import DashboardSummaryPanel from '../components/DashboardSummaryPanel';
import MapPlaceholder from '../components/MapPlaceholder';
import DataReadinessPanel from '../components/DataReadinessPanel';
import CurrentOperationalFocusCard from '../components/CurrentOperationalFocusCard';
import { analyzeIncident, APIError, fetchFacilities, fetchReadinessSnapshot } from '../services/api';
import { createIncidentRequest } from '../types/incident';
import type { IncidentInputData } from '../types/ui';
import type { FacilitiesResponse, IncidentAnalysisResponse, ReadinessSnapshotResponse } from '../types/incident';

function formatTimestamp(timestamp?: string | null): string {
  if (!timestamp) {
    return 'n/a';
  }
  return new Date(timestamp).toLocaleString();
}

function formatRecency(timestamp?: string | null): string {
  if (!timestamp) {
    return 'n/a';
  }
  const deltaMs = Date.now() - new Date(timestamp).getTime();
  const minutes = Math.max(0, Math.floor(deltaMs / 60000));
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function Dashboard() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResponse, setAnalysisResponse] = useState<IncidentAnalysisResponse | null>(null);
  const [facilitiesData, setFacilitiesData] = useState<FacilitiesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [readiness, setReadiness] = useState<ReadinessSnapshotResponse | null>(null);
  const [readinessLoading, setReadinessLoading] = useState(true);
  const [readinessError, setReadinessError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const loadReadiness = async () => {
      setReadinessLoading(true);
      setReadinessError(null);

      try {
        const snapshot = await fetchReadinessSnapshot(2);
        if (!active) {
          return;
        }
        setReadiness(snapshot);
      } catch (err) {
        if (!active) {
          return;
        }
        setReadinessError(err instanceof Error ? err.message : 'Failed to fetch readiness snapshot');
      } finally {
        if (active) {
          setReadinessLoading(false);
        }
      }
    };

    loadReadiness();

    return () => {
      active = false;
    };
  }, []);

  const handleIncidentSubmit = async (data: IncidentInputData) => {
    setIsProcessing(true);
    setError(null);
    setAnalysisResponse(null); // Clear previous results before new request
    setFacilitiesData(null);
    setSelectedCaseId(null);
    
    try {
      // Convert form data to API request format
      const request = createIncidentRequest(data);
      
      // Call backend API
      const response = await analyzeIncident(request);

      if (response.status === 'error') {
        const firstError = Array.isArray(response.errors) ? response.errors[0] : undefined;
        setError('Unable to complete incident analysis. Please verify incident details and try again.');
        if (firstError) {
          console.warn('Incident analysis returned error status', firstError);
        }
        setAnalysisResponse(null);
        setSelectedCaseId(null);
        return;
      }
      
      // Update state with successful response
      setAnalysisResponse(response);
      setSelectedCaseId(response.cases?.[0]?.caseId || response.events?.[0]?.eventId || null);

      // Fetch coordinate-bearing facility baseline for map markers.
      // Analyze response includes counts/IDs, but not full facility objects.
      const expectedFacilities = response.summary?.facilities?.baselineCount
        || response.metadata?.facilityBaselineCount
        || response.metadata?.fusionSummary?.facilityBaselineCount
        || 0;

      if (expectedFacilities > 0) {
        try {
          const facilityPayload = await fetchFacilities(expectedFacilities);
          setFacilitiesData(facilityPayload);
        } catch (facilityErr) {
          setFacilitiesData({
            totalAvailable: 0,
            returnedCount: 0,
            records: [],
            warnings: [
              facilityErr instanceof Error
                ? `Facilities fetch failed: ${facilityErr.message}`
                : 'Facilities fetch failed',
            ],
          });
        }
      } else {
        setFacilitiesData({ totalAvailable: 0, returnedCount: 0, records: [], warnings: [] });
      }
    } catch (err) {
      // Handle errors
      if (err instanceof APIError) {
        setError('Unable to complete incident analysis. Showing last stable dashboard state.');
      } else {
        setError('Unable to complete incident analysis. Showing last stable dashboard state.');
      }
      console.error('Incident analysis error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDismissError = () => {
    setError(null);
  };

  const selectedCaseTitle = analysisResponse?.cases?.find((item) => item.caseId === selectedCaseId)?.event?.title || null;
  const allEvidence = analysisResponse?.evidence || [];
  const allAlerts = analysisResponse?.alerts || [];

  const evidenceForPanel = selectedCaseId
    ? [...allEvidence].sort((a, b) => Number(b.eventId === selectedCaseId) - Number(a.eventId === selectedCaseId))
    : allEvidence;

  const alertsForPanel = selectedCaseId
    ? [...allAlerts].sort((a, b) => Number(b.eventId === selectedCaseId) - Number(a.eventId === selectedCaseId))
    : allAlerts;

  const selectedEvidence = selectedCaseId
    ? allEvidence.filter((item) => item.eventId === selectedCaseId)
    : allEvidence;

  const selectedAlerts = selectedCaseId
    ? allAlerts.filter((alert) => alert.eventId === selectedCaseId)
    : allAlerts;

  const planningContextForSelection = (() => {
    const source = analysisResponse?.planningContext;
    if (!source || !selectedCaseId) {
      return source || null;
    }

    return {
      ...source,
      matchesByCase: (source.matchesByCase || []).filter((entry) => entry.eventId === selectedCaseId),
    };
  })();

  const selectedCase = analysisResponse?.cases?.find((item) => item.caseId === selectedCaseId) || null;
  const hasPartialData = analysisResponse?.status === 'partial' || analysisResponse?.status === 'partial_success';
  const hasWarnings = (analysisResponse?.warnings || []).length > 0;
  const lastProcessedAt = analysisResponse?.processedAt || null;

  const handleSelectCase = (caseId: string) => {
    setSelectedCaseId(caseId);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Tampa Bay Route Access Decision Support</h1>
        <p className="subtitle">Hillsborough · Pinellas · Pasco | Live disruption monitoring with separate non-live planning baseline</p>
        <div className="header-freshness">
          <span>Last analysis update: {formatTimestamp(lastProcessedAt)}</span>
          <span>Freshness: {formatRecency(lastProcessedAt)}</span>
        </div>
      </header>

      <div className="operations-layout">
        {(hasPartialData || hasWarnings) && (
          <div className="error-banner operations-error-banner ops-info-banner">
            <div className="error-content">
              <span className="error-icon">ℹ️</span>
              <span className="error-message">
                Analysis completed with partial/degraded inputs. Operator guidance is available; verify linked evidence before escalation.
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="error-banner operations-error-banner">
            <div className="error-content">
              <span className="error-icon">⚠️</span>
              <span className="error-message">{error}</span>
              <button 
                className="error-dismiss" 
                onClick={handleDismissError}
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          </div>
        )}

        <aside className="operations-rail operations-left-rail">
          <div className="report-utility-panel">
            <details className="report-utility" open={false}>
              <summary>Submit Incident Report</summary>
              <p className="report-utility-helper">
                Utility input for adding a new disruption report. Regional monitoring remains active regardless of submissions.
              </p>
              <IncidentForm
                onSubmit={handleIncidentSubmit}
                isProcessing={isProcessing}
              />
            </details>
          </div>

          <EvidencePanel
            evidence={evidenceForPanel}
            selectedCaseId={selectedCaseId}
            selectedCaseTitle={selectedCaseTitle}
            isProcessing={isProcessing}
          />
        </aside>

        <main className="operations-main-stage">
          <SummaryCards
            cases={analysisResponse?.cases || []}
            alerts={analysisResponse?.alerts || []}
            planningContext={analysisResponse?.planningContext || null}
            selectedCaseId={selectedCaseId}
          />

          <CurrentOperationalFocusCard
            selectedCase={selectedCase}
            selectedAlerts={selectedAlerts}
            selectedEvidence={selectedEvidence}
            planningContext={analysisResponse?.planningContext || null}
          />

          <DataReadinessPanel
            readiness={readiness}
            loading={readinessLoading}
            error={readinessError}
          />

          <MapPlaceholder
            map={analysisResponse?.map || null}
            fallbackFeatures={[]}
            summary={analysisResponse?.summary || null}
            evidence={analysisResponse?.evidence || []}
            facilitiesData={facilitiesData}
            planningContext={planningContextForSelection}
            selectedCaseId={selectedCaseId}
            dataUpdatedAt={analysisResponse?.processedAt || null}
            isProcessing={isProcessing}
            hasError={Boolean(error)}
          />

          {!analysisResponse && !isProcessing && !error && (
            <div className="panel operations-state-panel">
              <h3>Regional Monitoring Active</h3>
              <p>
                No active disruption case is currently selected. The map remains focused on Tampa Bay and will update as new incidents or alerts are ingested.
              </p>
            </div>
          )}

          {isProcessing && (
            <div className="panel operations-state-panel loading">
              <h3>Updating Regional View</h3>
              <p>Analyzing incoming reports and refreshing case, alert, and map context.</p>
            </div>
          )}

          <DashboardSummaryPanel
            dashboardSummary={analysisResponse?.dashboard?.data || null}
            isProcessing={isProcessing}
          />

          <PlanningContextPanel
            planningContext={planningContextForSelection}
            selectedCaseId={selectedCaseId}
            isProcessing={isProcessing}
          />
        </main>

        <aside className="operations-rail operations-right-rail">
          <AlertsPanel
            alerts={alertsForPanel}
            selectedCaseId={selectedCaseId}
            selectedCaseTitle={selectedCaseTitle}
            onSelectCase={handleSelectCase}
            isProcessing={isProcessing}
          />
          <FusedEventsPanel
            cases={analysisResponse?.cases || []}
            selectedCaseId={selectedCaseId}
            onSelectCase={handleSelectCase}
            isProcessing={isProcessing}
          />
        </aside>
      </div>
    </div>
  );
}

export default Dashboard;
