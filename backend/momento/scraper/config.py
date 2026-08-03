"""
Configuration for Aviator Scraper

Supports:
- Environment variables
- .env file (default: .env.scraper)
- Multiple Aviator URLs with different configurations
- Authentication (cookie-based, token-based, API key)
"""

from pydantic import BaseSettings, Field
from typing import Any, Dict, List, Optional


class AuthConfig(BaseSettings):
    """Authentication configuration for a single site."""
    url: str = Field(default="", env="SCRAPER_URL")
    username: Optional[str] = Field(default=None, env="SCRAPER_USERNAME")
    password: Optional[str] = Field(default=None, env="SCRAPER_PASSWORD")
    api_key: Optional[str] = Field(default=None, env="SCRAPER_API_KEY")
    auth_token: Optional[str] = Field(default=None, env="SCRAPER_AUTH_TOKEN")
    auth_type: str = Field(default="cookie", env="SCRAPER_AUTH_TYPE")  # cookie, token, api_key, none
    login_url: Optional[str] = Field(default=None, env="SCRAPER_LOGIN_URL")
    login_method: str = Field(default="POST", env="SCRAPER_LOGIN_METHOD")  # POST, GET
    login_payload: Optional[Dict[str, Any]] = Field(default=None, env="SCRAPER_LOGIN_PAYLOAD")
    token_header: str = Field(default="Authorization", env="SCRAPER_TOKEN_HEADER")
    token_prefix: str = Field(default="Bearer", env="SCRAPER_TOKEN_PREFIX")
    session_timeout: int = Field(default=3600, env="SCRAPER_SESSION_TIMEOUT")  # seconds


class ScraperSettings(BaseSettings):
    """Main scraper configuration."""
    
    # General settings
    enabled: bool = Field(default=True, env="SCRAPER_ENABLED")
    interval_seconds: int = Field(default=5, env="SCRAPER_INTERVAL")
    max_retries: int = Field(default=3, env="SCRAPER_MAX_RETRIES")
    timeout_seconds: int = Field(default=30, env="SCRAPER_TIMEOUT")
    
    # Target URLs
    aviator_urls: List[str] = Field(default_factory=lambda: [
        "https://aviator.game",
    ])
    
    # API endpoints (optional, for sites with public APIs)
    api_endpoints: Optional[List[str]] = Field(default=None, env="SCRAPER_API_ENDPOINTS")
    
    # Database settings
    store_in_database: bool = Field(default=True, env="SCRAPER_STORE_DB")
    database_path: str = Field(default="backend/data/momento.db", env="SCRAPER_DB_PATH")
    
    # WebSocket broadcasting
    broadcast_enabled: bool = Field(default=True, env="SCRAPER_BROADCAST")
    ws_url: Optional[str] = Field(default=None, env="SCRAPER_WS_URL")
    
    # Proxy settings
    use_proxy: bool = Field(default=False, env="SCRAPER_USE_PROXY")
    proxy_url: Optional[str] = Field(default=None, env="SCRAPER_PROXY_URL")
    
    # User agent settings
    user_agent: str = Field(default="Mozilla/5.0 (Windows NT 10.0; Win64; x64)", env="SCRAPER_USER_AGENT")
    user_agents: List[str] = Field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    ])
    
    # Rate limiting
    requests_per_minute: int = Field(default=60, env="SCRAPER_RPM")
    
    # Authentication settings
    # Can be configured per-URL via auth_config, or globally via these env vars
    auth_enabled: bool = Field(default=False, env="SCRAPER_AUTH_ENABLED")
    global_username: Optional[str] = Field(default=None, env="SCRAPER_GLOBAL_USERNAME")
    global_password: Optional[str] = Field(default=None, env="SCRAPER_GLOBAL_PASSWORD")
    global_api_key: Optional[str] = Field(default=None, env="SCRAPER_GLOBAL_API_KEY")
    global_auth_token: Optional[str] = Field(default=None, env="SCRAPER_GLOBAL_AUTH_TOKEN")
    global_auth_type: str = Field(default="cookie", env="SCRAPER_GLOBAL_AUTH_TYPE")
    
    # Per-URL authentication configuration
    # This is a list of AuthConfig objects, but Pydantic doesn't support list of BaseSettings directly
    # So we use a JSON string that gets parsed
    auth_config_json: Optional[str] = Field(default=None, env="SCRAPER_AUTH_CONFIG")
    
    @property
    def auth_config(self) -> List[Dict[str, Any]]:
        """Parse auth config from JSON string."""
        if not self.auth_config_json:
            return []
        try:
            import json
            return json.loads(self.auth_config_json)
        except Exception:
            return []
    
    class Config:
        env_file = ".env.scraper"
        env_file_encoding = "utf-8"
        # Allow extra fields for flexibility
        extra = "ignore"


# Global settings instance
settings = ScraperSettings()


def update_settings_from_dict(config: Dict[str, Any]):
    """Update settings from a dictionary (useful for programmatic configuration)."""
    for key, value in config.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
