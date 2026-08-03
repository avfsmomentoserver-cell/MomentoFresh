"""
Forecast Engine for MomentoFresh

Generates predictions based on historical patterns and current state.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import settings
from .analysis import AnalysisPayload, get_analysis_payload_cached
from .db import Round, get_session, session_scope
from .store import get_latest_round

logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Result of a forecast prediction."""
    source: str
    round_id: Optional[int]
    predicted_min: float
    predicted_max: float
    predicted_multiplier: float
    confidence: float
    explanation: str
    state: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    scored_at: Optional[datetime] = None
    accuracy: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "round_id": self.round_id,
            "predicted_min": self.predicted_min,
            "predicted_max": self.predicted_max,
            "predicted_multiplier": self.predicted_multiplier,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "scored_at": self.scored_at.isoformat() if self.scored_at else None,
            "accuracy": self.accuracy,
        }


def generate_forecast(source: str, limit: int = settings.default_round_limit) -> ForecastResult:
    """
    Generate a forecast for the next round.
    
    Uses historical patterns to predict the next multiplier range.
    
    Args:
        source: The game source
        limit: Number of historical rounds to use
        
    Returns:
        ForecastResult with prediction
    """
    # Get analysis payload
    payload = get_analysis_payload_cached(source, limit)
    
    if not payload.rounds or len(payload.multipliers) < 10:
        return ForecastResult(
            source=source,
            round_id=None,
            predicted_min=1.0,
            predicted_max=2.0,
            predicted_multiplier=1.5,
            confidence=0.0,
            explanation="Insufficient data for forecast",
            state="insufficient_data",
        )
    
    multipliers = payload.multipliers
    stats = payload.stats
    patterns = payload.patterns
    
    # Simple forecasting based on recent trends
    # Use last N multipliers to predict next
    recent = multipliers[:20]  # Last 20 rounds
    
    # Calculate average of recent
    avg_recent = sum(recent) / len(recent)
    
    # Calculate trend direction
    if len(recent) >= 2:
        trend = (recent[0] - recent[-1]) / len(recent)
    else:
        trend = 0
    
    # Predict based on average and trend
    predicted_multiplier = max(1.0, avg_recent + trend)
    
    # Calculate confidence based on volatility
    if stats.get("std_dev", 0) > 0:
        volatility = stats["std_dev"] / stats["mean"] if stats["mean"] > 0 else 0
        confidence = max(0.0, min(1.0, 1.0 - volatility))
    else:
        confidence = 0.5
    
    # Adjust confidence based on pattern strength
    if patterns.get("streaks"):
        streak_len = max(
            patterns["streaks"].get("max_ascending", 0),
            patterns["streaks"].get("max_descending", 0)
        )
        confidence *= min(1.0, streak_len / 10.0) * 0.5 + 0.5
    
    # Calculate range
    range_size = stats.get("std_dev", 0.5) * 2
    predicted_min = max(1.0, predicted_multiplier - range_size)
    predicted_max = predicted_multiplier + range_size
    
    # Generate explanation
    explanation_parts = []
    if trend > 0.1:
        explanation_parts.append(f"Upward trend detected (last 20 avg: {avg_recent:.2f}x)")
    elif trend < -0.1:
        explanation_parts.append(f"Downward trend detected (last 20 avg: {avg_recent:.2f}x)")
    else:
        explanation_parts.append(f"Stable pattern (last 20 avg: {avg_recent:.2f}x)")
    
    explanation_parts.append(f"Volatility: {stats.get('std_dev', 0):.2f}x")
    explanation = "; ".join(explanation_parts)
    
    return ForecastResult(
        source=source,
        round_id=None,
        predicted_min=round(predicted_min, 2),
        predicted_max=round(predicted_max, 2),
        predicted_multiplier=round(predicted_multiplier, 2),
        confidence=round(confidence, 2),
        explanation=explanation,
        state="generated",
    )


def score_forecast(forecast: ForecastResult, actual_multiplier: float) -> ForecastResult:
    """
    Score a forecast against the actual result.
    
    Args:
        forecast: The forecast to score
        actual_multiplier: The actual multiplier that occurred
        
    Returns:
        Updated ForecastResult with accuracy
    """
    if actual_multiplier < forecast.predicted_min:
        accuracy = 0.0
    elif actual_multiplier > forecast.predicted_max:
        accuracy = 0.0
    else:
        # Linear accuracy within range
        range_size = forecast.predicted_max - forecast.predicted_min
        if range_size == 0:
            accuracy = 1.0 if actual_multiplier == forecast.predicted_min else 0.0
        else:
            distance = abs(actual_multiplier - forecast.predicted_multiplier)
            accuracy = max(0.0, 1.0 - (distance / (range_size / 2)))
    
    forecast.accuracy = round(accuracy, 2)
    forecast.state = "scored"
    forecast.scored_at = datetime.utcnow()
    
    return forecast


def get_forecast(source: str) -> Optional[ForecastResult]:
    """Get the latest forecast for a source."""
    with session_scope() as session:
        from .db import Forecast
        forecast = session.query(Forecast).filter(
            Forecast.source == source
        ).order_by(Forecast.created_at.desc()).first()
        return forecast


def create_forecast(source: str) -> ForecastResult:
    """
    Create and save a new forecast.
    
    Args:
        source: The game source
        
    Returns:
        The created forecast
    """
    forecast = generate_forecast(source)
    
    # Save to database
    with session_scope() as session:
        from .db import Forecast
        db_forecast = Forecast(
            source=forecast.source,
            round_id=forecast.round_id,
            multiplier=forecast.predicted_multiplier,
            predicted_min=forecast.predicted_min,
            predicted_max=forecast.predicted_max,
            confidence=forecast.confidence,
            state=forecast.state,
            explanation=forecast.explanation,
        )
        session.add(db_forecast)
    
    return forecast