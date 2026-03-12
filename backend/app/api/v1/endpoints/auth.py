from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
    get_password_hash, verify_password,
)
from app.core.session import token_blacklist, session_manager
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse, UserUpdate

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)

    # Track session
    access_payload = decode_token(access_token)
    refresh_payload = decode_token(refresh_token)
    if refresh_payload and refresh_payload.get("jti"):
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip and request.client:
            client_ip = request.client.host
        user_agent = request.headers.get("User-Agent", "")

        evicted_jti = session_manager.register_session(
            user_id=str(user.id),
            token_jti=refresh_payload["jti"],
            ip=client_ip or "",
            user_agent=user_agent,
        )
        # Blacklist evicted session's token
        if evicted_jti:
            token_blacklist.revoke(evicted_jti, expires_at=datetime.now(timezone.utc).timestamp() + 7 * 86400)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
):
    """Logout current session — blacklists the current access token."""
    # Extract current token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_token(token)
        if payload and payload.get("jti"):
            # Blacklist the access token
            token_blacklist.revoke(payload["jti"], expires_at=payload.get("exp", 0))

    return {"detail": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all_sessions(
    current_user: User = Depends(get_current_active_user),
):
    """Logout all sessions for the current user — revokes all active tokens."""
    revoked_jtis = session_manager.revoke_all_sessions(str(current_user.id))
    for jti in revoked_jtis:
        token_blacklist.revoke(jti, expires_at=datetime.now(timezone.utc).timestamp() + 7 * 86400)

    return {
        "detail": "All sessions revoked",
        "sessions_revoked": len(revoked_jtis),
    }


@router.get("/sessions")
async def list_active_sessions(
    current_user: User = Depends(get_current_active_user),
):
    """List all active sessions for the current user."""
    sessions = session_manager.get_active_sessions(str(current_user.id))
    return {
        "sessions": [
            {
                "ip": s["ip"],
                "user_agent": s["user_agent"],
                "created_at": datetime.fromtimestamp(s["created_at"], tz=timezone.utc).isoformat(),
                "last_active": datetime.fromtimestamp(s["last_active"], tz=timezone.utc).isoformat(),
            }
            for s in sessions
        ],
        "count": len(sessions),
    }


@router.post("/register", response_model=UserResponse)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in (UserRole.SuperAdmin, UserRole.Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    exists = await db.execute(select(User).where(User.email == data.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=UserRole(data.role),
        department_id=data.department_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Check if refresh token was blacklisted
    jti = payload.get("jti")
    if jti and token_blacklist.is_revoked(jti):
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Blacklist old refresh token
    if jti:
        token_blacklist.revoke(jti, expires_at=payload.get("exp", 0))

    return Token(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return current_user
