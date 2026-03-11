from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLE_PERMISSIONS = {
    "SuperAdmin": ["*"],
    "Admin": [
        "users:read", "users:write",
        "patients:read", "patients:write",
        "appointments:read", "appointments:write",
        "ipd:read", "ipd:write",
        "billing:read", "billing:write",
        "inventory:read", "inventory:write",
        "pharmacy:read", "pharmacy:write",
        "laboratory:read", "laboratory:write",
        "radiology:read", "radiology:write",
        "ot:read", "ot:write",
        "reports:read", "reports:export",
        "staff:read", "staff:write",
    ],
    "Doctor": [
        "patients:read", "patients:write",
        "appointments:read", "appointments:write",
        "ipd:read", "ipd:write",
        "pharmacy:read", "pharmacy:prescribe",
        "laboratory:read", "laboratory:order",
        "radiology:read", "radiology:order",
        "ot:read", "ot:write",
        "reports:read",
    ],
    "Nurse": [
        "patients:read",
        "appointments:read",
        "ipd:read", "ipd:nursing",
        "pharmacy:read",
        "laboratory:read",
    ],
    "Pharmacist": [
        "patients:read",
        "pharmacy:read", "pharmacy:dispense",
        "inventory:read", "inventory:write",
    ],
    "LabTech": [
        "patients:read",
        "laboratory:read", "laboratory:write",
    ],
    "Receptionist": [
        "patients:read", "patients:write",
        "appointments:read", "appointments:write",
        "billing:read", "billing:write",
    ],
    "Accountant": [
        "billing:read", "billing:write",
        "reports:read", "reports:export",
        "inventory:read",
    ],
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: UUID, role: str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "role": role, "exp": expire, "type": "access"}
    if extra:
        payload.update(extra)
    secret = settings.SECRET_KEY.get_secret_value()
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "exp": expire, "type": "refresh"}
    secret = settings.SECRET_KEY.get_secret_value()
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        secret = settings.SECRET_KEY.get_secret_value()
        return jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def has_permission(role: str, permission: str) -> bool:
    perms = ROLE_PERMISSIONS.get(role, [])
    return "*" in perms or permission in perms
