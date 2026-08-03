"""Signal Detection for Backtest Framework"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .models import SignalResult, SignalType, SignalConfig, BacktestConfig

logger = logging.getLogger(__name__)


@dataclass
class SignalDetector:
    def __init__(self):
        self._detectors: Dict[SignalType, Callable] = {}
        self._register_builtins()

    def _register_builtins(self):
        self._detectors[SignalType.PRESSURE] = self._detect_pressure
        self._detectors[SignalType.MOONSHOT] = self._detect_moonshot
        self._detectors[SignalType.COLLAPSE] = self._detect_collapse
        self._detectors[SignalType.RESISTANCE_BREAK] = self._detect_resistance_break
        self._detectors[SignalType.SUPPORT_BOUNCE] = self._detect_support_bounce
        self._detectors[SignalType.TREND_REVERSAL] = self._detect_trend_reversal
        self._detectors[SignalType.GAP_SWING] = self._detect_gap_swing
        self._detectors[SignalType.LADDER] = self._detect_ladder
        self._detectors[SignalType.COMPRESSION] = self._detect_compression
        self._detectors[SignalType.EXPANSION] = self._detect_expansion

    def register(self, signal_type: SignalType, detector: Callable):
        self._detectors[signal_type] = detector

    def detect(self, signal_type: SignalType, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        detector = self._detectors.get(signal_type)
        if detector is None:
            return SignalResult(
                signal_type=signal_type,
                name=signal_type.value,
                detected=False,
                confidence=0.0
            )
        return detector(multipliers, data, config)

    def detect_all(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> List[SignalResult]:
        results = []
        for signal_type in self._detectors:
            result = self.detect(signal_type, multipliers, data, config)
            if result.detected:
                results.append(result)
        return results

    def _detect_pressure(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        from ...features.pressure.calculator import PressureCalculator
        calculator = PressureCalculator()
        result = calculator.calculate(multipliers, "test")
        return SignalResult(
            signal_type=SignalType.PRESSURE,
            name="Pressure",
            detected=result.total_pressure > 50,
            confidence=min(1.0, result.total_pressure / 100.0),
            strength=result.total_pressure,
            metadata={"pressure_score": result.total_pressure, "ceilings": len(result.ceiling_results)}
        )

    def _detect_moonshot(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if not multipliers:
            return SignalResult(signal_type=SignalType.MOONSHOT, name="Moonshot", detected=False, confidence=0.0)
        
        recent = multipliers[:5]
        high_count = sum(1 for m in recent if m > 5.0)
        
        return SignalResult(
            signal_type=SignalType.MOONSHOT,
            name="Moonshot",
            detected=high_count >= 2,
            confidence=min(1.0, high_count / 5.0 * 2.0),
            strength=high_count,
            metadata={"high_multipliers": high_count}
        )

    def _detect_collapse(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if not multipliers:
            return SignalResult(signal_type=SignalType.COLLAPSE, name="Collapse", detected=False, confidence=0.0)
        
        recent = multipliers[:5]
        low_count = sum(1 for m in recent if m < 1.5)
        
        return SignalResult(
            signal_type=SignalType.COLLAPSE,
            name="Collapse",
            detected=low_count >= 3,
            confidence=min(1.0, low_count / 5.0 * 2.0),
            strength=low_count,
            metadata={"low_multipliers": low_count}
        )

    def _detect_resistance_break(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if len(multipliers) < 3:
            return SignalResult(signal_type=SignalType.RESISTANCE_BREAK, name="Resistance Break", detected=False, confidence=0.0)
        
        # Check if recent multipliers broke above a resistance level
        resistance_levels = [2.0, 3.0, 5.0, 10.0]
        for level in resistance_levels:
            below = [m for m in multipliers[:10] if m < level]
            above = [m for m in multipliers[:5] if m >= level]
            if below and above:
                return SignalResult(
                    signal_type=SignalType.RESISTANCE_BREAK,
                    name="Resistance Break",
                    detected=True,
                    confidence=0.8,
                    strength=level,
                    metadata={"level": level, "count_below": len(below), "count_above": len(above)}
                )
        return SignalResult(signal_type=SignalType.RESISTANCE_BREAK, name="Resistance Break", detected=False, confidence=0.0)

    def _detect_support_bounce(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if len(multipliers) < 3:
            return SignalResult(signal_type=SignalType.SUPPORT_BOUNCE, name="Support Bounce", detected=False, confidence=0.0)
        
        # Check for bounce from low levels
        low_levels = [1.0, 1.2, 1.5]
        for level in low_levels:
            near = [m for m in multipliers[:10] if abs(m - level) < 0.2]
            above = [m for m in multipliers[:5] if m > level + 0.2]
            if near and above:
                return SignalResult(
                    signal_type=SignalType.SUPPORT_BOUNCE,
                    name="Support Bounce",
                    detected=True,
                    confidence=0.75,
                    strength=level,
                    metadata={"level": level, "count_near": len(near), "count_above": len(above)}
                )
        return SignalResult(signal_type=SignalType.SUPPORT_BOUNCE, name="Support Bounce", detected=False, confidence=0.0)

    def _detect_trend_reversal(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if len(multipliers) < 5:
            return SignalResult(signal_type=SignalType.TREND_REVERSAL, name="Trend Reversal", detected=False, confidence=0.0)
        
        # Check for trend reversal
        first_half = multipliers[:5]
        second_half = multipliers[5:10]
        
        if not first_half or not second_half:
            return SignalResult(signal_type=SignalType.TREND_REVERSAL, name="Trend Reversal", detected=False, confidence=0.0)
        
        first_trend = (first_half[-1] - first_half[0]) / len(first_half)
        second_trend = (second_half[-1] - second_half[0]) / len(second_half)
        
        if first_trend * second_trend < 0 and abs(first_trend) > 0.1 and abs(second_trend) > 0.1:
            return SignalResult(
                signal_type=SignalType.TREND_REVERSAL,
                name="Trend Reversal",
                detected=True,
                confidence=0.85,
                strength=abs(first_trend - second_trend),
                metadata={"first_trend": first_trend, "second_trend": second_trend}
            )
        return SignalResult(signal_type=SignalType.TREND_REVERSAL, name="Trend Reversal", detected=False, confidence=0.0)

    def _detect_gap_swing(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if len(multipliers) < 2:
            return SignalResult(signal_type=SignalType.GAP_SWING, name="Gap Swing", detected=False, confidence=0.0)
        
        # Check for large gaps between consecutive multipliers
        gaps = [abs(multipliers[i] - multipliers[i+1]) for i in range(len(multipliers)-1)]
        large_gaps = [g for g in gaps if g > 2.0]
        
        if large_gaps:
            return SignalResult(
                signal_type=SignalType.GAP_SWING,
                name="Gap Swing",
                detected=True,
                confidence=min(1.0, len(large_gaps) / 5.0),
                strength=max(large_gaps),
                metadata={"gap_count": len(large_gaps), "max_gap": max(large_gaps)}
            )
        return SignalResult(signal_type=SignalType.GAP_SWING, name="Gap Swing", detected=False, confidence=0.0)

    def _detect_ladder(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if len(multipliers) < 5:
            return SignalResult(signal_type=SignalType.LADDER, name="Ladder", detected=False, confidence=0.0)
        
        # Check for ascending or descending ladder
        ascending = all(multipliers[i] < multipliers[i+1] for i in range(len(multipliers)-1))
        descending = all(multipliers[i] > multipliers[i+1] for i in range(len(multipliers)-1))
        
        if ascending or descending:
            return SignalResult(
                signal_type=SignalType.LADDER,
                name="Ladder",
                detected=True,
                confidence=0.9,
                strength=len(multipliers),
                metadata={"direction": "ascending" if ascending else "descending"}
            )
        return SignalResult(signal_type=SignalType.LADDER, name="Ladder", detected=False, confidence=0.0)

    def _detect_compression(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if len(multipliers) < 5:
            return SignalResult(signal_type=SignalType.COMPRESSION, name="Compression", detected=False, confidence=0.0)
        
        # Check for low volatility (compression)
        mean = sum(multipliers) / len(multipliers)
        variance = sum((m - mean) ** 2 for m in multipliers) / len(multipliers)
        std_dev = variance ** 0.5
        
        if std_dev < 0.5:
            return SignalResult(
                signal_type=SignalType.COMPRESSION,
                name="Compression",
                detected=True,
                confidence=min(1.0, 1.0 - std_dev),
                strength=1.0 - std_dev,
                metadata={"std_dev": std_dev, "mean": mean}
            )
        return SignalResult(signal_type=SignalType.COMPRESSION, name="Compression", detected=False, confidence=0.0)

    def _detect_expansion(self, multipliers: List[float], data: List[Any], config: Optional[BacktestConfig] = None) -> SignalResult:
        if len(multipliers) < 5:
            return SignalResult(signal_type=SignalType.EXPANSION, name="Expansion", detected=False, confidence=0.0)
        
        # Check for high volatility (expansion)
        mean = sum(multipliers) / len(multipliers)
        variance = sum((m - mean) ** 2 for m in multipliers) / len(multipliers)
        std_dev = variance ** 0.5
        
        if std_dev > 2.0:
            return SignalResult(
                signal_type=SignalType.EXPANSION,
                name="Expansion",
                detected=True,
                confidence=min(1.0, std_dev / 5.0),
                strength=std_dev,
                metadata={"std_dev": std_dev, "mean": mean}
            )
        return SignalResult(signal_type=SignalType.EXPANSION, name="Expansion", detected=False, confidence=0.0)