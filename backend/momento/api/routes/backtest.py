"""Backtest API routes"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..deps import verify_api_key
from ....backtest import run_backtest, BacktestConfig

router = APIRouter(prefix="/backtest")


@router.post("")
async def run_backtest_endpoint(
    config: BacktestConfig,
    api_key: str = Depends(verify_api_key)
):
    try:
        result = run_backtest(config)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config")
async def run_backtest_with_config(
    name: str = Query(..., description="Backtest name"),
    source: str = Query(..., description="Data source"),
    rounds_limit: int = Query(1000, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    config = BacktestConfig(
        name=name,
        source=source,
        rounds_limit=rounds_limit
    )
    result = run_backtest(config)
    return result.to_dict()


@router.get("/simple")
async def simple_backtest(
    source: str = Query(..., description="Data source"),
    limit: int = Query(1000, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    config = BacktestConfig(
        name="Simple Test",
        source=source,
        rounds_limit=limit
    )
    result = run_backtest(config)
    return result.to_dict()


@router.get("/signals")
async def test_signals(
    source: str = Query(..., description="Data source"),
    limit: int = Query(1000, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    from ....backtest.signals import SignalDetector
    from ....store import get_rounds
    
    rounds = get_rounds(source, limit)
    multipliers = [r.multiplier for r in rounds]
    
    detector = SignalDetector()
    signals = detector.detect_all(multipliers, rounds)
    
    return {
        "source": source,
        "count": len(multipliers),
        "signals": [s.to_dict() for s in signals],
    }


@router.get("/metrics")
async def test_metrics(
    source: str = Query(..., description="Data source"),
    limit: int = Query(1000, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    from ....backtest.metrics import MetricCalculator
    from ....store import get_rounds
    
    rounds = get_rounds(source, limit)
    multipliers = [r.multiplier for r in rounds]
    
    calculator = MetricCalculator()
    metrics = calculator.calculate_all(multipliers, rounds)
    
    return {
        "source": source,
        "count": len(multipliers),
        "metrics": [m.to_dict() for m in metrics],
    }