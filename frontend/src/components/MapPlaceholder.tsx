/**
 * Map Placeholder Component
 * 
 * Placeholder for geographic visualization.
 * TODO: Integrate with actual mapping library (e.g., Leaflet, Mapbox)
 */

import type { MapFeaturePayload, MapView } from '../types/incident';

interface MapPlaceholderProps {
  map?: MapView | null;
  fallbackFeatures?: MapFeaturePayload[];
}

function MapPlaceholder({ map = null, fallbackFeatures = [] }: MapPlaceholderProps) {
  const mapFeatures = map?.features || fallbackFeatures;
  /**
   * Format coordinates for Point geometry
   */
   const formatCoordinates = (coords: number[] | number[][] | number[][][]): string => {
    if (Array.isArray(coords) && coords.length >= 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') {
      return `(${coords[1].toFixed(4)}, ${coords[0].toFixed(4)})`;
    }
    return '';
  };

  return (
    <div className="panel map-placeholder">
      <h2>Map Data Preview</h2>
      <p className="panel-subtitle">Current map features from backend output for corridors, alerts, and impact points.</p>
      <div className="map-container">
        {mapFeatures.length === 0 ? (
          <div className="map-empty-state">
            <div className="map-icon">🗺️</div>
            <p>No map features yet</p>
            <p className="empty-state-hint">
              Submit an incident to load route and alert feature points
            </p>
          </div>
        ) : (
          <div className="map-preview">
            <div className="map-icon">🗺️</div>
            <p><strong>{mapFeatures.length} map features loaded</strong></p>
            <ul className="map-features-list">
              {mapFeatures.slice(0, 5).map((feature) => (
                <li key={feature.featureId}>
                  {feature.properties?.title || feature.properties?.description || feature.featureType}
                  {feature.geometry.type === 'Point' && (
                    <span className="coordinates">
                      {' '}{formatCoordinates(feature.geometry.coordinates)}
                    </span>
                  )}
                </li>
              ))}
            </ul>
            {mapFeatures.length > 5 && (
              <p className="empty-state-hint">+ {mapFeatures.length - 5} more features</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MapPlaceholder;
