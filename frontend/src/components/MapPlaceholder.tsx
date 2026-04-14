import { useEffect, useMemo } from 'react';
import { CircleMarker, MapContainer, Polygon, Polyline, Popup, Rectangle, TileLayer } from 'react-leaflet';
import type { LatLngTuple } from 'leaflet';
import { useMap } from 'react-leaflet';
import type {
  EvidenceRecord,
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
  evidence?: EvidenceRecord[];
  facilitiesData?: FacilitiesResponse | null;
  planningContext?: PlanningContextView | null;
  selectedCaseId?: string | null;
  dataUpdatedAt?: string | null;
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
  eventId?: string;
}

interface AlertGeometryOverlay {
  id: string;
  title: string;
  description?: string;
  eventId?: string;
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

function formatRecency(timestamp?: string | null): string {
  if (!timestamp) {
    return 'n/a';
  }
  const deltaMs = Date.now() - new Date(timestamp).getTime();
  const minutes = Math.max(0, Math.floor(deltaMs / 60000));
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
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

function extractLiveEvidenceOverlays(
  evidence: EvidenceRecord[],
): PointOverlay[] {
  const overlays: PointOverlay[] = [];

  evidence.forEach((item) => {
    const lat = Number(item.location?.latitude);
    const lng = Number(item.location?.longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      return;
    }

    const point: LatLngTuple = [lat, lng];
    if (!isWithinTampaBounds(point)) {
      return;
    }

    overlays.push({
      id: `live-${item.observationId}`,
      position: point,
      title: item.observationType || 'live observation',
      description: item.description,
      source: 'live evidence',
      eventId: item.eventId,
    });
  });

  return overlays;
}

function extractPlanningOverlays(
  planningContext?: PlanningContextView | null,
  selectedCaseId?: string | null,
): PointOverlay[] {
  if (!planningContext?.requested || planningContext?.isLiveEvidence !== false || !planningContext?.matchesByCase?.length) {
    return [];
  }

  const items: PointOverlay[] = [];

  const caseSource = selectedCaseId
    ? planningContext.matchesByCase.filter((entry) => entry.eventId === selectedCaseId)
    : planningContext.matchesByCase;

  const sortedCases = [...caseSource].sort((a, b) => {
    const eventTypeCompare = String(a?.eventType || '').localeCompare(String(b?.eventType || ''));
    if (eventTypeCompare !== 0) {
      return eventTypeCompare;
    }
    return String(a?.eventId || '').localeCompare(String(b?.eventId || ''));
  });

  sortedCases.forEach((caseEntry, caseIndex) => {
    const sortedMatches = [...(caseEntry.matches || [])].sort((a, b) => {
      return String(a?.concept || '').localeCompare(String(b?.concept || ''));
    });

    sortedMatches.forEach((match, matchIndex) => {
      const lat = Number(match?.latitude ?? match?.lat ?? match?.location?.latitude ?? match?.location?.lat);
      const lng = Number(match?.longitude ?? match?.lon ?? match?.lng ?? match?.location?.longitude ?? match?.location?.lon ?? match?.location?.lng);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
        return;
      }
      const point: LatLngTuple = [lat, lng];
      if (!isWithinTampaBounds(point)) {
        return;
      }
      items.push({
        id: `plan-${caseIndex}-${matchIndex}`,
        position: point,
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
            eventId: feature.properties?.eventId,
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
            eventId: feature.properties?.eventId,
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
            eventId: feature.properties?.eventId,
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
            eventId: feature.properties?.eventId,
            geometryType: 'MultiPolygon',
            multiPolygon: parts,
          });
        }
      }
    });

  return overlays;
}

function filterMapFeaturesBySelectedCase(
  features: MapFeaturePayload[],
  selectedCaseId?: string | null,
): MapFeaturePayload[] {
  if (!selectedCaseId) {
    return features;
  }

  // Preserve full regional context, but promote selected incident-linked features.
  return [...features].sort((a, b) => {
    const aSelected = (
      (a.featureType === 'event' && (a.dataId === selectedCaseId || a.properties?.eventId === selectedCaseId))
      || ((a.featureType === 'disruption' || a.featureType === 'alert') && a.properties?.eventId === selectedCaseId)
    ) ? 1 : 0;
    const bSelected = (
      (b.featureType === 'event' && (b.dataId === selectedCaseId || b.properties?.eventId === selectedCaseId))
      || ((b.featureType === 'disruption' || b.featureType === 'alert') && b.properties?.eventId === selectedCaseId)
    ) ? 1 : 0;
    return bSelected - aSelected;
  });
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
  evidence = [],
  facilitiesData = null,
  planningContext = null,
  selectedCaseId = null,
  dataUpdatedAt = null,
  isProcessing = false,
  hasError = false,
}: MapPlaceholderProps) {
  const baseMapFeatures = map?.features || fallbackFeatures;
  const mapFeatures = useMemo(
    () => filterMapFeaturesBySelectedCase(baseMapFeatures, selectedCaseId),
    [baseMapFeatures, selectedCaseId],
  );
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
  const liveEvidenceOverlays = useMemo(
    () => extractLiveEvidenceOverlays(evidence),
    [evidence],
  );
  const planningOverlays = useMemo(
    () => extractPlanningOverlays(planningContext, selectedCaseId),
    [planningContext, selectedCaseId],
  );
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
      <p className="panel-subtitle">Regional operations map with live evidence overlays and separate non-live planning baseline.</p>
      {selectedCaseId ? <p className="empty-state-hint">Incident focus: {selectedCaseId}</p> : null}

      <div className="map-status-strip">
        <span>Baseline Facilities: <strong>{facilityBaselineCount}</strong></span>
        <span>Weather Signals: <strong>{weatherSignals}</strong></span>
        <span>Facilities in Feed: <strong>{facilityBuild.totalReceived}</strong></span>
        <span>Facilities on Map: <strong>{facilityOverlays.length}</strong></span>
        <span>Alert Areas: <strong>{alertOverlays.length}</strong></span>
        <span>Planning Baseline Points: <strong>{planningOverlays.length}</strong></span>
        <span>Updated: <strong>{formatRecency(dataUpdatedAt)}</strong></span>
        {isProcessing && <span className="map-status-live">Updating map layers...</span>}
        {hasError && <span className="map-status-warning">Using last stable update.</span>}
        {facilityBuild.skippedReasons.length > 0 && <span className="map-status-warning">Some facilities were excluded by quality/scope rules.</span>}
        {facilitiesData?.warnings?.length ? <span className="map-status-warning">Facility feed degraded; verified baseline points shown.</span> : null}
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
            const isSelectedAlert = Boolean(selectedCaseId && alert.eventId === selectedCaseId);
            if (alert.geometryType === 'Point' && alert.point) {
              return (
                <CircleMarker
                  key={alert.id}
                  center={alert.point}
                  radius={isSelectedAlert ? 10 : 6}
                  pathOptions={{
                    color: isSelectedAlert ? '#78350f' : '#92400e',
                    fillColor: '#f59e0b',
                    fillOpacity: isSelectedAlert ? 0.4 : 0.15,
                    weight: isSelectedAlert ? 3 : 1.5,
                    opacity: isSelectedAlert ? 1 : 0.6,
                  }}
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
                  pathOptions={{
                    color: isSelectedAlert ? '#92400e' : '#a16207',
                    weight: isSelectedAlert ? 4 : 2,
                    opacity: isSelectedAlert ? 0.95 : 0.45,
                  }}
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
                  pathOptions={{
                    color: isSelectedAlert ? '#92400e' : '#b45309',
                    weight: isSelectedAlert ? 3 : 1.5,
                    fillColor: '#f59e0b',
                    fillOpacity: isSelectedAlert ? 0.24 : 0.08,
                    opacity: isSelectedAlert ? 0.95 : 0.5,
                  }}
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
                  pathOptions={{
                    color: isSelectedAlert ? '#92400e' : '#b45309',
                    weight: isSelectedAlert ? 3 : 1.5,
                    fillColor: '#f59e0b',
                    fillOpacity: isSelectedAlert ? 0.24 : 0.08,
                    opacity: isSelectedAlert ? 0.95 : 0.5,
                  }}
                >
                  <Popup>{alert.title}</Popup>
                </Polygon>
              );
            }
            return null;
          })}

          {liveEvidenceOverlays.map((item) => {
            const isSelectedEvidence = Boolean(selectedCaseId && item.eventId === selectedCaseId);
            return (
              <CircleMarker
                key={item.id}
                center={item.position}
                radius={isSelectedEvidence ? 5 : 3.5}
                pathOptions={{
                  color: '#7f1d1d',
                  fillColor: '#ef4444',
                  fillOpacity: isSelectedEvidence ? 0.78 : 0.32,
                  weight: isSelectedEvidence ? 1.5 : 1,
                  opacity: isSelectedEvidence ? 1 : 0.5,
                }}
              >
                <Popup>
                  <strong>Live Evidence</strong>
                  <br />
                  {item.title}
                </Popup>
              </CircleMarker>
            );
          })}

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
            <span><i className="legend-dot fuel" />Fuel Facility Baseline</span>
            <span><i className="legend-dot grocery" />Grocery Facility Baseline</span>
            <span><i className="legend-dot alerts" />Active Alert Geometry</span>
            <span><i className="legend-dot live" />Live Evidence</span>
            <span><i className="legend-dot planning" />Planning Baseline (Non-live)</span>
          </div>
          {clippedNotice ? <p className="map-clipped-notice">{clippedNotice}</p> : null}
          {alertOverlays.length === 0 ? (
            <p className="map-empty-overlay-note">No active alert geometry currently. Regional map remains available.</p>
          ) : null}
          {hasError ? (
            <p className="map-contained-error">Latest update was degraded. Showing last stable map context.</p>
          ) : null}
          {isProcessing ? (
            <p className="map-contained-loading">Map refresh in progress...</p>
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
