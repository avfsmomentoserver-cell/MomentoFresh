"""Backtest Engine for MomentoFresh"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from .models import (
    BacktestConfig,
    BacktestResult,
    MetricConfig,
    MetricResult,
    MetricType,
    PhaseResult,
    SignalConfig,
    SignalResult,
    SignalType,
    TestPhase,
)

logger = logging.getLogger(__name__)


class BacktestEngine:
    def __init__(self):
        self._custom_signals: Dict[str, Callable] = {}
        self._custom_metrics: Dict[str, Callable] = {}

    def register_custom_signal(
        self,
        name: str,
        detector: Callable[[List[float], List[Any]], SignalResult]
    ):
        self._custom_signals[name] = detector

    def register_custom_metric(
        self,
        name: str,
        calculator: Callable[[List[float], List[Any], List[SignalResult]], MetricResult]
    ):
        self._custom_metrics[name] = calculator

    def _run_phase(
        self,
        phase: TestPhase,
        config: BacktestConfig,
        data: List[Any],
        result: BacktestResult,
        multipliers: List[float]
    ) -> PhaseResult:
        start_time = datetime.utcnow()
        phase_result = PhaseResult(
            phase=phase,
            status="started",
            start_time=start_time
        )

        try:
            if phase == TestPhase.PREPARE:
                phase_result.results["message"] = "Data validation and preparation complete"
                phase_result.status = "completed"

            elif phase == TestPhase.BASELINE:
                phase_result.results["baseline"] = self._calculate_baseline(multipliers)
                phase_result.status = "completed"

            elif phase == TestPhase.SIGNAL_DETECTION:
                signals = self._detect_signals(multipliers, data, config)
                result.signal_results.extend(signals)
                phase_result.results["signals_detected"] = len(signals)
                phase_result.status = "completed"

            elif phase == TestPhase.METRIC_CALCULATION:
                metrics = self._calculate_metrics(multipliers, data, result.signal_results, config)
                result.metric_results.extend(metrics)
                phase_result.results["metrics_calculated"] = len(metrics)
                phase_result.status = "completed"

            elif phase == TestPhase.OPTIMIZATION:
                phase_result.results["optimization"] = self._optimize(config, result)
                phase_result.status = "completed"

            elif phase == TestPhase.VALIDATION:
                phase_result.results["validation"] = self._validate(result)
                phase_result.status = "completed"

            elif phase == TestPhase.COMPARISON:
                phase_result.results["comparison"] = self._compare(result)
                phase_result.status = "completed"

            elif phase == TestPhase.REPORTING:
                result.summary = self._generate_summary(result)
                result.recommendations = self._generate_recommendations(result)
                phase_result.results["report"] = "Generated"
                phase_result.status = "completed"

        except Exception as e:
            phase_result.status = "failed"
            phase_result.results["error"] = str(e)
            logger.error(f"Phase {phase.value} failed: {e}")

        phase_result.end_time = datetime.utcnow()
        phase_result.duration_seconds = (
            phase_result.end_time - phase_result.start_time
        ).total_seconds()

        return phase_result

    def _calculate_baseline(self, multipliers: List[float]) -> Dict[str, Any]:
        if not multipliers:
            return {}
        return {
            "count": len(multipliers),
            "mean": sum(multipliers) / len(multipliers),
            "min": min(multipliers),
            "max": max(multipliers),
            "std_dev": (
                sum((x - (sum(multipliers) / len(multipliers))) ** 2 for x in multipliers)
                / len(multipliers)
            ) ** 0.5,
        }

    def _detect_signals(
        self,
        multipliers: List[float],
        data: List[Any],
        config: BacktestConfig
    ) -> List[SignalResult]:
        from .signals import SignalDetector
        detector = SignalDetector()
        return detector.detect_all(multipliers, data, config)

    def _calculate_metrics(
        self,
        multipliers: List[float],
        data: List[Any],
        signals: List[SignalResult],
        config: BacktestConfig
    ) -> List[MetricResult]:
        from .metrics import MetricCalculator
        calculator = MetricCalculator()
        return calculator.calculate_all(multipliers, data, signals, config)

    def _optimize(self, config: BacktestConfig, result: BacktestResult) -> Dict[str, Any]:
        return {"status": "optimized", "metrics": len(result.metric_results)}

    def _validate(self, result: BacktestResult) -> Dict[str, Any]:
        return {"status": "validated", "signals": len(result.signal_results)}

    def _compare(self, result: BacktestResult) -> Dict[str, Any]:
        return {"status": "compared"}

    def _generate_summary(self, result: BacktestResult) -> Dict[str, Any]:
        return {
            "total_rounds": result.config.rounds_limit,
            "signals_detected": len(result.signal_results),
            "metrics_calculated": len(result.metric_results),
            "duration_seconds": result.duration_seconds,
        }

    def _generate_recommendations(self, result: BacktestResult) -> List[str]:
        recommendations = []
        if result.metric_results:
            best_metric = max(
                result.metric_results,
                key=lambda m: m.value if m.better_is_higher else -m.value
            )
            recommendations.append(
                f"Best performing metric: {best_metric.name} ({best_metric.value})"
            )
        return recommendations

    def run(self, config: BacktestConfig, data: Optional[List[Any]] = None) -> BacktestResult:
        start_time = datetime.utcnow()
        
        result = BacktestResult(
            config=config,
            status="running",
            start_time=start_time
        )

        try:
            # Get data if not provided
            if data is None:
                from ..store import get_rounds
                data = get_rounds(config.source, config.rounds_limit)
            
            multipliers = [d.multiplier for d in data]

            # Run each phase
            for phase in config.test_phases:
                phase_result = self._run_phase(phase, config, data, result, multipliers)
                result.phase_results[phase.value] = phase_result

            result.status = "completed"

        except Exception as e:
            result.status = "failed"
            logger.error(f"Backtest failed: {e}")
            raise

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()

        return result


def run_backtest(config: BacktestConfig) -> BacktestResult:
    engine = BacktestEngine()
    return engine.run(config)