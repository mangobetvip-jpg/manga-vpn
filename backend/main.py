import os
import re
from functools import lru_cache
from typing import Literal

import jwt
import requests
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jwt import PyJWKClient
from pydantic import BaseModel, Field, field_validator

APP_ENV = os.getenv("APP_ENV", "production")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "https://manga-vpn.pages.dev").split(",")
    if origin.strip()
]

app = FastAPI(title="Manga VPN API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

REGIONS = [
    {"id": "us-east", "name": "Estados Unidos — Leste", "country": "US", "status": "planned"},
    {"id": "us-west", "name": "Estados Unidos — Oeste", "country": "US", "status": "planned"},
    {"id": "ca", "name": "Canadá", "country": "CA", "status": "planned"},
    {"id": "de", "name": "Alemanha", "country": "DE", "status": "planned"},
    {"id": "uk", "name": "Reino Unido", "country": "GB", "status": "planned"},
]

class ConfigRequest(BaseModel):
    region_id: str
    device_name: str = Field(min_length=1, max_length=64)
    ip_type: Literal["shared", "dedicated"]
    # Somente a chave pública WireGuard sai do dispositivo.
    public_key: str = Field(min_length=44, max_length=44)

    @field_validator("public_key")
    @classmethod
    def validate_public_key(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9+/]{43}=", value):
            raise ValueError("Chave pública WireGuard inválida")
        return value

class ProxyRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)

@lru_cache(maxsize=1)
def jwks_client():
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL não configurada")
    return PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json")

def require_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Autenticação necessária")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        signing_key = jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
    except (jwt.PyJWTError, requests.RequestException, RuntimeError, Exception) as exc:
        # Não expõe detalhes do token nem da validação ao cliente.
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada") from exc

    return {"id": claims["sub"], "claims": claims}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "manga-vpn-api"}

@app.get("/api/regions")
def regions():
    return {"regions": REGIONS}

@app.get("/api/me")
def me(user=Depends(require_user)):
    return {"user_id": user["id"]}

@app.post("/api/wireguard/config")
def create_wireguard_config(payload: ConfigRequest, user=Depends(require_user)):
    if payload.region_id not in {region["id"] for region in REGIONS}:
        raise HTTPException(status_code=404, detail="Região não encontrada")

    # Próxima etapa: consultar assinatura/limites no banco, reservar IP
    # e provisionar o peer no servidor da região. Falha fechada até existir
    # infraestrutura e regras de plano configuradas.
    raise HTTPException(
        status_code=503,
        detail="Provisionamento indisponível: servidores WireGuard ainda não conectados.",
    )

@app.post("/api/proxy/session")
def create_proxy_session(payload: ProxyRequest, user=Depends(require_user)):
    # Mantido desativado. Não implementar proxy aberto: requer allowlist,
    # bloqueio de IPs privados/metadata, DNS seguro, quotas e isolamento.
    raise HTTPException(status_code=503, detail="Proxy desativado por segurança.")
