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
import SourcesPanel from '../components/SourcesPanel';
import ActivityLogPanel from '../components/ActivityLogPanel';
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
        <h1>AI Disaster Response Dashboard</h1>
        <p className="subtitle">Multimodal Incident Analysis & Situational Awareness</p>
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
          <MapPlaceholder mapFeatures={analysisResponse?.mapFeatures || []} />
        </div>

        {/* Right Column: Results and Panels */}
        <div className="dashboard-column dashboard-right">
          {/* Show appropriate state based on analysis status */}
          {!analysisResponse && !isProcessing && !error && <EmptyState />}
          
          {isProcessing && <LoadingState />}
          
          {analysisResponse && (
            <>
              <SummaryCards summary={analysisResponse.dashboardSummary || null} />
              <AlertsPanel alerts={analysisResponse.alerts || []} />
              <FusedEventsPanel events={analysisResponse.events || []} />
              <div className="dashboard-row">
                <SourcesPanel response={analysisResponse} />
                <ActivityLogPanel response={analysisResponse} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
