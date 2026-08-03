"""Data models for Pressure Plugin"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ArchType(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"
    STABLE = "stable"
    EGG = "egg"
    DOME = "dome"
    INVERTED_EGG = "inverted_egg"


class ImminenceLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EXTREME = "extreme"


@dataclass
class CeilingConfig:
    value: float
    arch_type: ArchType = ArchType.ASCENDING
    verification_threshold: int = 3
    strength: float = 0.5


@dataclass
class PressureConfig:
    ceilings: List[float] = field(default_factory=lambda: [1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0])
    decay_rate: float = 0.95
    overflow_threshold: float = 100.0
    min_ceiling_strength: float = 0.3
    verification_threshold: int = 3
    arch_detection_window: int = 20
    gap_energy_multiplier: float = 1.5
    pressure_accumulation_rate: float = 1.0

    # Arch type multipliers
    arch_multipliers: Dict[ArchType, float] = field(default_factory=lambda: {
        ArchType.ASCENDING: 1.2,
        ArchType.DESCENDING: 0.8,
        ArchType.STABLE: 1.0,
        ArchType.EGG: 1.5,
        ArchType.DOME: 1.8,
        ArchType.INVERTED_EGG: 0.7,
    })


@dataclass
class CeilingResult:
    ceiling_value: float
    hits: int = 0
    arch_type: ArchType = ArchType.ASCENDING
    is_verified: bool = False
    pressure_score: float = 0.0
    gap_energy: float = 0.0
    strength: float = 0.0
    last_hit: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ceiling_value": self.ceiling_value,
            "hits": self.hits,
            "arch_type": self.arch_type.value,
            "is_verified": self.is_verified,
            "pressure_score": self.pressure_score,
            "gap_energy": self.gap_energy,
            "strength": self.strength,
            "last_hit": self.last_hit.isoformat() if self.last_hit else None,
        }


@dataclass
class PressureResult:
    source: str
    total_pressure: float = 0.0
    overflow: float = 0.0
    overflow_percent: float = 0.0
    ceiling_results: List[CeilingResult] = field(default_factory=list)
    state: str = "neutral"
    imminence: str = ImminenceLevel.LOW.value
    release_probability: float = 0.0
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "total_pressure": self.total_pressure,
            "overflow": self.overflow,
            "overflow_percent": self.overflow_percent,
            "ceiling_results": [c.to_dict() for c in self.ceiling_results],
            "state": self.state,
            "imminence": self.imminence,
            "release_probability": self.release_probability,
            "predictions": self.predictions,
            "timestamp": self.timestamp.isoformat(),
        }