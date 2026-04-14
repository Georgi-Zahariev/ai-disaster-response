/**
 * Incident Input Form Component
 * 
 * Allows users to submit incident descriptions for analysis.
 */

import { useState, FormEvent } from 'react';
import type { IncidentInputData } from '../types/ui';
import type { ContextGuideResponse } from '../types/incident';
import { fetchIncidentContextGuide } from '../services/api';

interface IncidentFormProps {
  onSubmit: (data: IncidentInputData) => void;
  isProcessing?: boolean;
}

function IncidentForm({ onSubmit, isProcessing = false }: IncidentFormProps) {
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [county, setCounty] = useState<'hillsborough' | 'pinellas' | 'pasco'>('hillsborough');
  const [enablePlanningContext, setEnablePlanningContext] = useState(false);
  const [isGuideLoading, setIsGuideLoading] = useState(false);
  const [guideError, setGuideError] = useState<string | null>(null);
  const [guideResponse, setGuideResponse] = useState<ContextGuideResponse | null>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (!description.trim()) {
      return;
    }

    onSubmit({
      description: description.trim(),
      location: location.trim() || undefined,
      county,
      enablePlanningContext,
    });
  };

  const handleClear = () => {
    setDescription('');
    setLocation('');
    setCounty('hillsborough');
    setEnablePlanningContext(false);
    setGuideError(null);
    setGuideResponse(null);
  };

  const handleGenerateGuide = async () => {
    const trimmedDescription = description.trim();
    if (!trimmedDescription) {
      setGuideError('Add incident description before generating AI context guidance.');
      return;
    }

    setGuideError(null);
    setIsGuideLoading(true);

    try {
      const response = await fetchIncidentContextGuide({
        description: trimmedDescription,
        location: location.trim() || undefined,
        county,
      });
      setGuideResponse(response);

      const suggestedCounty = response.guide?.suggestedCounty;
      if (suggestedCounty === 'hillsborough' || suggestedCounty === 'pinellas' || suggestedCounty === 'pasco') {
        setCounty(suggestedCounty);
      }

      if (response.guide?.enablePlanningContextRecommended === true) {
        setEnablePlanningContext(true);
      }
    } catch (error) {
      setGuideResponse(null);
      setGuideError('Decision brief unavailable. Please verify the incident details and try again.');
    } finally {
      setIsGuideLoading(false);
    }
  };

  return (
    <div className="panel incident-form-panel">
      <h2>Report Utility</h2>
      <p className="helper-text">
        Add a new Tampa Bay disruption signal for analysis without leaving the monitoring view.
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="description">
            Incident Description <span className="required">*</span>
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the Tampa Bay incident (route blockage, fuel disruption, grocery access risk, flooding, etc.)"
            rows={4}
            disabled={isProcessing}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="location">Location (Optional)</label>
          <input
            type="text"
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="City, region, or coordinates"
            disabled={isProcessing}
          />
        </div>

        <div className="form-group">
          <label htmlFor="county">Tampa Bay County Scope</label>
          <select
            id="county"
            value={county}
            onChange={(e) => setCounty(e.target.value as 'hillsborough' | 'pinellas' | 'pasco')}
            disabled={isProcessing}
          >
            <option value="hillsborough">Hillsborough</option>
            <option value="pinellas">Pinellas</option>
            <option value="pasco">Pasco</option>
          </select>
        </div>

        <div className="form-group checkbox-group">
          <label htmlFor="planningContext" className="checkbox-label">
            <input
              id="planningContext"
              type="checkbox"
              checked={enablePlanningContext}
              onChange={(e) => setEnablePlanningContext(e.target.checked)}
              disabled={isProcessing}
            />
            Enable planning-context enrichment (non-live)
          </label>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleGenerateGuide}
            disabled={isProcessing || isGuideLoading}
          >
            {isGuideLoading ? 'Generating Guide...' : 'Generate AI Context Guide'}
          </button>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isProcessing || !description.trim()}
          >
            {isProcessing ? 'Processing...' : 'Analyze Incident'}
          </button>
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={isProcessing}
          >
            Clear
          </button>
        </div>

        {guideError && (
          <p className="helper-text" role="alert">
            {guideError}
          </p>
        )}

        {guideResponse && (
          <div className="panel-subsection">
            <h3>Incident Decision Brief</h3>
            <p className="helper-text">
              Deterministic incident-specific brief for route, fuel, and grocery continuity.
            </p>
            {guideResponse.guide?.decisionBrief?.incidentFocus && (
              <p className="helper-text"><strong>Incident Focus:</strong> {guideResponse.guide.decisionBrief.incidentFocus}</p>
            )}
            {guideResponse.guide?.decisionBrief?.operationalObjective && (
              <p className="helper-text"><strong>Operational Objective:</strong> {guideResponse.guide.decisionBrief.operationalObjective}</p>
            )}
            {guideResponse.guide?.extraContextPrompt && (
              <p className="helper-text">{guideResponse.guide.extraContextPrompt}</p>
            )}
            {Array.isArray(guideResponse.guide?.decisionBrief?.immediateActions)
              && guideResponse.guide.decisionBrief.immediateActions.length > 0 && (
              <>
                <h4>Immediate Actions</h4>
                <ul>
                  {guideResponse.guide.decisionBrief.immediateActions.map((item, idx) => (
                    <li key={`brief-action-${idx}`}>{item}</li>
                  ))}
                </ul>
              </>
            )}
            {Array.isArray(guideResponse.guide?.operatorChecklist) && guideResponse.guide.operatorChecklist.length > 0 && (
              <>
                <h4>Verification Checklist</h4>
                <ul>
                  {guideResponse.guide.operatorChecklist.map((item, idx) => (
                    <li key={`guide-item-${idx}`}>{item}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </form>
    </div>
  );
}

export default IncidentForm;
