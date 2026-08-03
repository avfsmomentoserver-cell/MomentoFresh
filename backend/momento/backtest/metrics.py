"""Metric Calculation for Backtest Framework"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .models import MetricResult, MetricType, MetricConfig, SignalResult, BacktestConfig

logger = logging.getLogger(__name__)


@dataclass
class MetricCalculator:
    def __init__(self):
        self._calculators: Dict[MetricType, Callable] = {}
        self._register_builtins()

    def _register_builtins(self):
        self._calculators[MetricType.ACCURACY] = self._calculate_accuracy
        self._calculators[MetricType.PRECISION] = self._calculate_precision
        self._calculators[MetricType.RECALL] = self._calculate_recall
        self._calculators[MetricType.F1_SCORE] = self._calculate_f1_score
        self._calculators[MetricType.SHARPE_RATIO] = self._calculate_sharpe_ratio
        self._calculators[MetricType.PROFIT_FACTOR] = self._calculate_profit_factor
        self._calculators[MetricType.MAX_DRAWDOWN] = self._calculate_max_drawdown
        self._calculators[MetricType.WIN_RATE] = self._calculate_win_rate
        self._calculators[MetricType.RISK_REWARD] = self._calculate_risk_reward
        self._calculators[MetricType.EXPECTED_VALUE] = self._calculate_expected_value
        self._calculators[MetricType.BRIER_SCORE] = self._calculate_brier_score

    def register(self, metric_type: MetricType, calculator: Callable):
        self._calculators[metric_type] = calculator

    def calculate(self, metric_type: MetricType, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        calculator = self._calculators.get(metric_type)
        if calculator is None:
            return MetricResult(
                metric_type=metric_type,
                name=metric_type.value,
                value=0.0,
                unit="",
                better_is_higher=True
            )
        return calculator(multipliers, data, signals, config)

    def calculate_all(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> List[MetricResult]:
        results = []
        for metric_type in self._calculators:
            result = self.calculate(metric_type, multipliers, data, signals, config)
            results.append(result)
        return results

    def _calculate_accuracy(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Placeholder - accuracy requires actual vs predicted
        return MetricResult(
            metric_type=MetricType.ACCURACY,
            name="Accuracy",
            value=0.0,
            unit="%",
            better_is_higher=True
        )

    def _calculate_precision(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Precision = TP / (TP + FP)
        # Placeholder without actual predictions
        return MetricResult(
            metric_type=MetricType.PRECISION,
            name="Precision",
            value=0.0,
            unit="%",
            better_is_higher=True
        )

    def _calculate_recall(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Recall = TP / (TP + FN)
        return MetricResult(
            metric_type=MetricType.RECALL,
            name="Recall",
            value=0.0,
            unit="%",
            better_is_higher=True
        )

    def _calculate_f1_score(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # F1 = 2 * (precision * recall) / (precision + recall)
        return MetricResult(
            metric_type=MetricType.F1_SCORE,
            name="F1 Score",
            value=0.0,
            unit="",
            better_is_higher=True
        )

    def _calculate_sharpe_ratio(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Sharpe ratio = (mean return - risk-free rate) / std dev
        if not multipliers:
            return MetricResult(
                metric_type=MetricType.SHARPE_RATIO,
                name="Sharpe Ratio",
                value=0.0,
                unit="",
                better_is_higher=True
            )
        
        mean = sum(multipliers) / len(multipliers)
        variance = sum((m - mean) ** 2 for m in multipliers) / len(multipliers)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return MetricResult(
                metric_type=MetricType.SHARPE_RATIO,
                name="Sharpe Ratio",
                value=0.0,
                unit="",
                better_is_higher=True
            )
        
        return MetricResult(
            metric_type=MetricType.SHARPE_RATIO,
            name="Sharpe Ratio",
            value=mean / std_dev,
            unit="",
            better_is_higher=True
        )

    def _calculate_profit_factor(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Profit factor = gross profit / gross loss
        if not multipliers:
            return MetricResult(
                metric_type=MetricType.PROFIT_FACTOR,
                name="Profit Factor",
                value=1.0,
                unit="",
                better_is_higher=True
            )
        
        wins = [m for m in multipliers if m > 1.5]
        losses = [m for m in multipliers if m <= 1.5]
        
        if not losses:
            return MetricResult(
                metric_type=MetricType.PROFIT_FACTOR,
                name="Profit Factor",
                value=float('inf'),
                unit="",
                better_is_higher=True
            )
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            return MetricResult(
                metric_type=MetricType.PROFIT_FACTOR,
                name="Profit Factor",
                value=float('inf'),
                unit="",
                better_is_higher=True
            )
        
        return MetricResult(
            metric_type=MetricType.PROFIT_FACTOR,
            name="Profit Factor",
            value=avg_win / avg_loss,
            unit="",
            better_is_higher=True
        )

    def _calculate_max_drawdown(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Max drawdown from peak
        if not multipliers:
            return MetricResult(
                metric_type=MetricType.MAX_DRAWDOWN,
                name="Max Drawdown",
                value=0.0,
                unit="%",
                better_is_higher=False
            )
        
        max_drawdown = 0.0
        peak = multipliers[0]
        
        for m in multipliers[1:]:
            if m > peak:
                peak = m
            drawdown = (peak - m) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        return MetricResult(
            metric_type=MetricType.MAX_DRAWDOWN,
            name="Max Drawdown",
            value=max_drawdown,
            unit="%",
            better_is_higher=False
        )

    def _calculate_win_rate(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        if not multipliers:
            return MetricResult(
                metric_type=MetricType.WIN_RATE,
                name="Win Rate",
                value=0.0,
                unit="%",
                better_is_higher=True
            )
        
        wins = sum(1 for m in multipliers if m > 1.5)
        win_rate = wins / len(multipliers) * 100
        
        return MetricResult(
            metric_type=MetricType.WIN_RATE,
            name="Win Rate",
            value=win_rate,
            unit="%",
            better_is_higher=True
        )

    def _calculate_risk_reward(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Risk/Reward ratio
        if not multipliers:
            return MetricResult(
                metric_type=MetricType.RISK_REWARD,
                name="Risk/Reward",
                value=1.0,
                unit="",
                better_is_higher=True
            )
        
        wins = [m for m in multipliers if m > 1.5]
        losses = [m for m in multipliers if m <= 1.5]
        
        if not losses:
            return MetricResult(
                metric_type=MetricType.RISK_REWARD,
                name="Risk/Reward",
                value=float('inf'),
                unit="",
                better_is_higher=True
            )
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            return MetricResult(
                metric_type=MetricType.RISK_REWARD,
                name="Risk/Reward",
                value=float('inf'),
                unit="",
                better_is_higher=True
            )
        
        return MetricResult(
            metric_type=MetricType.RISK_REWARD,
            name="Risk/Reward",
            value=avg_win / avg_loss,
            unit="",
            better_is_higher=True
        )

    def _calculate_expected_value(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Expected value per trade
        if not multipliers:
            return MetricResult(
                metric_type=MetricType.EXPECTED_VALUE,
                name="Expected Value",
                value=0.0,
                unit="x",
                better_is_higher=True
            )
        
        wins = [m for m in multipliers if m > 1.5]
        losses = [m for m in multipliers if m <= 1.5]
        
        win_prob = len(wins) / len(multipliers) if multipliers else 0
        loss_prob = len(losses) / len(multipliers) if multipliers else 0
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        ev = win_prob * avg_win + loss_prob * avg_loss
        
        return MetricResult(
            metric_type=MetricType.EXPECTED_VALUE,
            name="Expected Value",
            value=ev,
            unit="x",
            better_is_higher=True
        )

    def _calculate_brier_score(self, multipliers: List[float], data: List[Any], signals: List[SignalResult], config: Optional[BacktestConfig] = None) -> MetricResult:
        # Brier score for probability predictions
        # Requires predicted probabilities and actual outcomes
        return MetricResult(
            metric_type=MetricType.BRIER_SCORE,
            name="Brier Score",
            value=0.0,
            unit="",
            better_is_higher=False
        )