/**
 * Empty State Component
 * 
 * Displayed when no incident has been analyzed yet.
 */

function EmptyState() {
  return (
    <div className="empty-dashboard-state">
      <div className="empty-state-card">
        <div className="empty-state-icon">🌐</div>
        <h2>Situational Awareness Dashboard</h2>
        <p className="empty-state-description">
          Submit an incident report using the form on the left to activate multimodal analysis and generate real-time situational awareness.
        </p>
        <div className="empty-state-features">
          <div className="feature-item">
            <span className="feature-icon">📊</span>
            <span className="feature-text">Multi-source data fusion</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <span className="feature-text">Automated event detection</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚠️</span>
            <span className="feature-text">Intelligent alert generation</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🗺️</span>
            <span className="feature-text">Impact & disruption assessment</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmptyState;
