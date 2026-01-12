from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from sqlalchemy.orm import Session, selectinload

import dependencies
import models
import schemas
import security
import services


router = APIRouter()

# Simulação de armazenamento de tokens de recuperação
reset_tokens = {}

from fastapi import Body
from jose import jwt
from datetime import datetime, timedelta

def get_user_by_email(email: str, db):
    return db.query(models.User).filter(models.User.email == email).first()

def update_user_password(user_id: int, new_password: str, db):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.password_hash = security.get_password_hash(new_password)
        db.commit()
        db.refresh(user)
    return user

# Endpoint para solicitar recuperação de senha
@router.post("/auth/forgot-password")
def forgot_password(
    email: str = Body(..., embed=True),
    db: Session = Depends(dependencies.get_db),
):
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": user.id, "exp": expire}, security.SECRET_KEY, algorithm=security.ALGORITHM)
    reset_tokens[token] = user.id
    # Em produção, envie por email. Aqui, só retorna.
    return {"reset_token": token}

# Endpoint para redefinir senha
@router.post("/auth/reset-password")
def reset_password(
    token: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(dependencies.get_db),
):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    if reset_tokens.get(token) != user_id:
        raise HTTPException(status_code=400, detail="Token não reconhecido")
    user = update_user_password(user_id, new_password, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    reset_tokens.pop(token)
    return {"message": "Senha redefinida com sucesso"}



# Helper para fingerprint
def get_fingerprint(request: Request) -> str:
    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    return security._hash_token(f"{ua}:{ip}")


@router.post("/auth/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: schemas.UserCreate,
    db: Session = Depends(dependencies.get_db),
):
    if db.query(models.User).filter_by(email=payload.email).first():
        raise HTTPException(400, "E-mail já cadastrado")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=security.hash_password(payload.password),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# =====================================================
# AUTH — LOGIN
# =====================================================

@router.post("/auth/login", response_model=schemas.Token)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db),
):
    user = db.query(models.User).filter_by(email=form.username).first()

    if not user or not security.verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciais inválidas")

    if not user.is_active:
        raise HTTPException(403, "Usuário inativo")

    fingerprint = get_fingerprint(request)

    access = security.create_access_token(
        user_id=str(user.id),
        fingerprint=fingerprint,
    )

    refresh = security.create_refresh_token(
        user_id=str(user.id),
        fingerprint=fingerprint,
    )

    # Persistir refresh (hash + jti)
    db.add(
        models.RefreshSession(
            jti=refresh["jti"],
            token_hash=refresh["token_hash"],
            user_id=user.id,
            expires_at=security._now() + timedelta(days=security.REFRESH_TOKEN_DAYS),
        )
    )
    db.commit()

    return {
        "access_token": access,
        "refresh_token": refresh["token"],
        "token_type": "bearer",
    }


    # =====================================================
    # AUTH — REFRESH
    # =====================================================

    @router.post("/auth/refresh", response_model=schemas.Token)
    def refresh_token(
        request: Request,
        refresh_token: str = Body(..., embed=True),
        db: Session = Depends(dependencies.get_db),
    ):
        fingerprint = get_fingerprint(request)

        def is_jti_active(jti: str) -> bool:
            return db.query(models.RefreshSession).filter_by(jti=jti, revoked=False).first() is not None

        def revoke_jti(jti: str):
            db.query(models.RefreshSession).filter_by(jti=jti).update({"revoked": True})

        def store_new_jti(jti, token_hash, user_id, expires_at):
            db.add(
                models.RefreshSession(
                    jti=jti,
                    token_hash=token_hash,
                    user_id=int(user_id),
                    expires_at=expires_at,
                )
            )

        tokens = security.rotate_refresh_token(
            old_token=refresh_token,
            fingerprint=fingerprint,
            is_jti_active=is_jti_active,
            revoke_jti=revoke_jti,
            store_new_jti=store_new_jti,
        )

        db.commit()
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
        }


    # =====================================================
    # AUTH — FORGOT / RESET PASSWORD
    # =====================================================

    @router.post("/auth/forgot-password")
    def forgot_password(
        email: str = Body(..., embed=True),
        db: Session = Depends(dependencies.get_db),
    ):
        user = db.query(models.User).filter_by(email=email).first()
        if not user:
            return {"message": "Se existir, enviaremos instruções"}  # anti-enumeração

        token = security.create_access_token(
            user_id=str(user.id),
            fingerprint="password-reset",
            extra_claims={"type": "password_reset"},
        )

        # Em produção: enviar por e-mail
        return {"reset_token": token}


    @router.post("/auth/reset-password")
    def reset_password(
        token: str = Body(...),
        new_password: str = Body(...),
        db: Session = Depends(dependencies.get_db),
    ):
        try:
            payload = security.decode_token(
                token=token,
                expected_type="password_reset",
                fingerprint="password-reset",
            )
        except ValueError:
            raise HTTPException(400, "Token inválido")

        user = db.query(models.User).filter_by(id=int(payload["sub"])).first()
        if not user:
            raise HTTPException(404, "Usuário não encontrado")

        user.password_hash = security.hash_password(new_password)

        # Revoga TODAS as sessões
        db.query(models.RefreshSession).filter_by(user_id=user.id).update({"revoked": True})

        db.commit()
        return {"message": "Senha redefinida com sucesso"}


    # =====================================================
    # USERS / TASKS (INALTERADOS, SÓ DEPENDÊNCIA SEGURA)
    # =====================================================

    @router.get("/users/me", response_model=schemas.UserRead)
    def get_me(
        current_user: models.User = Depends(dependencies.get_current_user),
    ):
        return current_user


@router.get("/users/me/stats", response_model=schemas.UserRead)
def get_my_stats(
    current_user: models.User = Depends(dependencies.get_current_user),
    db: Session = Depends(dependencies.get_db),
):
    db.refresh(current_user)
    return current_user


@router.get("/health", response_model=schemas.Message)
def healthcheck():
    return schemas.Message(message="OK")