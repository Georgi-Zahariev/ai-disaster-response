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
        <h2>Tampa Bay Decision-Support Dashboard</h2>
        <p className="empty-state-description">
          Submit a route disruption report to generate live cases, evidence, alerts, and optional planning enrichment.
        </p>
        <div className="empty-state-features">
          <div className="feature-item">
            <span className="feature-icon">📊</span>
            <span className="feature-text">Route and weather signal fusion</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <span className="feature-text">Fused disruption case detection</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚠️</span>
            <span className="feature-text">Route, fuel, and grocery access alerts</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🗺️</span>
            <span className="feature-text">Planning context (non-live) support</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmptyState;
