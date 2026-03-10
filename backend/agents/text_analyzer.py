"""
Text Signal Analyzer

Converts raw text signals into structured ExtractedObservation objects.
Uses NLP and LLM analysis to extract key information from text-based disaster reports,
social media posts, emergency alerts, and news articles.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid
import re


class TextAnalyzer:
    """
    Analyzes text signals to extract structured observations.
    
    In production, this will use:
    - LLM models for semantic understanding
    - NER (Named Entity Recognition) for location/organization extraction
    - Event classification models
    - Sentiment/severity analysis
    - Sector and asset identification
    """
    
    def __init__(self):
        """Initialize the text analyzer."""
        # TODO: Initialize NLP models and LLM service
        # self.llm_service = LLMService()
        # self.ner_model = spacy.load("en_core_web_trf")
        # self.classifier = load_event_classifier()
        pass
    
    async def analyze(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a text signal and extract observations.
        
        Args:
            signal: TextSignal object from provider
            
        Returns:
            List of ExtractedObservation objects
        """
        content = signal.get("content", "")
        if not content:
            return []
        
        # TODO: Replace with real LLM-based extraction
        # Example production call:
        # observations = await self.llm_service.extract_observations(
        #     text=content,
        #     source=signal.get("source"),
        #     context=signal.get("metadata")
        # )
        
        # For now, use rule-based mock extraction
        observations = await self._mock_extract(signal)
        
        return observations
    
    async def _mock_extract(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Mock extraction logic (placeholder for LLM).
        
        Extracts observations using simple keyword matching and heuristics.
        In production, this will be replaced with sophisticated NLP/LLM analysis.
        """
        content = signal.get("content", "").lower()
        metadata = signal.get("metadata", {})
        
        # Extract observation type based on keywords
        observation_type = self._classify_observation_type(content)
        
        # Extract severity
        severity = self._infer_severity(content, metadata)
        
        # Extract affected sectors and assets
        sectors = self._extract_sectors(content, metadata)
        assets = self._extract_assets(content, metadata)
        
        # Extract entities (simplified)
        entities = self._extract_entities(content)
        
        # Build structured observation
        observation = {
            "observationId": f"obs-txt-{uuid.uuid4().hex[:12]}",
            "observationType": observation_type,
            "description": self._generate_description(signal, observation_type),
            "sourceSignalIds": [signal.get("signalId", "unknown")],
            "confidence": self._calculate_confidence(signal, content),
            "location": signal.get("location"),
            "timeReference": {
                "observedAt": signal.get("createdAt"),
                "reportedAt": signal.get("receivedAt")
            },
            "severity": severity,
            "affectedSectors": sectors,
            "affectedAssets": assets,
            "extractedData": {
                "rawText": signal.get("content"),
                "source": signal.get("source"),
                "entities": entities,
                "keywords": self._extract_keywords(content),
                "language": signal.get("language", "en")
            },
            "evidence": [
                f"Text signal from {signal.get('source')}",
                f"Content: {signal.get('content')[:100]}..."
            ]
        }
        
        return [observation]
    
    def _classify_observation_type(self, content: str) -> str:
        """Classify observation type based on content keywords."""
        # TODO: Replace with ML classifier or LLM
        
        if any(word in content for word in ["collision", "accident", "crash", "wreck"]):
            return "traffic_incident"
        elif any(word in content for word in ["fire", "burning", "flames", "smoke"]):
            return "fire_incident"
        elif any(word in content for word in ["flood", "flooding", "water", "inundated"]):
            return "flooding"
        elif any(word in content for word in ["closure", "closed", "blocked", "shutdown"]):
            return "infrastructure_closure"
        elif any(word in content for word in ["collapse", "collapsed", "structural failure"]):
            return "structural_failure"
        elif any(word in content for word in ["shortage", "unavailable", "depleted", "empty"]):
            return "supply_shortage"
        elif any(word in content for word in ["delay", "delayed", "backlog", "congestion"]):
            return "logistics_delay"
        elif any(word in content for word in ["evacuation", "evacuate", "evacuating"]):
            return "evacuation_order"
        elif any(word in content for word in ["power", "outage", "electricity", "blackout"]):
            return "power_outage"
        elif any(word in content for word in ["storm", "snow", "ice", "blizzard", "wind"]):
            return "weather_event"
        else:
            return "general_disruption"
    
    def _infer_severity(self, content: str, metadata: Dict[str, Any]) -> str:
        """Infer severity level from text content."""
        # TODO: Replace with ML-based severity classifier
        
        # Use metadata hint if available
        severity_hint = metadata.get("severity_hint")
        if severity_hint:
            return severity_hint
        
        # Critical indicators
        if any(word in content for word in ["critical", "emergency", "immediate", "urgent"]):
            return "critical"
        
        # High severity indicators
        if any(word in content for word in ["major", "severe", "significant", "extensive"]):
            return "high"
        
        # Moderate severity indicators
        if any(word in content for word in ["moderate", "partial", "limited"]):
            return "moderate"
        
        # Default to moderate
        return "moderate"
    
    def _extract_sectors(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Extract affected supply chain sectors."""
        # TODO: Replace with NER + sector classification model
        
        # Use metadata hint if available
        sectors_hint = metadata.get("sectors_hint", [])
        if sectors_hint:
            return sectors_hint
        
        sectors = []
        
        if any(word in content for word in ["highway", "road", "traffic", "bridge", "i-5", "i-405"]):
            sectors.append("transportation")
        
        if any(word in content for word in ["port", "shipping", "vessel", "cargo", "freight"]):
            sectors.append("logistics")
        
        if any(word in content for word in ["warehouse", "distribution", "storage", "facility"]):
            sectors.append("warehousing")
        
        if any(word in content for word in ["fuel", "gas", "pipeline", "refinery", "energy"]):
            sectors.append("energy")
        
        if any(word in content for word in ["manufacturing", "factory", "production", "plant"]):
            sectors.append("manufacturing")
        
        return sectors if sectors else ["transportation"]  # Default fallback
    
    def _extract_assets(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Extract affected asset types."""
        # TODO: Replace with entity recognition + asset mapping model
        
        # Use metadata hint if available
        assets_hint = metadata.get("assets_hint", [])
        if assets_hint:
            return assets_hint
        
        assets = []
        
        if any(word in content for word in ["highway", "freeway", "interstate", "road"]):
            assets.append("road")
        
        if "bridge" in content:
            assets.append("bridge")
        
        if "port" in content or "terminal" in content:
            assets.append("port")
        
        if "warehouse" in content or "distribution center" in content:
            assets.append("warehouse")
        
        if "rail" in content or "train" in content or "tracks" in content:
            assets.append("rail_line")
        
        if "pipeline" in content:
            assets.append("pipeline")
        
        if "refinery" in content:
            assets.append("refinery")
        
        return assets if assets else ["road"]  # Default fallback
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        # TODO: Replace with spaCy NER or LLM-based entity extraction
        # Example:
        # doc = self.ner_model(content)
        # entities = {
        #     "locations": [ent.text for ent in doc.ents if ent.label_ == "GPE"],
        #     "organizations": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        #     "dates": [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        # }
        
        # Simple pattern matching for now
        entities = {
            "locations": [],
            "organizations": [],
            "routes": []
        }
        
        # Extract highway/route numbers
        route_pattern = r'I-\d+|SR-\d+|US-\d+'
        entities["routes"] = re.findall(route_pattern, content, re.IGNORECASE)
        
        # Extract city names (simplified)
        cities = ["Seattle", "Tacoma", "Bellevue", "Everett", "Kent", "Kirkland"]
        entities["locations"] = [city for city in cities if city.lower() in content.lower()]
        
        return entities
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content."""
        # TODO: Replace with TF-IDF or keyword extraction model
        
        # Simple keyword extraction based on frequency and importance
        important_terms = [
            "accident", "collision", "closure", "blocked", "fire", "flood",
            "shortage", "delay", "evacuation", "emergency", "critical",
            "shutdown", "failure", "damage", "disruption"
        ]
        
        keywords = [term for term in important_terms if term in content.lower()]
        return keywords[:5]  # Limit to top 5
    
    def _calculate_confidence(self, signal: Dict[str, Any], content: str) -> float:
        """Calculate confidence score for the observation."""
        # TODO: Replace with ML-based confidence estimation
        
        base_confidence = signal.get("confidence", 0.7)
        
        # Boost confidence for emergency services and official sources
        source = signal.get("source", "")
        if source in ["emergency_services", "dot", "corporate"]:
            base_confidence = min(base_confidence + 0.15, 1.0)
        elif source in ["news"]:
            base_confidence = min(base_confidence + 0.10, 1.0)
        elif source in ["twitter", "reddit"]:
            base_confidence = max(base_confidence - 0.10, 0.4)
        
        # Adjust based on content length (longer = more detail = higher confidence)
        if len(content) > 200:
            base_confidence = min(base_confidence + 0.05, 1.0)
        
        return round(base_confidence, 2)
    
    def _generate_description(self, signal: Dict[str, Any], observation_type: str) -> str:
        """Generate a concise description of the observation."""
        # TODO: Replace with LLM-based summarization
        # Example:
        # description = await self.llm_service.summarize(
        #     text=signal.get("content"),
        #     max_length=150
        # )
        
        content = signal.get("content", "")
        
        # For now, use first sentence or first 150 chars
        sentences = content.split('. ')
        if sentences:
            description = sentences[0]
            if len(description) > 150:
                description = description[:147] + "..."
            return description
        
        return content[:147] + "..." if len(content) > 150 else content
