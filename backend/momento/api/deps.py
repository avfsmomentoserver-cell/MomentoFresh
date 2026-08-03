"""Dependencies for FastAPI routes"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from ..config import settings
from ..db import get_session

security = HTTPBasic()


def get_db():
    """Get database session dependency."""
    db = get_session()
    try:
        yield db
    finally:
        db.close()


def verify_operator(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify operator credentials."""
    correct_username = settings.operator_username
    correct_password = settings.operator_password
    
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def verify_api_key(api_key: str = ""):
    """Verify API key."""
    if api_key != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key