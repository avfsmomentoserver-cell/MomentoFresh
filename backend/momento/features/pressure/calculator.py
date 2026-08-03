"""Pressure Calculator for MomentoFresh"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    ArchType,
    CeilingConfig,
    CeilingResult,
    ImminenceLevel,
    PressureConfig,
    PressureResult,
)

logger = logging.getLogger(__name__)


class PressureCalculator:
    def __init__(self, config: Optional[PressureConfig] = None):
        self.config = config or PressureConfig()
        self._ceilings: Dict[float, CeilingResult] = {}
        self._initialize_ceilings()

    def _initialize_ceilings(self):
        for ceiling_value in self.config.ceilings:
            self._ceilings[ceiling_value] = CeilingResult(
                ceiling_value=ceiling_value,
                hits=0,
                arch_type=ArchType.ASCENDING,
                is_verified=False,
                pressure_score=0.0,
                gap_energy=0.0,
                strength=0.0,
            )

    def _detect_arch_type(self, multipliers: List[float], ceiling_value: float) -> ArchType:
        if len(multipliers) < self.config.arch_detection_window:
            return ArchType.STABLE
        
        recent = multipliers[:self.config.arch_detection_window]
        below = [m for m in recent if m < ceiling_value]
        above = [m for m in recent if m > ceiling_value]
        near = [m for m in recent if abs(m - ceiling_value) < ceiling_value * 0.1]
        
        if len(above) > len(below) * 1.5:
            return ArchType.ASCENDING
        elif len(below) > len(above) * 1.5:
            return ArchType.DESCENDING
        elif len(near) > len(recent) * 0.7:
            return ArchType.EGG
        elif len(near) > len(recent) * 0.5:
            return ArchType.DOME
        else:
            return ArchType.STABLE

    def _calculate_gap_energy(self, multipliers: List[float], ceiling_value: float) -> Tuple[float, float]:
        below = [m for m in multipliers if m < ceiling_value]
        if not below:
            return 0.0, 0.0
        
        avg_distance = sum(ceiling_value - m for m in below) / len(below)
        normalized_distance = avg_distance / ceiling_value
        
        range_below = max(below) - min(below) if len(below) > 1 else 0
        compression_ratio = 1.0 - (range_below / ceiling_value) if ceiling_value > 0 else 0
        
        gap_energy = normalized_distance * compression_ratio * self.config.gap_energy_multiplier
        
        return gap_energy, normalized_distance

    def _calculate_pressure(
        self,
        hits: int,
        gap_energy: float,
        arch_type: ArchType,
        is_verified: bool,
        strength: float
    ) -> float:
        hit_pressure = hits * 0.1
        arch_multiplier = self.config.arch_multipliers.get(arch_type, 1.0)
        verified_multiplier = 1.5 if is_verified else 1.0
        strength_multiplier = 1.0 + (strength * 0.5)
        
        pressure = (
            hit_pressure
            * gap_energy
            * arch_multiplier
            * verified_multiplier
            * strength_multiplier
            * self.config.pressure_accumulation_rate
        )
        
        return pressure

    def _get_imminence(self, pressure_score: float, overflow: float) -> Tuple[str, float]:
        total = pressure_score + overflow
        
        if total >= 90:
            return ImminenceLevel.EXTREME.value, 1.0
        elif total >= 70:
            return ImminenceLevel.CRITICAL.value, 0.9
        elif total >= 50:
            return ImminenceLevel.HIGH.value, 0.7
        elif total >= 30:
            return ImminenceLevel.MODERATE.value, 0.5
        else:
            return ImminenceLevel.LOW.value, 0.2

    def _get_state(self, pressure_score: float) -> str:
        if pressure_score >= 80:
            return "critical"
        elif pressure_score >= 50:
            return "high"
        elif pressure_score >= 30:
            return "building"
        elif pressure_score >= 10:
            return "normal"
        else:
            return "neutral"

    def calculate(self, multipliers: List[float], source: str) -> PressureResult:
        if not multipliers:
            return PressureResult(source=source)
        
        # Reset ceiling results
        for ceiling_value in self._ceilings:
            self._ceilings[ceiling_value] = CeilingResult(
                ceiling_value=ceiling_value,
                hits=0,
                arch_type=ArchType.ASCENDING,
                is_verified=False,
                pressure_score=0.0,
                gap_energy=0.0,
                strength=0.0,
            )
        
        # Process each multiplier
        ceiling_results = []
        total_pressure = 0.0
        
        for ceiling_value, ceiling in self._ceilings.items():
            # Count hits
            hits = sum(1 for m in multipliers if m >= ceiling_value)
            ceiling.hits = hits
            
            # Detect arch type
            ceiling.arch_type = self._detect_arch_type(multipliers, ceiling_value)
            
            # Calculate gap energy
            gap_energy, normalized_distance = self._calculate_gap_energy(multipliers, ceiling_value)
            ceiling.gap_energy = gap_energy
            
            # Verify ceiling
            ceiling.is_verified = hits >= self.config.verification_threshold
            
            # Calculate strength
            ceiling.strength = min(1.0, hits / 10.0) if hits > 0 else 0.0
            
            # Calculate pressure for this ceiling
            pressure = self._calculate_pressure(
                hits, gap_energy, ceiling.arch_type, ceiling.is_verified, ceiling.strength
            )
            ceiling.pressure_score = pressure
            total_pressure += pressure
            
            ceiling_results.append(ceiling)
        
        # Calculate overflow
        overflow = max(0, total_pressure - self.config.overflow_threshold)
        overflow_percent = min(100, (overflow / self.config.overflow_threshold) * 100) if self.config.overflow_threshold > 0 else 0
        
        # Determine state and imminence
        state = self._get_state(total_pressure)
        imminence, release_probability = self._get_imminence(total_pressure, overflow)
        
        # Generate predictions
        predictions = self._generate_predictions(total_pressure, overflow, ceiling_results)
        
        return PressureResult(
            source=source,
            total_pressure=total_pressure,
            overflow=overflow,
            overflow_percent=overflow_percent,
            ceiling_results=ceiling_results,
            state=state,
            imminence=imminence,
            release_probability=release_probability,
            predictions=predictions,
        )

    def _generate_predictions(
        self,
        total_pressure: float,
        overflow: float,
        ceiling_results: List[CeilingResult]
    ) -> List[Dict[str, Any]]:
        predictions = []
        
        # Release range prediction
        if total_pressure > 50:
            min_release = 1.5
            max_release = 50.0
            
            for ceiling in ceiling_results:
                if ceiling.pressure_score > 10:
                    min_release = max(min_release, ceiling.ceiling_value * 0.5)
                    max_release = min(max_release, ceiling.ceiling_value * 2.0)
            
            predictions.append({
                "type": "release_range",
                "min": min_release,
                "max": max_release,
                "confidence": min(1.0, total_pressure / 100.0)
            })
        
        # Timing prediction
        if total_pressure > 70:
            timing = "imminent" if total_pressure > 90 else "soon"
            predictions.append({
                "type": "release_timing",
                "timing": timing,
                "confidence": min(1.0, (total_pressure - 70) / 30.0)
            })
        
        return predictions


# Convenience function
calculator = PressureCalculator()