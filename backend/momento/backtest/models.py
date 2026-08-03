"""Data models for the backtest framework"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TestPhase(Enum):
    PREPARE = "prepare"
    BASELINE = "baseline"
    SIGNAL_DETECTION = "signal_detection"
    METRIC_CALCULATION = "metric_calculation"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"
    COMPARISON = "comparison"
    REPORTING = "reporting"


class SignalType(Enum):
    PRESSURE = "pressure"
    MOONSHOT = "moonshot"
    COLLAPSE = "collapse"
    RESISTANCE_BREAK = "resistance_break"
    SUPPORT_BOUNCE = "support_bounce"
    TREND_REVERSAL = "trend_reversal"
    GAP_SWING = "gap_swing"
    LADDER = "ladder"
    COMPRESSION = "compression"
    EXPANSION = "expansion"
    CUSTOM = "custom"


class MetricType(Enum):
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    SHARPE_RATIO = "sharpe_ratio"
    PROFIT_FACTOR = "profit_factor"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    RISK_REWARD = "risk_reward"
    EXPECTED_VALUE = "expected_value"
    BRIER_SCORE = "brier_score"
    CUSTOM = "custom"


@dataclass
class SignalConfig:
    signal_type: SignalType
    name: str
    enabled: bool = True
    threshold: float = 0.5
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricConfig:
    metric_type: MetricType
    name: str
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BacktestConfig:
    name: str
    source: str
    rounds_limit: int = 1000
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    test_phases: List[TestPhase] = field(default_factory=lambda: list(TestPhase))
    signal_configs: List[SignalConfig] = field(default_factory=list)
    metric_configs: List[MetricConfig] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    random_seed: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "rounds_limit": self.rounds_limit,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "test_phases": [p.value for p in self.test_phases],
            "signal_configs": [s.to_dict() for s in self.signal_configs],
            "metric_configs": [m.to_dict() for m in self.metric_configs],
            "parameters": self.parameters,
            "random_seed": self.random_seed,
        }


@dataclass
class SignalResult:
    signal_type: SignalType
    name: str
    detected: bool
    confidence: float
    strength: float = 0.0
    position: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type.value,
            "name": self.name,
            "detected": self.detected,
            "confidence": self.confidence,
            "strength": self.strength,
            "position": self.position,
            "metadata": self.metadata,
        }


@dataclass
class MetricResult:
    metric_type: MetricType
    name: str
    value: float
    unit: str = ""
    better_is_higher: bool = True
    baseline: float = 0.0
    improvement: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_type": self.metric_type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "better_is_higher": self.better_is_higher,
            "baseline": self.baseline,
            "improvement": self.improvement,
        }


@dataclass
class PhaseResult:
    phase: TestPhase
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    results: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "results": self.results,
        }


@dataclass
class BacktestResult:
    config: BacktestConfig
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    phase_results: Dict[str, PhaseResult] = field(default_factory=dict)
    signal_results: List[SignalResult] = field(default_factory=list)
    metric_results: List[MetricResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "phase_results": {k: v.to_dict() for k, v in self.phase_results.items()},
            "signal_results": [s.to_dict() for s in self.signal_results],
            "metric_results": [m.to_dict() for m in self.metric_results],
            "summary": self.summary,
            "recommendations": self.recommendations,
        }