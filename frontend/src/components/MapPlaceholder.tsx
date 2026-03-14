import { useEffect, useMemo } from 'react';
import { CircleMarker, MapContainer, Polygon, Polyline, Popup, Rectangle, TileLayer } from 'react-leaflet';
import type { LatLngTuple } from 'leaflet';
import { useMap } from 'react-leaflet';
import type {
  FacilitiesResponse,
  FacilityRecord,
  MapFeaturePayload,
  MapView,
  PlanningContextView,
} from '../types/incident';
import type { MVPSummary } from '../types/incident';

interface MapPlaceholderProps {
  map?: MapView | null;
  fallbackFeatures?: MapFeaturePayload[];
  summary?: MVPSummary | null;
  facilitiesData?: FacilitiesResponse | null;
  planningContext?: PlanningContextView | null;
  isProcessing?: boolean;
  hasError?: boolean;
}

type FacilityCategory = 'fuel' | 'grocery' | 'other';

interface PointOverlay {
  id: string;
  position: LatLngTuple;
  title: string;
  description?: string;
  source?: string;
  category?: FacilityCategory;
}

interface AlertGeometryOverlay {
  id: string;
  title: string;
  description?: string;
  geometryType: 'Point' | 'LineString' | 'Polygon' | 'MultiPolygon';
  point?: LatLngTuple;
  line?: LatLngTuple[];
  polygon?: LatLngTuple[];
  multiPolygon?: LatLngTuple[][];
}

interface FacilityOverlayBuildResult {
  overlays: PointOverlay[];
  totalReceived: number;
  sampledRecords: number;
  skippedCount: number;
  skippedReasons: string[];
}

const TAMPA_CENTER: LatLngTuple = [27.95, -82.46];
const TAMPA_BOUNDS: [LatLngTuple, LatLngTuple] = [
  [27.34, -83.03],
  [28.38, -82.05],
];

const FACILITY_RENDER_LIMIT = 450;

function normalizeLabel(value?: string): string {
  return (value || '').toLowerCase();
}

function toLatLng(coords: number[]): LatLngTuple | null {
  if (coords.length < 2) {
    return null;
  }
  const [lng, lat] = coords;
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    return null;
  }
  return [lat, lng];
}

function isWithinTampaBounds(point: LatLngTuple): boolean {
  const [lat, lng] = point;
  const [southWest, northEast] = TAMPA_BOUNDS;
  return lat >= southWest[0] && lat <= northEast[0] && lng >= southWest[1] && lng <= northEast[1];
}

function inferFacilityCategory(feature: MapFeaturePayload): FacilityCategory {
  const label = normalizeLabel([
    feature.properties?.title,
    feature.properties?.description,
    feature.properties?.icon,
    feature.popupContent,
  ].filter(Boolean).join(' '));

  if (label.includes('fuel') || label.includes('gas')) {
    return 'fuel';
  }
  if (label.includes('grocery') || label.includes('supermarket') || label.includes('market')) {
    return 'grocery';
  }
  return 'other';
}

function isFacilityFeature(feature: MapFeaturePayload): boolean {
  if (feature.geometry.type !== 'Point') {
    return false;
  }

  const title = normalizeLabel(feature.properties?.title);
  const description = normalizeLabel(feature.properties?.description);
  const popup = normalizeLabel(feature.popupContent);
  const combined = `${title} ${description} ${popup}`;

  return (
    feature.featureType === 'asset' ||
    combined.includes('fuel') ||
    combined.includes('gas station') ||
    combined.includes('grocery') ||
    combined.includes('supermarket')
  );
}

function isLiveEvidenceFeature(feature: MapFeaturePayload): boolean {
  if (feature.geometry.type !== 'Point') {
    return false;
  }
  if (feature.featureType === 'alert') {
    return false;
  }
  return !isFacilityFeature(feature);
}

function getFeatureDescription(feature: MapFeaturePayload): string {
  return feature.properties?.description || feature.popupContent || '';
}

function extractFacilityOverlaysFromBaseline(records: FacilityRecord[]): FacilityOverlayBuildResult {
  const overlays: PointOverlay[] = [];
  let missingCoordinates = 0;
  let invalidCoordinates = 0;
  let outOfRegion = 0;
  let unsupportedType = 0;

  records.forEach((record) => {
    const lat = Number(record.latitude);
    const lng = Number(record.longitude);

    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      if (record.latitude === undefined || record.longitude === undefined) {
        missingCoordinates += 1;
      } else {
        invalidCoordinates += 1;
      }
      return;
    }

    const position: LatLngTuple = [lat, lng];
    if (!isWithinTampaBounds(position)) {
      outOfRegion += 1;
      return;
    }

    const rawType = normalizeLabel(record.category);
    let category: FacilityCategory = 'other';
    if (rawType.includes('fuel') || rawType.includes('gas')) {
      category = 'fuel';
    } else if (rawType.includes('grocery') || rawType.includes('supermarket')) {
      category = 'grocery';
    } else {
      unsupportedType += 1;
      return;
    }

    overlays.push({
      id: record.facility_id || `facility-${overlays.length}`,
      position,
      title: record.name || 'Facility',
      description: record.county || undefined,
      source: record.source || 'backend facility baseline',
      category,
    });
  });

  const skippedReasons: string[] = [];
  if (missingCoordinates > 0) {
    skippedReasons.push(`missing coordinates: ${missingCoordinates}`);
  }
  if (invalidCoordinates > 0) {
    skippedReasons.push(`invalid coordinates: ${invalidCoordinates}`);
  }
  if (outOfRegion > 0) {
    skippedReasons.push(`outside Tampa scope: ${outOfRegion}`);
  }
  if (unsupportedType > 0) {
    skippedReasons.push(`unsupported type: ${unsupportedType}`);
  }

  return {
    overlays,
    totalReceived: records.length,
    sampledRecords: records.length,
    skippedCount: missingCoordinates + invalidCoordinates + outOfRegion + unsupportedType,
    skippedReasons,
  };
}

function extractFacilityOverlaysFromMapFeatures(features: MapFeaturePayload[]): FacilityOverlayBuildResult {
  const overlays: PointOverlay[] = [];
  let invalidCoordinates = 0;

  features.filter(isFacilityFeature).forEach((feature) => {
    const point = toLatLng(feature.geometry.coordinates as number[]);
    if (!point) {
      invalidCoordinates += 1;
      return;
    }
    overlays.push({
      id: feature.featureId,
      position: point,
      title: feature.properties?.title || 'Facility',
      description: getFeatureDescription(feature),
      source: 'backend map feed',
      category: inferFacilityCategory(feature),
    });
  });

  return {
    overlays,
    totalReceived: overlays.length + invalidCoordinates,
    sampledRecords: overlays.length + invalidCoordinates,
    skippedCount: invalidCoordinates,
    skippedReasons: invalidCoordinates > 0 ? [`invalid map feature coordinates: ${invalidCoordinates}`] : [],
  };
}

function extractLiveEvidenceOverlays(features: MapFeaturePayload[]): PointOverlay[] {
  const overlays: PointOverlay[] = [];
  features.filter(isLiveEvidenceFeature).forEach((feature) => {
    const point = toLatLng(feature.geometry.coordinates as number[]);
    if (!point) {
      return;
    }
    overlays.push({
      id: `live-${feature.featureId}`,
      position: point,
      title: feature.properties?.title || feature.featureType,
      description: getFeatureDescription(feature),
      source: 'live evidence',
    });
  });
  return overlays;
}

function extractPlanningOverlays(planningContext?: PlanningContextView | null): PointOverlay[] {
  if (!planningContext?.matchesByCase?.length) {
    return [];
  }

  const items: PointOverlay[] = [];

  planningContext.matchesByCase.forEach((caseEntry, caseIndex) => {
    caseEntry.matches.forEach((match, matchIndex) => {
      const lat = Number(match?.latitude ?? match?.lat ?? match?.location?.latitude ?? match?.location?.lat);
      const lng = Number(match?.longitude ?? match?.lon ?? match?.lng ?? match?.location?.longitude ?? match?.location?.lon ?? match?.location?.lng);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
        return;
      }
      items.push({
        id: `plan-${caseIndex}-${matchIndex}`,
        position: [lat, lng],
        title: `Planning Context: ${caseEntry.eventType || 'scenario'}`,
        description: typeof match?.description === 'string' ? match.description : 'Historical/planning context reference (not live evidence)',
        source: 'planning context',
      });
    });
  });

  return items;
}

function extractAlertOverlays(features: MapFeaturePayload[]): AlertGeometryOverlay[] {
  const overlays: AlertGeometryOverlay[] = [];

  features
    .filter((feature) => feature.featureType === 'alert')
    .forEach((feature) => {
      const title = feature.properties?.title || 'Weather Alert';
      const description = getFeatureDescription(feature);
      const geometry = feature.geometry;

      if (geometry.type === 'Point') {
        const point = toLatLng(geometry.coordinates as number[]);
        if (point) {
          overlays.push({
            id: `alert-${feature.featureId}`,
            title,
            description,
            geometryType: 'Point',
            point,
          });
        }
        return;
      }

      if (geometry.type === 'LineString') {
        const line = (geometry.coordinates as number[][])
          .map((coords) => toLatLng(coords))
          .filter((coords): coords is LatLngTuple => Boolean(coords));
        if (line.length > 1) {
          overlays.push({
            id: `alert-${feature.featureId}`,
            title,
            description,
            geometryType: 'LineString',
            line,
          });
        }
        return;
      }

      if (geometry.type === 'Polygon') {
        const raw = geometry.coordinates as unknown;
        const polygonCoords = Array.isArray(raw) && Array.isArray(raw[0]) && Array.isArray((raw as any[])[0][0])
          ? ((raw as number[][][])[0] || [])
          : (raw as number[][]);
        const polygon = polygonCoords
          .map((coords) => toLatLng(coords))
          .filter((coords): coords is LatLngTuple => Boolean(coords));
        if (polygon.length > 2) {
          overlays.push({
            id: `alert-${feature.featureId}`,
            title,
            description,
            geometryType: 'Polygon',
            polygon,
          });
        }
        return;
      }

      if (geometry.type === 'MultiPolygon') {
        const raw = geometry.coordinates as unknown as number[][][][];
        const parts = raw
          .map((polygon) => (polygon[0] || []).map((coords) => toLatLng(coords)).filter((coords): coords is LatLngTuple => Boolean(coords)))
          .filter((ring) => ring.length > 2);
        if (parts.length > 0) {
          overlays.push({
            id: `alert-${feature.featureId}`,
            title,
            description,
            geometryType: 'MultiPolygon',
            multiPolygon: parts,
          });
        }
      }
    });

  return overlays;
}

function BoundsController({ points }: { points: LatLngTuple[] }) {
  const map = useMap();

  useEffect(() => {
    if (!points.length) {
      return;
    }
    map.fitBounds([TAMPA_BOUNDS[0], TAMPA_BOUNDS[1], ...points], { padding: [28, 28], maxZoom: 11 });
  }, [map, points]);

  return null;
}

function getFacilityStyle(category: FacilityCategory): { color: string; fillColor: string; radius: number } {
  if (category === 'fuel') {
    return { color: '#b45309', fillColor: '#f59e0b', radius: 5 };
  }
  if (category === 'grocery') {
    return { color: '#166534', fillColor: '#22c55e', radius: 5 };
  }
  return { color: '#334155', fillColor: '#94a3b8', radius: 4 };
}

function MapPlaceholder({
  map = null,
  fallbackFeatures = [],
  summary = null,
  facilitiesData = null,
  planningContext = null,
  isProcessing = false,
  hasError = false,
}: MapPlaceholderProps) {
  const mapFeatures = map?.features || fallbackFeatures;
  const facilityBaselineCount = summary?.facilities?.baselineCount ?? 0;
  const weatherSignals = summary?.signals?.weatherHazardSignals ?? 0;
  const facilityBuild = useMemo(() => {
    const facilityRecords = facilitiesData?.records || [];
    if (facilityRecords.length > 0) {
      const fromBaseline = extractFacilityOverlaysFromBaseline(facilityRecords);
      const totalFromBackend = typeof facilitiesData?.totalAvailable === 'number'
        ? facilitiesData.totalAvailable
        : fromBaseline.totalReceived;
      const extraReasons = [...fromBaseline.skippedReasons];
      if (totalFromBackend > fromBaseline.sampledRecords) {
        extraReasons.push(`not returned due to limit: ${totalFromBackend - fromBaseline.sampledRecords}`);
      }
      return {
        ...fromBaseline,
        totalReceived: totalFromBackend,
        skippedReasons: extraReasons,
      };
    }
    return extractFacilityOverlaysFromMapFeatures(mapFeatures);
  }, [facilitiesData, mapFeatures]);
  const facilityOverlays = facilityBuild.overlays;
  const liveEvidenceOverlays = useMemo(() => extractLiveEvidenceOverlays(mapFeatures), [mapFeatures]);
  const planningOverlays = useMemo(() => extractPlanningOverlays(planningContext), [planningContext]);
  const alertOverlays = useMemo(() => extractAlertOverlays(mapFeatures), [mapFeatures]);

  const clippedFacilities = facilityOverlays.slice(0, FACILITY_RENDER_LIMIT);
  const clippedNotice = facilityOverlays.length > clippedFacilities.length
    ? `${clippedFacilities.length} of ${facilityOverlays.length} facilities shown for map readability`
    : null;

  const boundsPoints = useMemo(
    () => [
      ...clippedFacilities.map((item) => item.position),
      ...liveEvidenceOverlays.slice(0, 120).map((item) => item.position),
      ...planningOverlays.slice(0, 80).map((item) => item.position),
    ],
    [clippedFacilities, liveEvidenceOverlays, planningOverlays]
  );

  return (
    <div className="panel map-placeholder ops-map-shell">
      <div className="map-title-row">
        <h2>Tampa Bay Operational Map</h2>
        <span className="map-region-tag">Hillsborough · Pinellas · Pasco</span>
      </div>
      <p className="panel-subtitle">Always-on regional view with facility baseline and active case overlays.</p>

      <div className="map-status-strip">
        <span>Facilities: <strong>{facilityBaselineCount}</strong></span>
        <span>Weather Signals: <strong>{weatherSignals}</strong></span>
        <span>Facilities Received: <strong>{facilityBuild.totalReceived}</strong></span>
        <span>Facilities Rendered: <strong>{facilityOverlays.length}</strong></span>
        <span>Facilities Skipped: <strong>{facilityBuild.skippedCount}</strong></span>
        <span>Alert Geometries: <strong>{alertOverlays.length}</strong></span>
        <span>Planning Points: <strong>{planningOverlays.length}</strong></span>
        {isProcessing && <span className="map-status-live">Refreshing...</span>}
        {hasError && <span className="map-status-warning">Data update issue</span>}
        {facilityBuild.skippedReasons.length > 0 && (
          <span className="map-status-warning">Skip reasons: {facilityBuild.skippedReasons.join(' | ')}</span>
        )}
        {facilitiesData?.warnings?.length ? (
          <span className="map-status-warning">Facility source warnings: {facilitiesData.warnings.join(' | ')}</span>
        ) : null}
      </div>

      <div className="map-container">
        <MapContainer
          center={TAMPA_CENTER}
          zoom={9}
          minZoom={8}
          maxZoom={13}
          maxBounds={TAMPA_BOUNDS}
          maxBoundsViscosity={0.9}
          scrollWheelZoom
          className="map-canvas"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <Rectangle
            bounds={TAMPA_BOUNDS}
            pathOptions={{ color: '#1d4ed8', weight: 1.5, fillOpacity: 0.04, fillColor: '#bfdbfe' }}
          >
            <Popup>Tampa Bay Regional Focus: Hillsborough, Pinellas, Pasco</Popup>
          </Rectangle>

          <BoundsController points={boundsPoints} />

          {clippedFacilities.map((facility) => {
            const style = getFacilityStyle(facility.category || 'other');
            return (
              <CircleMarker
                key={facility.id}
                center={facility.position}
                radius={style.radius}
                pathOptions={{ color: style.color, fillColor: style.fillColor, fillOpacity: 0.85, weight: 1 }}
              >
                <Popup>
                  <strong>{facility.title}</strong>
                  <br />
                  Category: {facility.category || 'other'}
                  {facility.description ? (
                    <>
                      <br />
                      {facility.description}
                    </>
                  ) : null}
                </Popup>
              </CircleMarker>
            );
          })}

          {alertOverlays.map((alert) => {
            if (alert.geometryType === 'Point' && alert.point) {
              return (
                <CircleMarker
                  key={alert.id}
                  center={alert.point}
                  radius={8}
                  pathOptions={{ color: '#92400e', fillColor: '#f59e0b', fillOpacity: 0.25, weight: 2 }}
                >
                  <Popup>
                    <strong>{alert.title}</strong>
                    {alert.description ? (
                      <>
                        <br />
                        {alert.description}
                      </>
                    ) : null}
                  </Popup>
                </CircleMarker>
              );
            }
            if (alert.geometryType === 'LineString' && alert.line) {
              return (
                <Polyline
                  key={alert.id}
                  positions={alert.line}
                  pathOptions={{ color: '#a16207', weight: 3, opacity: 0.9 }}
                >
                  <Popup>{alert.title}</Popup>
                </Polyline>
              );
            }
            if (alert.geometryType === 'Polygon' && alert.polygon) {
              return (
                <Polygon
                  key={alert.id}
                  positions={alert.polygon}
                  pathOptions={{ color: '#b45309', weight: 2, fillColor: '#f59e0b', fillOpacity: 0.16 }}
                >
                  <Popup>{alert.title}</Popup>
                </Polygon>
              );
            }
            if (alert.geometryType === 'MultiPolygon' && alert.multiPolygon) {
              return (
                <Polygon
                  key={alert.id}
                  positions={alert.multiPolygon}
                  pathOptions={{ color: '#b45309', weight: 2, fillColor: '#f59e0b', fillOpacity: 0.16 }}
                >
                  <Popup>{alert.title}</Popup>
                </Polygon>
              );
            }
            return null;
          })}

          {liveEvidenceOverlays.map((item) => (
            <CircleMarker
              key={item.id}
              center={item.position}
              radius={4}
              pathOptions={{ color: '#7f1d1d', fillColor: '#ef4444', fillOpacity: 0.55, weight: 1 }}
            >
              <Popup>
                <strong>Live Evidence</strong>
                <br />
                {item.title}
              </Popup>
            </CircleMarker>
          ))}

          {planningOverlays.map((item) => (
            <CircleMarker
              key={item.id}
              center={item.position}
              radius={8}
              pathOptions={{ color: '#0c4a6e', fillColor: '#7dd3fc', fillOpacity: 0.15, weight: 2 }}
            >
              <Popup>
                <strong>Planning Context (Not Live)</strong>
                <br />
                {item.title}
                {item.description ? (
                  <>
                    <br />
                    {item.description}
                  </>
                ) : null}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>

        <div className="map-overlay-panel">
          <div className="map-legend">
            <span><i className="legend-dot fuel" />Fuel Facilities</span>
            <span><i className="legend-dot grocery" />Grocery Facilities</span>
            <span><i className="legend-dot alerts" />Weather Alerts</span>
            <span><i className="legend-dot live" />Live Evidence</span>
            <span><i className="legend-dot planning" />Planning Context</span>
          </div>
          {clippedNotice ? <p className="map-clipped-notice">{clippedNotice}</p> : null}
          {alertOverlays.length === 0 ? (
            <p className="map-empty-overlay-note">No active weather overlay geometry. Regional map remains operational.</p>
          ) : null}
          {hasError ? (
            <p className="map-contained-error">Backend update error. Showing last known map context.</p>
          ) : null}
          {isProcessing ? (
            <p className="map-contained-loading">Refreshing map layers...</p>
          ) : null}
        </div>

        {!mapFeatures.length && !facilityOverlays.length && !planningOverlays.length && !alertOverlays.length && (
          <div className="map-empty-state-inline">
            <p>Tampa Bay region view is active.</p>
            <p className="empty-state-hint">Layers will populate as new live evidence, facilities, and alert geometry arrive.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default MapPlaceholder;
