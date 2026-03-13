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
import EmptyState from '../components/EmptyState';
import LoadingState from '../components/LoadingState';
import { analyzeIncident, APIError } from '../services/api';
import { createIncidentRequest } from '../types/incident';
import type { IncidentInputData } from '../types/ui';
import type { IncidentAnalysisResponse } from '../types/incident';

function Dashboard() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResponse, setAnalysisResponse] = useState<IncidentAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleIncidentSubmit = async (data: IncidentInputData) => {
    setIsProcessing(true);
    setError(null);
    setAnalysisResponse(null); // Clear previous results before new request
    
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
      {/* Header */}
      <header className="dashboard-header">
        <h1>Tampa Bay Route Access Decision Support</h1>
        <p className="subtitle">Hillsborough · Pinellas · Pasco | Live Monitoring + Optional Planning Context</p>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Error Banner */}
        {error && (
          <div className="error-banner">
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

        {/* Left Column: Input and Map */}
        <div className="dashboard-column dashboard-left">
          <IncidentForm 
            onSubmit={handleIncidentSubmit} 
            isProcessing={isProcessing}
          />
          <MapPlaceholder
            map={analysisResponse?.map || null}
            fallbackFeatures={analysisResponse?.mapFeatures || []}
          />
        </div>

        {/* Right Column: Results and Panels */}
        <div className="dashboard-column dashboard-right">
          {/* Show appropriate state based on analysis status */}
          {!analysisResponse && !isProcessing && !error && <EmptyState />}
          
          {isProcessing && <LoadingState />}
          
          {analysisResponse && (
            <>
              <SummaryCards
                summary={analysisResponse.summary || null}
                legacySummary={analysisResponse.dashboardSummary || null}
              />
              <FusedEventsPanel
                cases={analysisResponse.cases || []}
                events={analysisResponse.events || []}
              />
              <AlertsPanel alerts={analysisResponse.alerts || []} />
              <div className="dashboard-row">
                <EvidencePanel evidence={analysisResponse.evidence || []} />
                <PlanningContextPanel planningContext={analysisResponse.planningContext || null} />
              </div>
              <DashboardSummaryPanel
                dashboardSummary={analysisResponse.dashboard?.data || analysisResponse.dashboardSummary || null}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
