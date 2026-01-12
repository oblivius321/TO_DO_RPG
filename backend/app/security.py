from __future__ import annotations

import os
import hashlib
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

# =====================================================
# CONFIGURAÇÃO (SEM PIEDADE)
# =====================================================

SECRET_KEY = os.getenv("TODO_RPG_SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "5"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY fraca ou inexistente. Gere uma chave forte.")

# =====================================================
# PASSWORDS — ARGON2 (PADRÃO MODERNO)
# =====================================================

_pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError("Senha fraca. Mínimo 10 caracteres.")
    return _pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _pwd_context.verify(password, hashed)


# =====================================================
# UTILS
# =====================================================

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    """Nunca salvar token puro no banco"""
    return hashlib.sha256(token.encode()).hexdigest()


# =====================================================
# JWT — CRIAÇÃO
# =====================================================

def create_access_token(
    *,
    user_id: str,
    fingerprint: str,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    payload = {
        "sub": user_id,
        "type": "access",
        "jti": str(uuid4()),
        "fp": fingerprint,
        "iat": _now(),
        "nbf": _now(),
        "exp": _now() + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    *,
    user_id: str,
    fingerprint: str,
) -> Dict[str, str]:
    jti = str(uuid4())

    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "fp": fingerprint,
        "iat": _now(),
        "nbf": _now(),
        "exp": _now() + timedelta(days=REFRESH_TOKEN_DAYS),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "token": token,
        "jti": jti,
        "token_hash": _hash_token(token),
    }


# =====================================================
# JWT — VALIDAÇÃO
# =====================================================

def decode_token(
    *,
    token: str,
    expected_type: str,
    fingerprint: str,
) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "jti", "fp", "iat", "nbf"]},
        )

        if payload["type"] != expected_type:
            raise JWTError("Tipo de token inválido.")

        if payload["fp"] != fingerprint:
            raise JWTError("Fingerprint incompatível.")

        return payload

    except ExpiredSignatureError:
        raise ValueError("Token expirado.")

    except JWTError:
        raise ValueError("Token inválido ou adulterado.")


# =====================================================
# REFRESH TOKEN ROTATION (ANTI-REUSE)
# =====================================================

def rotate_refresh_token(
    *,
    old_token: str,
    fingerprint: str,
    is_jti_active,
    revoke_jti,
    store_new_jti,
) -> Dict[str, str]:
    """
    Callbacks esperados:
    - is_jti_active(jti) -> bool
    - revoke_jti(jti)
    - store_new_jti(jti, token_hash, user_id, expires_at)
    """

    payload = decode_token(
        token=old_token,
        expected_type="refresh",
        fingerprint=fingerprint,
    )

    jti = payload["jti"]

    if not is_jti_active(jti):
        raise ValueError("Reuse de refresh token detectado. Sessão comprometida.")

    # Mata o refresh antigo
    revoke_jti(jti)

    # Cria novo refresh
    new_refresh = create_refresh_token(
        user_id=payload["sub"],
        fingerprint=fingerprint,
    )

    store_new_jti(
        jti=new_refresh["jti"],
        token_hash=new_refresh["token_hash"],
        user_id=payload["sub"],
        expires_at=_now() + timedelta(days=REFRESH_TOKEN_DAYS),
    )

    return {
        "refresh_token": new_refresh["token"],
        "access_token": create_access_token(
            user_id=payload["sub"],
            fingerprint=fingerprint,
        ),
    }
