from uuid import UUID
from datetime import datetime, UTC, timedelta
from typing import Any

from app.core import settings
from app.security import JWTUtils


class JWTTokenService:
    
    @staticmethod
    def create_access_token(
        uuid: UUID,
        role: str,
        *,
        expire_minutes: int = settings.access_token_expire_minutes,
    ) -> str:
        
        now = datetime.now(UTC)
        expire = now + timedelta(minutes=expire_minutes)
        
        payload: dict[str, Any] = {
            "sub": str(uuid),
            "role": role,
            "exp": expire,
            "iat": now,
        }
        
        return JWTUtils.encode(payload=payload)
    
    @staticmethod
    def create_refresh_token(
        uuid: UUID,
        role: str,
        *,
        expire_days: int = settings.refresh_token_expire_days,
    ) -> str:
        
        now = datetime.now(UTC)
        expire = now + timedelta(days=expire_days)
        
        payload: dict[str, Any] = {
            "sub": str(uuid),
            "role": role,
            "exp": expire,
            "iat": now,
        }
        
        return JWTUtils.encode(payload=payload)
        
    @staticmethod
    def get_uuid_from_token(token: str) -> str:
        
        try:
            payload = JWTUtils.decode(token)
        except:
            