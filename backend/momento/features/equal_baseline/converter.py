"""
Equal Baseline Converter for MomentoFresh

Converts multipliers to a symmetric scale where:
- 1.00x maps to -reference (default -50)
- reference x maps to +reference (default +50)
- Values in between are linearly interpolated

This creates equal trendlines upside and downside for professional forex-style analysis.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


@dataclass
class ConversionConfig:
    reference: float = 50.0
    precision: int = 4
    clamp_min: Optional[float] = 0.0
    clamp_max: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversionConfig":
        return cls(
            reference=data.get("reference", 50.0),
            precision=data.get("precision", 4),
            clamp_min=data.get("clamp_min"),
            clamp_max=data.get("clamp_max"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference": self.reference,
            "precision": self.precision,
            "clamp_min": self.clamp_min,
            "clamp_max": self.clamp_max,
        }


@dataclass
class ConvertedValue:
    original: float
    points: float
    normalized: float
    band: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original": self.original,
            "points": self.points,
            "normalized": self.normalized,
            "band": self.band,
        }


class EqualBaselineConverter:
    def __init__(self, config: Optional[ConversionConfig] = None):
        self.config = config or ConversionConfig()
    
    def convert(self, multiplier: float) -> ConvertedValue:
        if self.config.clamp_min is not None:
            multiplier = max(multiplier, self.config.clamp_min)
        if self.config.clamp_max is not None:
            multiplier = min(multiplier, self.config.clamp_max)
        
        points = self._multiplier_to_points(multiplier)
        normalized = points / self.config.reference
        band = self._get_band(multiplier)
        
        return ConvertedValue(
            original=round(multiplier, self.config.precision),
            points=round(points, self.config.precision),
            normalized=round(normalized, self.config.precision),
            band=band,
        )
    
    def _multiplier_to_points(self, multiplier: float) -> float:
        ref = self.config.reference
        
        if multiplier <= 1.0:
            return -ref * (2 - multiplier)
        else:
            return (multiplier - 1) * (2 * ref) - ref
    
    def _points_to_multiplier(self, points: float) -> float:
        ref = self.config.reference
        
        if points <= -ref:
            return 2 + points / ref
        else:
            return 1 + (points + ref) / (2 * ref)
    
    def _get_band(self, multiplier: float) -> str:
        ref = self.config.reference
        points = self._multiplier_to_points(multiplier)
        
        if points <= -ref * 2:
            return "ultra-crash"
        elif points <= -ref * 1.5:
            return "crash"
        elif points <= -ref * 1.0:
            return "deep-low"
        elif points <= -ref * 0.5:
            return "low"
        elif points <= 0:
            return "neutral"
        elif points <= ref * 0.5:
            return "mid"
        elif points <= ref * 1.0:
            return "high"
        elif points <= ref * 1.5:
            return "ignition"
        elif points <= ref * 2.0:
            return "moonshot"
        else:
            return "stratospheric"
    
    def convert_list(self, multipliers: List[float]) -> List[ConvertedValue]:
        return [self.convert(m) for m in multipliers]
    
    def convert_to_points(self, multipliers: List[float]) -> List[float]:
        return [self._multiplier_to_points(m) for m in multipliers]
    
    def convert_to_normalized(self, multipliers: List[float]) -> List[float]:
        return [self._multiplier_to_points(m) / self.config.reference for m in multipliers]
    
    def inverse(self, points: List[float]) -> List[float]:
        return [self._points_to_multiplier(p) for p in points]


def convert_multipliers(multipliers: List[float], reference: float = 50.0) -> List[float]:
    converter = EqualBaselineConverter(ConversionConfig(reference=reference))
    return converter.convert_to_points(multipliers)


def convert_to_points(multiplier: float, reference: float = 50.0) -> float:
    converter = EqualBaselineConverter(ConversionConfig(reference=reference))
    return converter._multiplier_to_points(multiplier)