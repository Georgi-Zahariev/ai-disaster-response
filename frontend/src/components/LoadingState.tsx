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
        <h3>Analyzing Tampa Bay Incident...</h3>
        <p className="loading-description">
          Building a live route-access operating picture
        </p>
        <div className="loading-steps">
          <div className="loading-step">
            <div className="step-indicator active"></div>
            <span className="step-text">Collecting in-scope signals</span>
          </div>
          <div className="loading-step">
            <div className="step-indicator active"></div>
            <span className="step-text">Fusing route and hazard evidence</span>
          </div>
          <div className="loading-step">
            <div className="step-indicator active pulse"></div>
            <span className="step-text">Scoring disruption impacts</span>
          </div>
          <div className="loading-step">
            <div className="step-indicator"></div>
            <span className="step-text">Preparing alerts and summary</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoadingState;
