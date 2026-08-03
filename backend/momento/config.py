"""
Configuration Management for MomentoFresh

Centralized configuration using environment variables with safe defaults.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, AnyHttpUrl, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_base_path: str = "/api/v1"

    # Database Configuration
    database_path: Path = Path("backend/data/momento.db")
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Security
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Operator Account (created on first run)
    operator_email: str = "operator@momento.local"
    operator_password: str = "momento"

    # Feed Configuration
    feed_autostart: bool = False
    feed_interval_seconds: float = 1.0

    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    cors_allow_all: bool = True
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Ingest Configuration
    inbox_path: Path = Path("backend/data/inbox")
    ingest_batch_size: int = 100
    ingest_workers: int = 4

    # Analysis Configuration
    analysis_cache_ttl: float = 1.0
    max_rounds_per_analysis: int = 1000
    default_round_limit: int = 400

    # Backtest Configuration
    backtest_max_rounds: int = 10000
    backtest_default_limit: int = 1000
    backtest_concurrent_tests: int = 4

    # Pressure Plugin Configuration
    pressure_enabled: bool = True
    pressure_ceilings: List[float] = [1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0]
    pressure_decay_rate: float = 0.95
    pressure_overflow_threshold: float = 100.0

    # Equal Baseline Configuration
    equal_baseline_enabled: bool = True
    equal_baseline_reference: float = 50.0
    equal_baseline_precision: int = 4

    # Forecast Configuration
    forecast_enabled: bool = True
    forecast_window: int = 10
    forecast_confidence_threshold: float = 0.5

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Optional[List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v or []

    @validator("database_path", pre=True)
    def make_absolute_path(cls, v: Path) -> Path:
        if not v.is_absolute():
            return Path.cwd() / v
        return v

    @validator("inbox_path", pre=True)
    def make_inbox_absolute(cls, v: Path) -> Path:
        if not v.is_absolute():
            return Path.cwd() / v
        return v


settings = Settings()


def get_settings() -> Settings:
    return settings