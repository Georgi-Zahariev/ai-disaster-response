/**
 * Loading State Component
 * 
 * Displayed while incident analysis is in progress.
 */

function LoadingState() {
  return (
    <div className="loading-dashboard-state">
      <div className="loading-state-card">
        <div className="loading-spinner"></div>
        <h3>Analyzing Incident...</h3>
        <p className="loading-description">
          Processing multimodal signals and generating insights
        </p>
        <div className="loading-steps">
          <div className="loading-step">
            <div className="step-indicator active"></div>
            <span className="step-text">Collecting signals</span>
          </div>
          <div className="loading-step">
            <div className="step-indicator active"></div>
            <span className="step-text">Fusing data sources</span>
          </div>
          <div className="loading-step">
            <div className="step-indicator active pulse"></div>
            <span className="step-text">Detecting events</span>
          </div>
          <div className="loading-step">
            <div className="step-indicator"></div>
            <span className="step-text">Generating alerts</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoadingState;
