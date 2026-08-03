"""Core API routes"""

from fastapi import APIRouter, Depends

from ..deps import verify_api_key
from ....db import Source, get_session, table_exists

router = APIRouter(prefix="/core")


@router.get("/health")
async def health_check(api_key: str = Depends(verify_api_key)):
    return {
        "status": "healthy",
        "version": "4.0.0",
        "database": table_exists("rounds"),
    }


@router.get("/platform")
async def platform_info(api_key: str = Depends(verify_api_key)):
    return {
        "name": "MomentoFresh",
        "version": "4.0.0",
        "description": "Advanced Analytics & Forecasting Platform for Crash Games",
        "features": [
            "pressure_analysis",
            "equal_baseline",
            "backtest_framework",
            "linguistics",
            "real_time_feed",
        ],
    }


@router.get("/sources")
async def list_sources(api_key: str = Depends(verify_api_key)):
    with get_session() as session:
        sources = session.query(Source).all()
        return [s.to_dict() for s in sources]


@router.post("/sources")
async def create_source(
    name: str,
    display_name: str = "",
    active: bool = True,
    api_key: str = Depends(verify_api_key)
):
    with get_session() as session:
        source = Source(
            name=name,
            display_name=display_name or name,
            active=active
        )
        session.add(source)
        session.commit()
        return source.to_dict()