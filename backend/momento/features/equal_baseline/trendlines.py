"""
Trendline Calculator for Equal Baseline Charts

Calculates continuous trendlines for equal baseline converted data.
Provides forex-style trendline analysis with equal upside/downside representation.
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Trendline:
    points: List[Tuple[float, float]]
    slope: float
    intercept: float
    start_index: int
    end_index: int
    strength: float
    direction: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "points": self.points,
            "slope": self.slope,
            "intercept": self.intercept,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "strength": self.strength,
            "direction": self.direction,
        }
    
    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept



@dataclass
class TrendlineConfig:
    min_points: int = 3
    max_gap: Optional[float] = None
    min_strength: float = 0.5
    extend_lines: bool = True



class TrendlineCalculator:
    def __init__(self, config: Optional[TrendlineConfig] = None):
        self.config = config or TrendlineConfig()
    
    def calculate(self, points: List[float], x_values: Optional[List[float]] = None) -> List[Trendline]:
        if not points or len(points) < self.config.min_points:
            return []
        
        if x_values is None:
            x_values = list(range(len(points)))
        
        min_len = min(len(points), len(x_values))
        points = points[:min_len]
        x_values = x_values[:min_len]
        
        main_trendline = self._calculate_linear_regression(x_values, points, 0, len(points) - 1)
        
        if main_trendline:
            main_trendline.start_index = 0
            main_trendline.end_index = len(points) - 1
        
        segment_trendlines = self._calculate_segment_trendlines(x_values, points)
        
        trendlines = [main_trendline] if main_trendline else []
        trendlines.extend(segment_trendlines)
        
        trendlines = [tl for tl in trendlines if tl.strength >= self.config.min_strength]
        
        return trendlines
    
    def _calculate_linear_regression(self, x: List[float], y: List[float], start_idx: int, end_idx: int) -> Optional[Trendline]:
        segment_x = x[start_idx:end_idx + 1]
        segment_y = y[start_idx:end_idx + 1]
        
        if len(segment_x) < self.config.min_points:
            return None
        
        n = len(segment_x)
        sum_x = sum(segment_x)
        sum_y = sum(segment_y)
        sum_xy = sum(xi * yi for xi, yi in zip(segment_x, segment_y))
        sum_x2 = sum(xi ** 2 for xi in segment_x)
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return None
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        y_mean = sum_y / n
        ss_total = sum((yi - y_mean) ** 2 for yi in segment_y)
        ss_residual = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(segment_x, segment_y))
        
        r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 1.0
        
        if slope > 0.01:
            direction = "up"
        elif slope < -0.01:
            direction = "down"
        else:
            direction = "flat"
        
        trendline_points = [
            (segment_x[0], slope * segment_x[0] + intercept),
            (segment_x[-1], slope * segment_x[-1] + intercept),
        ]
        
        return Trendline(
            points=trendline_points,
            slope=slope,
            intercept=intercept,
            start_index=start_idx,
            end_index=end_idx,
            strength=abs(r_squared),
            direction=direction,
        )
    
    def _calculate_segment_trendlines(self, x: List[float], y: List[float]) -> List[Trendline]:
        trendlines = []
        n = len(x)
        
        if n < self.config.min_points * 2:
            return trendlines
        
        for segment_size in range(self.config.min_points, n // 2 + 1):
            for start in range(0, n - segment_size):
                end = start + segment_size - 1
                
                trendline = self._calculate_linear_regression(x, y, start, end)
                
                if trendline and trendline.strength >= self.config.min_strength * 1.5:
                    if not any(abs(trendline.slope - existing.slope) < 0.001 and abs(trendline.intercept - existing.intercept) < 0.1 for existing in trendlines):
                        trendlines.append(trendline)
        
        trendlines.sort(key=lambda tl: tl.strength, reverse=True)
        return trendlines[:5]
    
    def calculate_channels(self, points: List[float], x_values: Optional[List[float]] = None, width: float = 0.5) -> List[Dict[str, Any]]:
        if not points or len(points) < self.config.min_points:
            return []
        
        if x_values is None:
            x_values = list(range(len(points)))
        
        main_tl = self._calculate_linear_regression(x_values, points, 0, len(points) - 1)
        
        if not main_tl:
            return []
        
        y_range = max(points) - min(points)
        channel_height = y_range * width
        
        upper_tl = Trendline(
            points=[
                (main_tl.points[0][0], main_tl.points[0][1] + channel_height / 2),
                (main_tl.points[1][0], main_tl.points[1][1] + channel_height / 2),
            ],
            slope=main_tl.slope,
            intercept=main_tl.intercept + channel_height / 2,
            start_index=main_tl.start_index,
            end_index=main_tl.end_index,
            strength=main_tl.strength * 0.8,
            direction=main_tl.direction,
        )
        
        lower_tl = Trendline(
            points=[
                (main_tl.points[0][0], main_tl.points[0][1] - channel_height / 2),
                (main_tl.points[1][0], main_tl.points[1][1] - channel_height / 2),
            ],
            slope=main_tl.slope,
            intercept=main_tl.intercept - channel_height / 2,
            start_index=main_tl.start_index,
            end_index=main_tl.end_index,
            strength=main_tl.strength * 0.8,
            direction=main_tl.direction,
        )
        
        return [{
            "type": "channel",
            "upper": upper_tl.to_dict(),
            "lower": lower_tl.to_dict(),
            "middle": main_tl.to_dict(),
            "width": channel_height,
        }]
    
    def calculate_support_resistance(self, points: List[float], x_values: Optional[List[float]] = None, tolerance: float = 0.05) -> List[Dict[str, Any]]:
        if not points or len(points) < self.config.min_points:
            return []
        
        from collections import defaultdict
        
        rounded = [round(p / tolerance) * tolerance for p in points]
        clusters = defaultdict(int)
        for r in rounded:
            clusters[r] += 1
        
        significant = [(level, count) for level, count in clusters.items() if count >= 2]
        significant.sort(key=lambda x: x[1], reverse=True)
        
        levels = []
        for level, count in significant[:10]:
            below = sum(1 for p in points if p < level)
            above = sum(1 for p in points if p > level)
            level_type = "resistance" if below > above else "support"
            
            levels.append({
                "type": level_type,
                "value": level,
                "count": count,
                "strength": min(count / len(points), 1.0),
            })
        
        return levels
    
    def calculate_fibonacci(self, points: List[float], x_values: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        if not points or len(points) < 2:
            return []
        
        swing_high = max(points)
        swing_low = min(points)
        
        if swing_high == swing_low:
            return []
        
        fib_ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        
        levels = []
        for ratio in fib_ratios:
            uptrend_level = swing_low + ratio * (swing_high - swing_low)
            downtrend_level = swing_high - ratio * (swing_high - swing_low)
            
            levels.append({
                "ratio": ratio,
                "uptrend": uptrend_level,
                "downtrend": downtrend_level,
                "type": "retracement",
            })
        
        extension_ratios = [1.272, 1.618, 2.0, 2.618]
        for ratio in extension_ratios:
            uptrend_ext = swing_low + ratio * (swing_high - swing_low)
            downtrend_ext = swing_high - ratio * (swing_high - swing_low)
            
            levels.append({
                "ratio": ratio,
                "uptrend": uptrend_ext,
                "downtrend": downtrend_ext,
                "type": "extension",
            })
        
        return levels


def calculate_trendlines(points: List[float], x_values: Optional[List[float]] = None) -> List[Dict[str, Any]]:
    calculator = TrendlineCalculator()
    trendlines = calculator.calculate(points, x_values)
    return [tl.to_dict() for tl in trendlines]