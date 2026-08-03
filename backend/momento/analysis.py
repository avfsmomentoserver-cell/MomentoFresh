"""
Core Analysis Engine for MomentoFresh

Computes metrics, patterns, and insights from crash game rounds.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .config import settings
from .db import Round, get_session, session_scope

logger = logging.getLogger(__name__)


@dataclass
class AnalysisPayload:
    """Complete analysis payload for a set of rounds."""
    rounds: List[Dict[str, Any]]
    count: int
    source: str
    timestamps: List[datetime]
    multipliers: List[float]
    stats: Dict[str, Any]
    patterns: Dict[str, Any]
    pressure: Optional[Dict[str, Any]] = None
    equal_baseline: Optional[Dict[str, Any]] = None
    linguistics: Optional[Dict[str, Any]] = None
    signals: Optional[List[Dict[str, Any]]] = None
    forecast: Optional[Dict[str, Any]] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rounds": self.rounds,
            "count": self.count,
            "source": self.source,
            "timestamps": [t.isoformat() for t in self.timestamps],
            "multipliers": self.multipliers,
            "stats": self.stats,
            "patterns": self.patterns,
            "pressure": self.pressure,
            "equal_baseline": self.equal_baseline,
            "linguistics": self.linguistics,
            "signals": self.signals,
            "forecast": self.forecast,
            "last_updated": self.last_updated.isoformat(),
        }


def calculate_basic_stats(multipliers: List[float]) -> Dict[str, Any]:
    """Calculate basic statistics for a list of multipliers."""
    if not multipliers:
        return {}
    
    multipliers = [m for m in multipliers if m is not None]
    if not multipliers:
        return {}
    
    return {
        "count": len(multipliers),
        "min": min(multipliers),
        "max": max(multipliers),
        "mean": sum(multipliers) / len(multipliers),
        "median": sorted(multipliers)[len(multipliers) // 2],
        "std_dev": (sum((x - (sum(multipliers) / len(multipliers))) ** 2 for x in multipliers) / len(multipliers)) ** 0.5 if len(multipliers) > 1 else 0,
        "sum": sum(multipliers),
        "range": max(multipliers) - min(multipliers),
    }


def calculate_patterns(multipliers: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
    """Detect patterns in multiplier data."""
    if len(multipliers) < 2:
        return {}
    
    # Calculate streaks
    streaks = {"ascending": 0, "descending": 0, "max_ascending": 0, "max_descending": 0}
    current_streak = 0
    current_direction = None
    
    for i in range(1, len(multipliers)):
        if multipliers[i] > multipliers[i-1]:
            if current_direction == "ascending":
                current_streak += 1
            else:
                current_streak = 1
                current_direction = "ascending"
            streaks["ascending"] += 1
            streaks["max_ascending"] = max(streaks["max_ascending"], current_streak)
        elif multipliers[i] < multipliers[i-1]:
            if current_direction == "descending":
                current_streak += 1
            else:
                current_streak = 1
                current_direction = "descending"
            streaks["descending"] += 1
            streaks["max_descending"] = max(streaks["max_descending"], current_streak)
    
    # Calculate volatility
    returns = [(multipliers[i] - multipliers[i-1]) / multipliers[i-1] for i in range(1, len(multipliers))]
    volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 if returns else 0
    
    return {
        "streaks": streaks,
        "volatility": volatility,
        "trend": "ascending" if streaks["ascending"] > streaks["descending"] else "descending",
    }


def classify_band(multiplier: float) -> str:
    """Classify a multiplier into a band."""
    if multiplier <= 1.0:
        return "crash"
    elif multiplier <= 1.5:
        return "low"
    elif multiplier <= 2.0:
        return "neutral"
    elif multiplier <= 3.0:
        return "mid"
    elif multiplier <= 5.0:
        return "high"
    elif multiplier <= 10.0:
        return "very_high"
    elif multiplier <= 20.0:
        return "moonshot"
    else:
        return "stratospheric"


def analyze_rounds(source: str, limit: int = settings.default_round_limit) -> AnalysisPayload:
    """
    Analyze rounds from a specific source.
    
    Args:
        source: The game source to analyze
        limit: Maximum number of rounds to analyze
        
    Returns:
        AnalysisPayload with complete analysis
    """
    with session_scope() as session:
        # Get rounds
        query = session.query(Round).filter(Round.source == source).order_by(Round.timestamp.desc())
        if limit:
            query = query.limit(limit)
        rounds = query.all()
    
    if not rounds:
        return AnalysisPayload(
            rounds=[],
            count=0,
            source=source,
            timestamps=[],
            multipliers=[],
            stats={},
            patterns={},
        )
    
    # Extract data
    rounds_data = [r.to_dict() for r in rounds]
    timestamps = [r.timestamp for r in rounds]
    multipliers = [r.multiplier for r in rounds]
    
    # Calculate statistics
    stats = calculate_basic_stats(multipliers)
    
    # Calculate patterns
    patterns = calculate_patterns(multipliers, timestamps)
    
    # Classify bands
    bands = [classify_band(m) for m in multipliers]
    band_counts = {}
    for band in bands:
        band_counts[band] = band_counts.get(band, 0) + 1
    patterns["band_distribution"] = band_counts
    
    return AnalysisPayload(
        rounds=rounds_data,
        count=len(rounds),
        source=source,
        timestamps=timestamps,
        multipliers=multipliers,
        stats=stats,
        patterns=patterns,
    )


def get_analysis_payload(source: str, limit: Optional[int] = None) -> AnalysisPayload:
    """
    Get or compute analysis payload for a source.
    
    Uses caching to avoid recomputing.
    """
    # Simple caching - in production, use Redis or similar
    _cache: Dict[str, Tuple[AnalysisPayload, datetime]] = {}
    
    cache_key = f"{source}:{limit}"
    cached = _cache.get(cache_key)
    
    if cached and (datetime.utcnow() - cached[1]).total_seconds() < settings.analysis_cache_ttl:
        return cached[0]
    
    payload = analyze_rounds(source, limit or settings.default_round_limit)
    _cache[cache_key] = (payload, datetime.utcnow())
    
    return payload