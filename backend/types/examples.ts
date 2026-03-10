/**
 * Usage examples for disaster response shared types
 * 
 * This file demonstrates how to use the shared TypeScript schemas
 * in various scenarios across the disaster response system.
 */

import {
  IncidentInputRequest,
  TextSignal,
  VisionSignal,
  QuantSignal,
  FusedEvent,
  DisruptionAssessment,
  AlertRecommendation,
  MapFeaturePayload,
  DashboardSummary,
  FinalApiResponse,
  AppError,
  SourceType,
  SeverityLevel,
  SupplyChainSector,
  AssetType,
  AlertPriority,
  isTextSignal,
  isVisionSignal,
  isQuantSignal
} from './index';

// ============================================================================
// Example 1: Creating a Text Signal from Social Media
// ============================================================================

const socialMediaSignal: TextSignal = {
  signalId: 'twitter-1234567890',
  signalType: 'text',
  source: {
    sourceId: 'src-twitter',
    sourceType: SourceType.SOCIAL_MEDIA,
    sourceName: 'Twitter Emergency Feed',
    provider: 'Twitter, Inc.',
    reliabilityScore: 0.65
  },
  receivedAt: '2026-03-09T14:32:00Z',
  createdAt: '2026-03-09T14:30:15Z',
  location: {
    latitude: 34.0522,
    longitude: -118.2437,
    placeName: 'Los Angeles, CA',
    uncertaintyRadiusMeters: 5000,
    countryCode: 'US'
  },
  timeReference: {
    timestamp: '2026-03-09T14:30:00Z',
    precision: 'minute',
    timezone: 'America/Los_Angeles',
    confidence: 0.9
  },
  confidence: 0.7,
  content: 'Major accident on I-405 southbound near LAX. Traffic completely stopped. Emergency vehicles rushing to scene. #LATraffic #Emergency',
  language: 'en',
  entities: [
    { text: 'I-405', type: 'LOCATION', confidence: 0.95 },
    { text: 'LAX', type: 'LOCATION', confidence: 0.98 }
  ],
  sentiment: -0.6
};

// ============================================================================
// Example 2: Creating a Vision Signal from Satellite Imagery
// ============================================================================

const satelliteImageSignal: VisionSignal = {
  signalId: 'sat-noaa20-img-001',
  signalType: 'vision',
  source: {
    sourceId: 'src-noaa20',
    sourceType: SourceType.SATELLITE,
    sourceName: 'NOAA-20 VIIRS',
    provider: 'NOAA',
    reliabilityScore: 0.98
  },
  receivedAt: '2026-03-09T14:35:00Z',
  createdAt: '2026-03-09T14:20:00Z',
  location: {
    latitude: 34.0522,
    longitude: -118.2437,
    placeName: 'Los Angeles Metropolitan Area',
    uncertaintyRadiusMeters: 100
  },
  timeReference: {
    timestamp: '2026-03-09T14:20:00Z',
    precision: 'minute',
    confidence: 1.0
  },
  confidence: 0.95,
  mediaUrl: 's3://disaster-response/imagery/noaa20-20260309-1420.tif',
  mediaType: 'image/tiff',
  resolution: {
    width: 4096,
    height: 4096
  },
  sensorInfo: {
    model: 'VIIRS',
    altitude: 824000, // meters (orbital altitude)
    fov: 112 // degrees
  },
  detectedObjects: [
    {
      label: 'traffic_congestion',
      confidence: 0.89,
      boundingBox: { x: 1024, y: 2048, width: 512, height: 256 }
    },
    {
      label: 'emergency_vehicles',
      confidence: 0.76,
      boundingBox: { x: 1200, y: 2100, width: 64, height: 128 }
    }
  ],
  caption: 'Satellite imagery showing significant traffic congestion on major highway with emergency vehicle presence'
};

// ============================================================================
// Example 3: Creating a Quantitative Sensor Signal
// ============================================================================

const trafficFlowSensor: QuantSignal = {
  signalId: 'sensor-i405-mm23-flow',
  signalType: 'quantitative',
  source: {
    sourceId: 'src-caltrans-sensors',
    sourceType: SourceType.SENSOR_NETWORK,
    sourceName: 'CalTrans Traffic Sensor Network',
    provider: 'California Department of Transportation',
    reliabilityScore: 0.92
  },
  receivedAt: '2026-03-09T14:33:00Z',
  createdAt: '2026-03-09T14:32:00Z',
  location: {
    latitude: 33.9425,
    longitude: -118.4081,
    placeName: 'I-405 Mile Marker 23',
    uncertaintyRadiusMeters: 10
  },
  timeReference: {
    timestamp: '2026-03-09T14:32:00Z',
    precision: 'minute',
    confidence: 1.0
  },
  confidence: 0.95,
  measurementType: 'traffic_flow_rate',
  value: 12,
  unit: 'vehicles_per_minute',
  sensorId: 'caltrans-i405-mm23-001',
  aggregation: {
    method: 'mean',
    windowSeconds: 300,
    sampleCount: 60
  },
  normalRange: {
    min: 400,
    max: 800
  },
  deviationScore: -0.97, // 97% below normal
  timeSeries: [
    { timestamp: '2026-03-09T14:27:00Z', value: 650 },
    { timestamp: '2026-03-09T14:28:00Z', value: 480 },
    { timestamp: '2026-03-09T14:29:00Z', value: 220 },
    { timestamp: '2026-03-09T14:30:00Z', value: 45 },
    { timestamp: '2026-03-09T14:31:00Z', value: 18 },
    { timestamp: '2026-03-09T14:32:00Z', value: 12 }
  ]
};

// ============================================================================
// Example 4: Building an Incident Input Request
// ============================================================================

const incidentRequest: IncidentInputRequest = {
  trace: {
    requestId: 'req-20260309-143500-abc123',
    traceId: 'trace-xyz789',
    spanId: 'span-001',
    timestamp: '2026-03-09T14:35:00Z',
    userId: 'emergency-coordinator-42',
    sessionId: 'session-daily-monitoring'
  },
  textSignals: [socialMediaSignal],
  visionSignals: [satelliteImageSignal],
  quantSignals: [trafficFlowSensor],
  options: {
    enableFusion: true,
    enableDisruptionAssessment: true,
    enableAlertGeneration: true,
    minConfidenceThreshold: 0.7,
    geographicBounds: {
      latitude: 34.0522,
      longitude: -118.2437,
      uncertaintyRadiusMeters: 50000,
      placeName: 'Los Angeles Metro Area'
    },
    timeWindow: {
      startTime: '2026-03-09T14:00:00Z',
      endTime: '2026-03-09T15:00:00Z'
    },
    focusSectors: [
      SupplyChainSector.TRANSPORTATION,
      SupplyChainSector.LOGISTICS
    ]
  },
  requestor: {
    userId: 'emergency-coordinator-42',
    organization: 'LA County Emergency Management',
    role: 'Operations Coordinator'
  }
};

// ============================================================================
// Example 5: Creating a Fused Event
// ============================================================================

const fusedTrafficEvent: FusedEvent = {
  eventId: 'evt-i405-accident-20260309-1430',
  eventType: 'transportation_incident',
  title: 'Multi-Vehicle Accident on I-405 Southbound near LAX',
  description: 'Severe multi-vehicle accident blocking all southbound lanes of Interstate 405 near Los Angeles International Airport. Traffic flow reduced by 97% from normal levels. Emergency response active on scene.',
  confidence: 0.92,
  severity: SeverityLevel.HIGH,
  location: {
    latitude: 33.9425,
    longitude: -118.4081,
    placeName: 'I-405 Southbound, Mile Marker 23, near LAX',
    region: 'Los Angeles County',
    countryCode: 'US',
    geometry: {
      type: 'LineString',
      coordinates: [
        [-118.4081, 33.9425],
        [-118.4085, 33.9420],
        [-118.4090, 33.9415]
      ]
    }
  },
  timeReference: {
    timestamp: '2026-03-09T14:30:15Z',
    startTime: '2026-03-09T14:28:00Z',
    precision: 'minute',
    timezone: 'America/Los_Angeles',
    confidence: 0.88
  },
  sourceSignalIds: [
    'twitter-1234567890',
    'sat-noaa20-img-001',
    'sensor-i405-mm23-flow'
  ],
  observations: [
    {
      observationId: 'obs-001',
      observationType: 'traffic_anomaly',
      description: 'Traffic flow dropped from 650 to 12 vehicles per minute',
      sourceSignalIds: ['sensor-i405-mm23-flow'],
      confidence: 0.95,
      severity: SeverityLevel.HIGH,
      affectedSectors: [SupplyChainSector.TRANSPORTATION],
      affectedAssets: [AssetType.ROAD]
    },
    {
      observationId: 'obs-002',
      observationType: 'emergency_response_active',
      description: 'Emergency vehicles detected at incident location',
      sourceSignalIds: ['sat-noaa20-img-001', 'twitter-1234567890'],
      confidence: 0.82,
      severity: SeverityLevel.MODERATE
    }
  ],
  affectedSectors: [
    SupplyChainSector.TRANSPORTATION,
    SupplyChainSector.LOGISTICS
  ],
  affectedAssets: [
    AssetType.ROAD,
    AssetType.EVACUATION_ROUTE
  ],
  impactRadiusMeters: 15000,
  status: 'active',
  detectedAt: '2026-03-09T14:33:45Z',
  updatedAt: '2026-03-09T14:35:00Z',
  relatedEventIds: [],
  metadata: {
    lanesClosed: 4,
    totalLanes: 4,
    estimatedVehiclesAffected: 3000,
    nearbyAirport: 'LAX'
  }
};

// ============================================================================
// Example 6: Creating a Disruption Assessment
// ============================================================================

const disruptionAssessment: DisruptionAssessment = {
  assessmentId: 'assess-evt-i405-001',
  eventId: 'evt-i405-accident-20260309-1430',
  disruptionSeverity: SeverityLevel.HIGH,
  confidence: 0.88,
  sectorImpacts: [
    {
      sector: SupplyChainSector.TRANSPORTATION,
      severity: SeverityLevel.CRITICAL,
      description: 'Complete blockage of major north-south freight corridor. Alternate routes at capacity.',
      estimatedRecoveryHours: 4
    },
    {
      sector: SupplyChainSector.LOGISTICS,
      severity: SeverityLevel.HIGH,
      description: 'Delivery delays expected for LAX cargo operations and regional distribution centers.',
      estimatedRecoveryHours: 12
    },
    {
      sector: SupplyChainSector.FUEL_DISTRIBUTION,
      severity: SeverityLevel.MODERATE,
      description: 'Fuel tanker trucks unable to reach LAX. Backup supplies available for 8 hours.',
      estimatedRecoveryHours: 8
    }
  ],
  assetImpacts: [
    {
      assetType: AssetType.ROAD,
      assetId: 'i405-sb-mm23',
      assetName: 'Interstate 405 Southbound',
      location: fusedTrafficEvent.location,
      status: 'offline',
      severity: SeverityLevel.CRITICAL,
      description: 'All southbound lanes closed'
    },
    {
      assetType: AssetType.AIRPORT,
      assetId: 'lax',
      assetName: 'Los Angeles International Airport',
      status: 'degraded',
      severity: SeverityLevel.MODERATE,
      description: 'Ground transportation access severely limited'
    }
  ],
  economicImpact: {
    estimatedCostUSD: 8500000,
    economicSectors: ['aviation', 'logistics', 'tourism'],
    affectedBusinessCount: 450
  },
  populationImpact: {
    affectedPopulation: 125000,
    evacuationRequired: false,
    criticalServicesDisrupted: ['airport_access', 'emergency_routes']
  },
  cascadingEffects: [
    {
      description: 'Secondary congestion on alternate routes (I-110, I-710)',
      sectors: [SupplyChainSector.TRANSPORTATION],
      likelihood: 0.95
    },
    {
      description: 'Airport cargo delays affecting regional supply chains',
      sectors: [SupplyChainSector.LOGISTICS, SupplyChainSector.RETAIL],
      likelihood: 0.82
    }
  ],
  recommendations: [
    'Activate alternate freight routing protocols',
    'Coordinate with LAX operations for cargo prioritization',
    'Deploy additional emergency response resources',
    'Issue public advisories for alternate routes'
  ],
  assessedAt: '2026-03-09T14:36:00Z',
  validUntil: '2026-03-09T18:00:00Z',
  assessedBy: 'ai-disruption-analyzer-v2.1'
};

// ============================================================================
// Example 7: Creating an Alert Recommendation
// ============================================================================

const alertRecommendation: AlertRecommendation = {
  alertId: 'alert-i405-001',
  eventId: 'evt-i405-accident-20260309-1430',
  assessmentId: 'assess-evt-i405-001',
  priority: AlertPriority.URGENT,
  title: 'URGENT: Major I-405 Closure Near LAX - Freight Rerouting Required',
  message: `Critical transportation disruption: All southbound lanes of Interstate 405 are closed near LAX due to a multi-vehicle accident. Complete blockage of major freight corridor with estimated 4-hour recovery time.

IMMEDIATE IMPACTS:
- 15km traffic backlog forming
- LAX ground access severely limited
- Regional freight corridor offline

RECOMMENDED ACTIONS:
- Activate emergency freight routing protocol
- Reroute all southbound freight to I-110/I-710
- Coordinate with LAX for cargo prioritization
- Issue public travel advisories

RESOURCES NEEDED:
- Additional traffic management personnel
- Tow trucks (heavy duty) - 3 units
- Alternative route signage deployment`,
  targetAudience: [
    'transportation_coordinators',
    'freight_logistics_managers',
    'airport_operations',
    'public_information_officers'
  ],
  alertArea: {
    latitude: 33.9425,
    longitude: -118.4081,
    uncertaintyRadiusMeters: 25000,
    placeName: 'South Bay / LAX Area'
  },
  recommendedActions: [
    'Activate alternate freight routing protocols',
    'Deploy traffic management personnel to alternate routes',
    'Issue travel advisory via emergency notification system',
    'Coordinate with LAX operations center',
    'Request additional heavy tow truck resources',
    'Establish incident command post'
  ],
  resourcesNeeded: [
    {
      resourceType: 'heavy_tow_truck',
      quantity: 3,
      priority: AlertPriority.URGENT
    },
    {
      resourceType: 'traffic_management_personnel',
      quantity: 8,
      priority: AlertPriority.HIGH
    },
    {
      resourceType: 'variable_message_signs',
      quantity: 6,
      priority: AlertPriority.HIGH
    }
  ],
  timeConstraints: {
    issueBy: '2026-03-09T14:40:00Z',
    responseWindowMinutes: 30
  },
  createdAt: '2026-03-09T14:36:30Z',
  status: 'active',
  relatedAlertIds: []
};

// ============================================================================
// Example 8: Creating a Map Feature for Visualization
// ============================================================================

const mapFeature: MapFeaturePayload = {
  featureId: 'map-evt-i405-001',
  featureType: 'event',
  dataId: 'evt-i405-accident-20260309-1430',
  geometry: {
    type: 'Point',
    coordinates: [-118.4081, 33.9425]
  },
  properties: {
    title: 'Multi-Vehicle Accident - I-405 SB',
    description: 'All lanes closed, 4-hour estimated recovery',
    severity: SeverityLevel.HIGH,
    status: 'active',
    color: '#ff6600',
    icon: 'traffic-incident'
  },
  style: {
    fillColor: '#ff6600',
    strokeColor: '#cc5200',
    strokeWidth: 3,
    opacity: 0.85,
    iconUrl: '/assets/icons/traffic-incident-high.png',
    iconSize: [48, 48]
  },
  popupContent: `
    <h3>Multi-Vehicle Accident</h3>
    <p><strong>Location:</strong> I-405 SB Mile Marker 23</p>
    <p><strong>Severity:</strong> HIGH</p>
    <p><strong>Status:</strong> Active - All lanes closed</p>
    <p><strong>Impact:</strong> 15km traffic backup, ~3000 vehicles affected</p>
    <p><strong>Recovery Estimate:</strong> 4 hours</p>
    <a href="#/events/evt-i405-accident-20260309-1430">View Details →</a>
  `,
  layer: 'active-incidents',
  zIndex: 900,
  visible: true,
  timestamp: '2026-03-09T14:36:45Z'
};

// ============================================================================
// Example 9: Creating a Dashboard Summary
// ============================================================================

const dashboardSummary: DashboardSummary = {
  generatedAt: '2026-03-09T14:37:00Z',
  timeWindow: {
    startTime: '2026-03-09T06:00:00Z',
    endTime: '2026-03-09T14:37:00Z'
  },
  situationStatus: {
    overallSeverity: SeverityLevel.MODERATE,
    activeEventsCount: 8,
    criticalAlertsCount: 1,
    affectedRegions: ['Los Angeles County', 'Orange County']
  },
  eventsBySeverity: [
    { severity: SeverityLevel.CRITICAL, count: 0, trend: 'stable' },
    { severity: SeverityLevel.HIGH, count: 1, trend: 'increasing' },
    { severity: SeverityLevel.MODERATE, count: 4, trend: 'stable' },
    { severity: SeverityLevel.LOW, count: 3, trend: 'decreasing' }
  ],
  sectorDisruptions: [
    {
      sector: SupplyChainSector.TRANSPORTATION,
      severity: SeverityLevel.HIGH,
      affectedAssetsCount: 3,
      description: 'Major highway incident affecting freight corridors'
    },
    {
      sector: SupplyChainSector.LOGISTICS,
      severity: SeverityLevel.MODERATE,
      affectedAssetsCount: 5,
      description: 'Delivery delays due to transportation disruptions'
    }
  ],
  alerts: {
    urgent: 1,
    high: 2,
    normal: 5,
    low: 0
  },
  keyMetrics: [
    {
      label: 'Signals Processed (8h)',
      value: 3847,
      trend: 'up',
      changePercent: 12
    },
    {
      label: 'Avg Detection Latency',
      value: '2.3',
      unit: 'minutes',
      trend: 'down',
      changePercent: -15
    },
    {
      label: 'Fusion Confidence',
      value: '89',
      unit: '%',
      trend: 'stable',
      changePercent: 0
    },
    {
      label: 'Active Response Ops',
      value: 6,
      trend: 'stable'
    }
  ],
  recentSignificantEvents: [
    {
      eventId: 'evt-i405-accident-20260309-1430',
      title: 'Multi-Vehicle Accident on I-405 SB near LAX',
      severity: SeverityLevel.HIGH,
      timestamp: '2026-03-09T14:30:15Z'
    }
  ],
  hotspots: [
    {
      location: {
        latitude: 33.9425,
        longitude: -118.4081,
        placeName: 'I-405 Corridor / LAX Area'
      },
      eventCount: 3,
      highestSeverity: SeverityLevel.HIGH
    }
  ],
  systemHealth: {
    signalsProcessedCount: 3847,
    averageProcessingLatencyMs: 138,
    dataQuality: 0.94,
    warnings: []
  }
};

// ============================================================================
// Example 10: Complete Final API Response
// ============================================================================

const finalResponse: FinalApiResponse = {
  trace: incidentRequest.trace,
  status: 'success',
  processedAt: '2026-03-09T14:37:15Z',
  processingDurationMs: 2450,
  events: [fusedTrafficEvent],
  disruptions: [disruptionAssessment],
  alerts: [alertRecommendation],
  mapFeatures: [mapFeature],
  dashboardSummary,
  warnings: [
    {
      code: 'LOW_SOURCE_CONFIDENCE',
      message: 'Social media signal has below-average reliability score',
      severity: 'low'
    }
  ],
  metadata: {
    signalsProcessed: 3,
    observationsExtracted: 2,
    eventsCreated: 1,
    modelVersions: {
      'text-analyzer': 'v2.4.1',
      'vision-detector': 'v3.1.0',
      'fusion-engine': 'v1.8.2',
      'disruption-assessor': 'v2.1.3'
    }
  }
};

// ============================================================================
// Example 11: Using Type Guards
// ============================================================================

function processSignalsByType(signals: Array<TextSignal | VisionSignal | QuantSignal>) {
  const textSignals = signals.filter(isTextSignal);
  const visionSignals = signals.filter(isVisionSignal);
  const quantSignals = signals.filter(isQuantSignal);
  
  console.log(`Processing ${textSignals.length} text signals`);
  console.log(`Processing ${visionSignals.length} vision signals`);
  console.log(`Processing ${quantSignals.length} quantitative signals`);
  
  // Now TypeScript knows the correct types
  textSignals.forEach(signal => {
    console.log(`Text content: ${signal.content.substring(0, 50)}...`);
  });
  
  visionSignals.forEach(signal => {
    console.log(`Image URL: ${signal.mediaUrl}`);
  });
  
  quantSignals.forEach(signal => {
    console.log(`Measurement: ${signal.value} ${signal.unit}`);
  });
}

// Usage
processSignalsByType([
  socialMediaSignal,
  satelliteImageSignal,
  trafficFlowSensor
]);

// ============================================================================
// Example 12: Error Handling
// ============================================================================

const apiError: AppError = {
  code: 'FUSION_TIMEOUT',
  message: 'Event fusion processing exceeded timeout threshold',
  statusCode: 504,
  details: {
    timeoutMs: 30000,
    signalsProcessed: 47,
    eventsCompleted: 12,
    eventsPending: 3
  },
  timestamp: '2026-03-09T14:45:00Z',
  trace: {
    requestId: 'req-timeout-example',
    timestamp: '2026-03-09T14:44:30Z'
  }
};

// ============================================================================
// Export examples for testing/documentation
// ============================================================================

export const examples = {
  signals: {
    socialMedia: socialMediaSignal,
    satellite: satelliteImageSignal,
    sensor: trafficFlowSensor
  },
  request: incidentRequest,
  event: fusedTrafficEvent,
  assessment: disruptionAssessment,
  alert: alertRecommendation,
  mapFeature,
  dashboard: dashboardSummary,
  response: finalResponse,
  error: apiError
};
