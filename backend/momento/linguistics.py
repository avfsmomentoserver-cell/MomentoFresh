"""
Enhanced Linguistics Engine for MomentoFresh

Provides extended semantic vocabulary for crash game analysis.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .config import settings
from .analysis import AnalysisPayload, get_analysis_payload_cached

logger = logging.getLogger(__name__)


class BandClassification(Enum):
    """Multiplier band classifications."""
    ULTRA_CRASH = "ultra-crash"
    CRASH = "crash"
    DEEP_LOW = "deep-low"
    LOW = "low"
    NEUTRAL = "neutral"
    MID = "mid"
    HIGH = "high"
    IGNITION = "ignition"
    MOONSHOT = "moonshot"
    MEGA_MOONSHOT = "mega-moonshot"
    STRATOSPHERIC = "stratospheric"


class StateClassification(Enum):
    """Game state classifications."""
    COMPRESSION = "compression"
    EXPANSION = "expansion"
    LADDER_ASCENDING = "ladder-ascending"
    LADDER_DESCENDING = "ladder-descending"
    RESISTANCE = "resistance"
    SUPPORT = "support"
    STREAK_LOW = "streak-low"
    STREAK_HIGH = "streak-high"
    EDGE_FIT = "edge-fit"
    PRESSURE_BUILDING = "pressure-building"
    PRESSURE_RELEASE = "pressure-release"
    MOONSHOT_APPROACH = "moonshot-approach"
    COLLAPSE_APPROACH = "collapse-approach"


class PressureVocabulary(Enum):
    """Pressure-related vocabulary."""
    BUILDING = "building"
    SUSTAINED = "sustained"
    RELEASING = "releasing"
    CRITICAL = "critical"
    OVERFLOW = "overflow"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"


@dataclass
class LinguisticAnalysis:
    """Complete linguistic analysis result."""
    primitive: Dict[str, Any]
    normalized: Dict[str, Any]
    band: Dict[str, Any]
    state: Dict[str, Any]
    pattern: Dict[str, Any]
    pressure: Dict[str, Any]
    relativity: Dict[str, Any]
    narrative: Dict[str, Any]
    vocabulary: Dict[str, List[str]]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primitive": self.primitive,
            "normalized": self.normalized,
            "band": self.band,
            "state": self.state,
            "pattern": self.pattern,
            "pressure": self.pressure,
            "relativity": self.relativity,
            "narrative": self.narrative,
            "vocabulary": self.vocabulary,
            "timestamp": self.timestamp.isoformat(),
        }


def classify_band_linguistics(multiplier: float, reference: float = 50.0) -> Tuple[str, str]:
    """
    Classify a multiplier into linguistic bands.
    
    Returns:
        Tuple of (band, description)
    """
    # Convert to equal baseline points for classification
    if multiplier <= 1.0:
        points = -reference * (2 - multiplier)
    else:
        points = (multiplier - 1) * (2 * reference) - reference
    
    # Classify based on points
    if points <= -reference * 2:
        band = BandClassification.ULTRA_CRASH.value
        description = "Extreme crash territory - multiplier at or below 0x"
    elif points <= -reference * 1.5:
        band = BandClassification.CRASH.value
        description = "Deep crash zone - multiplier below 0.5x"
    elif points <= -reference * 1.0:
        band = BandClassification.DEEP_LOW.value
        description = "Strong downside - multiplier at or below 1.0x"
    elif points <= -reference * 0.5:
        band = BandClassification.LOW.value
        description = "Moderate downside - multiplier between 1.0x and 1.25x"
    elif points <= 0:
        band = BandClassification.NEUTRAL.value
        description = "Balanced zone - multiplier around 1.5x"
    elif points <= reference * 0.5:
        band = BandClassification.MID.value
        description = "Moderate upside - multiplier between 1.5x and 1.75x"
    elif points <= reference * 1.0:
        band = BandClassification.HIGH.value
        description = "Strong upside - multiplier between 1.75x and 2.0x"
    elif points <= reference * 1.5:
        band = BandClassification.IGNITION.value
        description = "Approaching moonshot - multiplier between 2.0x and 2.5x"
    elif points <= reference * 2.0:
        band = BandClassification.MOONSHOT.value
        description = "High multiplier zone - multiplier between 2.5x and 50x"
    else:
        band = BandClassification.STRATOSPHERIC.value
        description = "Extreme upside - multiplier above 50x"
    
    return band, description


def classify_state_linguistics(
    multipliers: List[float],
    pressure_score: Optional[float] = None
) -> Tuple[str, str]:
    """
    Classify the current state into linguistic categories.
    
    Returns:
        Tuple of (state, description)
    """
    if not multipliers or len(multipliers) < 2:
        return StateClassification.NEUTRAL.value, "Insufficient data"
    
    # Calculate trend
    recent = multipliers[:5]
    trend = (recent[0] - recent[-1]) / len(recent)
    
    # Check for streaks
    ascending_streak = 0
    descending_streak = 0
    
    for i in range(1, len(recent)):
        if recent[i] > recent[i-1]:
            ascending_streak += 1
            descending_streak = 0
        elif recent[i] < recent[i-1]:
            descending_streak += 1
            ascending_streak = 0
    
    # Check pressure
    if pressure_score and pressure_score > 80:
        if trend > 0:
            return StateClassification.MOONSHOT_APPROACH.value, f"High pressure ({pressure_score:.0f}%) with upward trend"
        else:
            return StateClassification.COLLAPSE_APPROACH.value, f"High pressure ({pressure_score:.0f}%) with downward trend"
    
    # Check for streaks
    if ascending_streak >= 3:
        return StateClassification.LADDER_ASCENDING.value, f"Ascending ladder with {ascending_streak} round streak"
    elif descending_streak >= 3:
        return StateClassification.LADDER_DESCENDING.value, f"Descending ladder with {descending_streak} round streak"
    
    # Check for compression/expansion
    if len(recent) >= 3:
        volatility = (sum((recent[i] - recent[i-1])**2 for i in range(1, len(recent))) / len(recent)) ** 0.5
        if volatility < 0.2:
            return StateClassification.COMPRESSION.value, f"Low volatility compression (std: {volatility:.2f})"
        elif volatility > 1.0:
            return StateClassification.EXPANSION.value, f"High volatility expansion (std: {volatility:.2f})"
    
    return StateClassification.NEUTRAL.value, "Stable pattern"


def analyze_linguistics(source: str, limit: Optional[int] = None) -> LinguisticAnalysis:
    """
    Perform complete linguistic analysis for a source.
    
    Args:
        source: The game source
        limit: Maximum rounds to analyze
        
    Returns:
        LinguisticAnalysis with all layers
    """
    payload = get_analysis_payload_cached(source, limit or settings.default_round_limit)
    multipliers = payload.multipliers
    
    if not multipliers:
        return LinguisticAnalysis(
            primitive={},
            normalized={},
            band={},
            state={},
            pattern={},
            pressure={},
            relativity={},
            narrative={},
            vocabulary={},
        )
    
    # Primitive layer - raw values
    primitive = {
        "count": len(multipliers),
        "min": min(multipliers),
        "max": max(multipliers),
        "mean": sum(multipliers) / len(multipliers),
    }
    
    # Normalized layer - normalized values
    normalized_multipliers = [(m - primitive["mean"]) / primitive["mean"] if primitive["mean"] > 0 else 0 for m in multipliers]
    normalized = {
        "mean": sum(normalized_multipliers) / len(normalized_multipliers),
        "std_dev": (sum(n**2 for n in normalized_multipliers) / len(normalized_multipliers)) ** 0.5,
    }
    
    # Band layer - band classification
    band_distribution = {}
    for m in multipliers:
        band, _ = classify_band_linguistics(m)
        band_distribution[band] = band_distribution.get(band, 0) + 1
    
    band = {
        "distribution": band_distribution,
        "dominant": max(band_distribution.items(), key=lambda x: x[1])[0] if band_distribution else None,
    }
    
    # State layer - state classification
    state, state_desc = classify_state_linguistics(multipliers)
    state_analysis = {
        "current": state,
        "description": state_desc,
    }
    
    # Pattern layer
    pattern = {
        "trend": "ascending" if multipliers[0] > multipliers[-1] else "descending",
        "volatility": payload.stats.get("std_dev", 0),
    }
    
    # Pressure layer (placeholder - integrated with pressure plugin)
    pressure = {
        "score": 0,
        "state": "neutral",
    }
    
    # Relativity layer
    relativity = {
        "relative_to_mean": [(m - primitive["mean"]) / primitive["mean"] * 100 if primitive["mean"] > 0 else 0 for m in multipliers],
        "relative_to_max": [(m - primitive["max"]) / primitive["max"] * 100 if primitive["max"] > 0 else 0 for m in multipliers],
    }
    
    # Narrative layer
    narrative = {
        "summary": f"Analyzed {len(multipliers)} rounds with mean {primitive['mean']:.2f}x, range {primitive['min']:.2f}x - {primitive['max']:.2f}x",
        "insight": f"Current state: {state}. Dominant band: {band.get('dominant', 'N/A')}",
    }
    
    # Vocabulary
    vocabulary = {
        "bands": [b.value for b in BandClassification],
        "states": [s.value for s in StateClassification],
        "pressure": [p.value for p in PressureVocabulary],
    }
    
    return LinguisticAnalysis(
        primitive=primitive,
        normalized=normalized,
        band=band,
        state=state_analysis,
        pattern=pattern,
        pressure=pressure,
        relativity=relativity,
        narrative=narrative,
        vocabulary=vocabulary,
    )


def get_band_distribution(source: str, limit: Optional[int] = None) -> Dict[str, int]:
    """Get band distribution for a source."""
    analysis = analyze_linguistics(source, limit)
    return analysis.band.get("distribution", {})


def get_state_distribution(source: str, limit: Optional[int] = None) -> Dict[str, int]:
    """Get state distribution for a source."""
    payload = get_analysis_payload_cached(source, limit or settings.default_round_limit)
    multipliers = payload.multipliers
    
    if not multipliers or len(multipliers) < 2:
        return {}
    
    # Analyze last N rounds for state
    window_size = min(10, len(multipliers))
    states = {}
    
    for i in range(0, len(multipliers) - window_size + 1, max(1, window_size // 2)):
        window = multipliers[i:i + window_size]
        state, _ = classify_state_linguistics(window)
        states[state] = states.get(state, 0) + 1
    
    return states