import logging
import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pydantic import AnyUrl
from pydantic_settings import BaseSettings

# Carrega as variáveis de ambiente do arquivo .env
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(
    ","
)  # Carrega a lista de domínios que podem fazer requisições para API. O .split(",") transforma uma string em uma lista
SECRET_KEY = os.getenv(
    "SECRET_KEY", "mysecretkey"
)  # Uma chave secreta usada para "assinar" e verificar os tokens de login
ALGORITHM = "HS256"  # Algoritmo de criptografia usado para a assinatura (HS256)
EXPIRES_MINUTES = 30  # Define por quanto tempo um token de login é válido (30 minutos)
TOKEN_URL = "/users/login/admin"  # Define o endpoint de autenticação no FastAPI
OAUTH2_SCHEME = OAuth2PasswordBearer(
    tokenUrl=TOKEN_URL
)  # Cria um "esquema" de segurança que o FastAPI usará para proteger as rotas e para a documentação interativa

log = logging.getLogger("uvicorn")
load_dotenv()


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl = None


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()


# Instância do FastAPI com OpenAPI configurada
OPENAPI_SCHEMA = {
    "openapi": "3.0.2",
    "info": {
        "title": "Unigrande API",
        "version": "1.0.0",
        "description": "API Unigrande",
    },
    "components": {
        "securitySchemes": {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/users/login/admin",  # Este é o endpoint que gera o token
                    }
                },
            }
        }
    },
    "security": [
        {"OAuth2PasswordBearer": []}
    ],  # Garantir que todas as rotas usem esse esquema de segurança
}
