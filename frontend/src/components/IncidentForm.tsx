/**
 * Incident Input Form Component
 * 
 * Allows users to submit incident descriptions for analysis.
 */

import { useState, FormEvent } from 'react';
import type { IncidentInputData } from '../types/ui';

interface IncidentFormProps {
  onSubmit: (data: IncidentInputData) => void;
  isProcessing?: boolean;
}

function IncidentForm({ onSubmit, isProcessing = false }: IncidentFormProps) {
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (!description.trim()) {
      return;
    }

    onSubmit({
      description: description.trim(),
      location: location.trim() || undefined,
    });
  };

  const handleClear = () => {
    setDescription('');
    setLocation('');
  };

  return (
    <div className="panel incident-form-panel">
      <h2>Incident Input</h2>
      <p className="helper-text">
        Enter incident description, optional location, and submit for multimodal analysis
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
            placeholder="Describe the incident (e.g., 'Highway 101 bridge collapsed near San Francisco due to earthquake')"
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

        <div className="form-actions">
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
      </form>
    </div>
  );
}

export default IncidentForm;
