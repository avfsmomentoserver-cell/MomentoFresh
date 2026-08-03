"""Linguistics API routes"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..deps import verify_api_key
from ....linguistics import analyze_linguistics, get_band_distribution, get_state_distribution

router = APIRouter(prefix="/linguistics")


@router.get("")
async def get_linguistics(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(None, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    analysis = analyze_linguistics(source, limit)
    return analysis.to_dict()


@router.get("/bands")
async def get_bands(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(None, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    distribution = get_band_distribution(source, limit)
    return {"source": source, "bands": distribution}


@router.get("/states")
async def get_states(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(None, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    distribution = get_state_distribution(source, limit)
    return {"source": source, "states": distribution}


@router.get("/pressure")
async def get_pressure_linguistics(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(None, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    analysis = analyze_linguistics(source, limit)
    return {"pressure": analysis.pressure, "vocabulary": analysis.vocabulary.get("pressure", [])}