from __future__ import annotations

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import database
import models
import security

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,  # importante
)

# =====================================================
# DATABASE
# =====================================================

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# FINGERPRINT
# =====================================================

def get_fingerprint(request: Request) -> str:
    """
    Fingerprint simples e determinístico.
    Em produção: melhorar com JS + cookie httpOnly.
    """
    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    raw = f"{ua}:{ip}"
    return security.hashlib.sha256(raw.encode()).hexdigest()

# =====================================================
# CURRENT USER (BLINDADO)
# =====================================================

def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )

    fingerprint = get_fingerprint(request)

    try:
        payload = security.decode_token(
            token=token,
            expected_type="access",
            fingerprint=fingerprint,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]

    user = (
        db.query(models.User)
        .filter(models.User.id == int(user_id))
        .first()
    )

    if not user or (hasattr(user, "is_active") and not user.is_active):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido ou inativo",
        )

    return user
