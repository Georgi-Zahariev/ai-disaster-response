# Scoring Service

**Responsibility**: Confidence scoring and quality assessment for all system outputs.

## Purpose

The scoring service evaluates the reliability and confidence of:
- Raw signals (based on source reliability)
- Extracted observations (based on extraction confidence)
- Fused events (based on multi-modal agreement)
- Disruption assessments (based on evidence strength)

## Scoring Factors

### Source Reliability
- Historical accuracy of the source
- Type of source (satellite > sensor > social media)
- Verification status
- Recency and update frequency

### Signal Quality
- Completeness (all required fields present)
- Precision (low uncertainty)
- Currency (recent vs. outdated)
- Internal consistency

### Multi-Modal Agreement
- Cross-validation between modalities
- Number of sources reporting same observation
- Consensus vs. conflicting reports

### Evidence Strength
- Direct observation vs. inference
- First-hand vs. second-hand reports
- Corroboration by multiple independent sources

## Confidence Scales

All confidence scores are normalized to [0.0, 1.0]:
- 0.9-1.0: Very high confidence (multiple verified sources)
- 0.7-0.9: High confidence (reliable source or cross-validated)
- 0.5-0.7: Moderate confidence (single source or some validation)
- 0.3-0.5: Low confidence (unreliable source or weak evidence)
- 0.0-0.3: Very low confidence (unverified or contradictory)
