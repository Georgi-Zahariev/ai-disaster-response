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

import { useState } from 'react';
import IncidentForm from '../components/IncidentForm';
import SummaryCards from '../components/SummaryCards';
import AlertsPanel from '../components/AlertsPanel';
import FusedEventsPanel from '../components/FusedEventsPanel';
import EvidencePanel from '../components/EvidencePanel';
import PlanningContextPanel from '../components/PlanningContextPanel';
import DashboardSummaryPanel from '../components/DashboardSummaryPanel';
import MapPlaceholder from '../components/MapPlaceholder';
import { analyzeIncident, APIError, fetchFacilities } from '../services/api';
import { createIncidentRequest } from '../types/incident';
import type { IncidentInputData } from '../types/ui';
import type { FacilitiesResponse, IncidentAnalysisResponse } from '../types/incident';

function Dashboard() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResponse, setAnalysisResponse] = useState<IncidentAnalysisResponse | null>(null);
  const [facilitiesData, setFacilitiesData] = useState<FacilitiesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleIncidentSubmit = async (data: IncidentInputData) => {
    setIsProcessing(true);
    setError(null);
    setAnalysisResponse(null); // Clear previous results before new request
    setFacilitiesData(null);
    
    try {
      // Convert form data to API request format
      const request = createIncidentRequest(data);
      
      // Call backend API
      const response = await analyzeIncident(request);

      if (response.status === 'error') {
        const firstError = Array.isArray(response.errors) ? response.errors[0] : undefined;
        const message = typeof firstError === 'string'
          ? firstError
          : firstError?.message || 'Incident analysis returned an error status';
        setError(message);
        setAnalysisResponse(null);
        return;
      }
      
      // Update state with successful response
      setAnalysisResponse(response);

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
        setError(err.message);
      } else {
        setError('An unexpected error occurred while analyzing the incident');
      }
      console.error('Incident analysis error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDismissError = () => {
    setError(null);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Tampa Bay Route Access Decision Support</h1>
        <p className="subtitle">Hillsborough · Pinellas · Pasco | Regional Monitoring with Live Evidence and Optional Planning Context</p>
      </header>

      <div className="operations-layout">
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

          <EvidencePanel evidence={analysisResponse?.evidence || []} />
        </aside>

        <main className="operations-main-stage">
          <SummaryCards
            summary={analysisResponse?.summary || null}
            legacySummary={analysisResponse?.dashboardSummary || null}
          />

          <MapPlaceholder
            map={analysisResponse?.map || null}
            fallbackFeatures={analysisResponse?.mapFeatures || []}
            summary={analysisResponse?.summary || null}
            facilitiesData={facilitiesData}
            planningContext={analysisResponse?.planningContext || null}
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
            dashboardSummary={analysisResponse?.dashboard?.data || analysisResponse?.dashboardSummary || null}
          />
        </main>

        <aside className="operations-rail operations-right-rail">
          <AlertsPanel alerts={analysisResponse?.alerts || []} />
          <FusedEventsPanel
            cases={analysisResponse?.cases || []}
            events={analysisResponse?.events || []}
          />
          <PlanningContextPanel planningContext={analysisResponse?.planningContext || null} />
        </aside>
      </div>
    </div>
  );
}

export default Dashboard;
