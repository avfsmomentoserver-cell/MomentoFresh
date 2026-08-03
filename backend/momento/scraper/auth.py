"""
Authentication and Session Management for Aviator Scraper

Handles authenticated access to Aviator sites with:
- Cookie-based sessions
- Token-based authentication
- Login flows
- Session persistence
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector

from .config import settings

logger = logging.getLogger(__name__)


@dataclass
class AuthCredentials:
    """Authentication credentials for a site."""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    cookies: Optional[Dict[str, str]] = field(default_factory=dict)
    headers: Optional[Dict[str, str]] = field(default_factory=dict)
    login_url: Optional[str] = None
    login_method: str = "POST"  # POST, GET, or WEBSOCKET
    login_payload: Optional[Dict[str, Any]] = field(default_factory=dict)
    token_header: str = "Authorization"
    token_prefix: str = "Bearer"
    auth_type: str = "cookie"  # cookie, token, api_key, or none
    session_timeout: int = 3600  # Session timeout in seconds
    last_auth: Optional[datetime] = None


@dataclass
class AuthSession:
    """Authenticated session for a specific site."""
    url: str
    session: Optional[ClientSession] = None
    cookies: Optional[aiohttp.CookieJar] = None
    token: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    is_authenticated: bool = False
    last_auth: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auth_credentials: Optional[AuthCredentials] = None


class SessionManager:
    """Manages authenticated sessions for multiple Aviator sites."""
    
    def __init__(self):
        self.sessions: Dict[str, AuthSession] = {}
        self.credentials_map: Dict[str, AuthCredentials] = {}
        self.timeout = ClientTimeout(total=settings.timeout_seconds)
        
        # Load credentials from environment or config
        self._load_credentials()
    
    def _load_credentials(self):
        """Load authentication credentials from settings."""
        # If settings has auth config, use it
        if hasattr(settings, 'auth_config') and settings.auth_config:
            for config in settings.auth_config:
                creds = AuthCredentials(
                    url=config.get('url'),
                    username=config.get('username'),
                    password=config.get('password'),
                    api_key=config.get('api_key'),
                    auth_token=config.get('auth_token'),
                    auth_type=config.get('auth_type', 'cookie'),
                    login_url=config.get('login_url'),
                    login_method=config.get('login_method', 'POST'),
                    login_payload=config.get('login_payload', {}),
                    token_header=config.get('token_header', 'Authorization'),
                    token_prefix=config.get('token_prefix', 'Bearer'),
                    session_timeout=config.get('session_timeout', 3600),
                )
                self.credentials_map[creds.url] = creds
                logger.info(f"Loaded credentials for {creds.url} (type: {creds.auth_type})")
        
        # Also check for individual environment variables
        for url in settings.aviator_urls:
            if url not in self.credentials_map:
                # Try to load from environment variables
                base_name = url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_").upper()
                username = os.getenv(f"{base_name}_USERNAME") or os.getenv(f"AVIATOR_USERNAME")
                password = os.getenv(f"{base_name}_PASSWORD") or os.getenv(f"AVIATOR_PASSWORD")
                api_key = os.getenv(f"{base_name}_API_KEY") or os.getenv(f"AVIATOR_API_KEY")
                auth_token = os.getenv(f"{base_name}_AUTH_TOKEN") or os.getenv(f"AVIATOR_AUTH_TOKEN")
                
                if username or password or api_key or auth_token:
                    creds = AuthCredentials(
                        url=url,
                        username=username,
                        password=password,
                        api_key=api_key,
                        auth_token=auth_token,
                        auth_type="cookie" if (username and password) else "token" if auth_token else "api_key" if api_key else "none",
                    )
                    self.credentials_map[url] = creds
                    logger.info(f"Loaded credentials for {url} from environment")
    
    async def get_session(self, url: str) -> Optional[AuthSession]:
        """Get or create an authenticated session for a URL."""
        if url not in self.sessions:
            await self._create_session(url)
        
        session = self.sessions.get(url)
        if session:
            # Check if session is expired
            if session.expires_at and session.expires_at < datetime.utcnow():
                logger.info(f"Session expired for {url}, re-authenticating")
                await self._authenticate(session)
            
            # Check if session needs authentication
            if not session.is_authenticated:
                await self._authenticate(session)
        
        return session
    
    async def _create_session(self, url: str):
        """Create a new session for a URL."""
        credentials = self.credentials_map.get(url)
        
        # Create cookie jar
        cookie_jar = aiohttp.CookieJar(unsafe_warnings=False)
        
        # Create session with custom connector for better connection pooling
        connector = TCPConnector(
            limit=100,
            limit_per_host=20,
            force_close=True,
            enable_cleanup_closed=True,
        )
        
        session = ClientSession(
            cookie_jar=cookie_jar,
            timeout=self.timeout,
            connector=connector,
        )
        
        auth_session = AuthSession(
            url=url,
            session=session,
            cookies=cookie_jar,
            auth_credentials=credentials,
            is_authenticated=False,
        )
        
        self.sessions[url] = auth_session
        logger.debug(f"Created new session for {url}")
    
    async def _authenticate(self, session: AuthSession) -> bool:
        """Authenticate a session using its credentials."""
        if not session.auth_credentials:
            logger.debug(f"No credentials for {session.url}, skipping authentication")
            session.is_authenticated = True  # Mark as authenticated if no auth required
            return True
        
        creds = session.auth_credentials
        
        try:
            if creds.auth_type == "cookie" and creds.username and creds.password:
                return await self._authenticate_cookie(session, creds)
            elif creds.auth_type == "token" and creds.auth_token:
                return await self._authenticate_token(session, creds)
            elif creds.auth_type == "api_key" and creds.api_key:
                return await self._authenticate_api_key(session, creds)
            else:
                logger.debug(f"Unknown auth type: {creds.auth_type} for {session.url}")
                session.is_authenticated = True
                return True
        except Exception as e:
            logger.error(f"Authentication failed for {session.url}: {e}")
            return False
    
    async def _authenticate_cookie(self, session: AuthSession, creds: AuthCredentials) -> bool:
        """Authenticate using username/password (cookie-based)."""
        logger.info(f"Authenticating {creds.url} with username/password")
        
        # Use login_url if specified, otherwise try common patterns
        login_url = creds.login_url or f"{creds.url}/login" or f"{creds.url}/auth/login"
        
        # Build login payload
        payload = creds.login_payload or {
            "username": creds.username,
            "password": creds.password,
        }
        
        # Add CSRF token if needed (common pattern)
        if "csrf" not in str(payload).lower():
            # Try to get CSRF token first
            csrf_token = await self._get_csrf_token(session, login_url)
            if csrf_token:
                payload["csrf_token"] = csrf_token
                payload["CSRF-Token"] = csrf_token
        
        # Build headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Add custom headers from credentials
        headers.update(creds.headers or {})
        
        try:
            if creds.login_method.upper() == "GET":
                # GET request with query parameters
                async with session.session.get(
                    login_url,
                    params=payload,
                    headers=headers,
                    allow_redirects=True,
                ) as response:
                    if response.status == 200:
                        session.is_authenticated = True
                        session.last_auth = datetime.utcnow()
                        session.expires_at = session.last_auth + timedelta(seconds=creds.session_timeout)
                        logger.info(f"Successfully authenticated {creds.url} via GET")
                        return True
            else:
                # POST request (default)
                async with session.session.post(
                    login_url,
                    json=payload,
                    data=payload,  # Try both JSON and form data
                    headers=headers,
                    allow_redirects=True,
                ) as response:
                    if response.status == 200:
                        session.is_authenticated = True
                        session.last_auth = datetime.utcnow()
                        session.expires_at = session.last_auth + timedelta(seconds=creds.session_timeout)
                        logger.info(f"Successfully authenticated {creds.url} via POST")
                        return True
                    elif response.status in [301, 302, 303, 307, 308]:
                        # Follow redirect and check if we're logged in
                        location = response.headers.get('Location', '')
                        logger.debug(f"Redirect to {location} after login")
                        session.is_authenticated = True
                        session.last_auth = datetime.utcnow()
                        session.expires_at = session.last_auth + timedelta(seconds=creds.session_timeout)
                        return True
        except Exception as e:
            logger.error(f"Cookie authentication failed for {creds.url}: {e}")
            return False
        
        return False
    
    async def _get_csrf_token(self, session: AuthSession, url: str) -> Optional[str]:
        """Get CSRF token from a page (common requirement for login forms)."""
        try:
            from bs4 import BeautifulSoup
            async with session.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try common CSRF token locations
                    for tag in soup.find_all('meta'):
                        if tag.get('name') and 'csrf' in tag['name'].lower():
                            return tag.get('content')
                    
                    for tag in soup.find_all('input'):
                        if tag.get('name') and 'csrf' in tag['name'].lower():
                            return tag.get('value')
                    
                    # Look in scripts
                    for script in soup.find_all('script'):
                        if script.string and 'csrf' in script.string.lower():
                            # Try to extract token from script
                            import re
                            match = re.search(r'"csrf[_-]?token"[\s:]+"([^"]+)"', script.string)
                            if match:
                                return match.group(1)
                            match = re.search(r"'csrf[_-]?token'[\s:]+'([^']+)'", script.string)
                            if match:
                                return match.group(1)
        except Exception:
            pass
        return None
    
    async def _authenticate_token(self, session: AuthSession, creds: AuthCredentials) -> bool:
        """Authenticate using bearer token."""
        logger.info(f"Authenticating {creds.url} with bearer token")
        
        session.token = creds.auth_token
        session.headers[creds.token_header] = f"{creds.token_prefix} {creds.auth_token}"
        session.is_authenticated = True
        session.last_auth = datetime.utcnow()
        session.expires_at = session.last_auth + timedelta(seconds=creds.session_timeout)
        
        logger.info(f"Successfully authenticated {creds.url} with token")
        return True
    
    async def _authenticate_api_key(self, session: AuthSession, creds: AuthCredentials) -> bool:
        """Authenticate using API key."""
        logger.info(f"Authenticating {creds.url} with API key")
        
        # Common API key header names
        header_name = creds.headers.get('X-API-Key', 'X-API-Key')
        session.headers[header_name] = creds.api_key
        session.is_authenticated = True
        session.last_auth = datetime.utcnow()
        session.expires_at = session.last_auth + timedelta(seconds=creds.session_timeout)
        
        logger.info(f"Successfully authenticated {creds.url} with API key")
        return True
    
    async def close_all(self):
        """Close all sessions."""
        for url, session in self.sessions.items():
            if session.session and not session.session.closed:
                await session.session.close()
                logger.debug(f"Closed session for {url}")
        self.sessions.clear()
    
    def get_credentials(self, url: str) -> Optional[AuthCredentials]:
        """Get credentials for a URL."""
        return self.credentials_map.get(url)


# Global session manager instance
session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager
