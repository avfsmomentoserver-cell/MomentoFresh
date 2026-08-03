"""Pressure API routes"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..deps import verify_api_key
from ....features.pressure.calculator import PressureCalculator
from ....store import get_rounds

router = APIRouter(prefix="/pressure")


@router.get("")
async def get_pressure(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(100, description="Maximum rounds to analyze"),
    api_key: str = Depends(verify_api_key)
):
    calculator = PressureCalculator()
    rounds = get_rounds(source, limit or 100)
    
    multipliers = [r.multiplier for r in rounds]
    result = calculator.calculate(multipliers, source)
    
    return result.to_dict()


@router.get("/state")
async def get_pressure_state(
    source: str = Query(..., description="Game source"),
    api_key: str = Depends(verify_api_key)
):
    calculator = PressureCalculator()
    rounds = get_rounds(source, 100)
    
    multipliers = [r.multiplier for r in rounds]
    result = calculator.calculate(multipliers, source)
    
    return {
        "source": source,
        "state": result.state,
        "pressure_score": result.total_pressure,
        "ceilings": result.ceiling_results,
    }


@router.get("/predictions")
async def get_pressure_predictions(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(100, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    calculator = PressureCalculator()
    rounds = get_rounds(source, limit or 100)
    
    multipliers = [r.multiplier for r in rounds]
    result = calculator.calculate(multipliers, source)
    
    return {
        "source": source,
        "predictions": result.predictions,
        "imminence": result.imminence,
        "release_probability": result.release_probability,
    }