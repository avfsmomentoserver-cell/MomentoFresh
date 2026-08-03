"""
Configuration for Aviator Scraper
"""

from pydantic import BaseSettings, Field
from typing import List, Optional


class ScraperSettings(BaseSettings):
    enabled: bool = Field(default=True, env="SCRAPER_ENABLED")
    interval_seconds: int = Field(default=5, env="SCRAPER_INTERVAL")
    max_retries: int = Field(default=3, env="SCRAPER_MAX_RETRIES")
    timeout_seconds: int = Field(default=30, env="SCRAPER_TIMEOUT")
    
    aviator_urls: List[str] = Field(default_factory=lambda: [
        "https://aviator.game",
    ])
    
    api_endpoints: Optional[List[str]] = Field(default=None, env="SCRAPER_API_ENDPOINTS")
    
    store_in_database: bool = Field(default=True, env="SCRAPER_STORE_DB")
    database_path: str = Field(default="backend/data/momento.db", env="SCRAPER_DB_PATH")
    
    broadcast_enabled: bool = Field(default=True, env="SCRAPER_BROADCAST")
    ws_url: Optional[str] = Field(default=None, env="SCRAPER_WS_URL")
    
    use_proxy: bool = Field(default=False, env="SCRAPER_USE_PROXY")
    proxy_url: Optional[str] = Field(default=None, env="SCRAPER_PROXY_URL")
    
    user_agent: str = Field(default="Mozilla/5.0 (Windows NT 10.0; Win64; x64)", env="SCRAPER_USER_AGENT")
    
    requests_per_minute: int = Field(default=60, env="SCRAPER_RPM")
    
    class Config:
        env_file = ".env.scraper"
        env_file_encoding = "utf-8"


settings = ScraperSettings()