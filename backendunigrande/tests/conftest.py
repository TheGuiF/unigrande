import os

import pytest
import pytest_asyncio
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from httpx import AsyncClient
from starlette.testclient import TestClient
from tortoise.contrib.fastapi import RegisterTortoise

from app.config.application import create_application
from app.config.settings import Settings, get_settings


# Função auxiliar que cria um objeto de configurações (Settings) específico para o ambiente de testes
def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


# Esta fixture cria uma versão da sua API para testes sem conexão com o banco de dados
@pytest.fixture(scope="module")
def test_app():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override

    # Remove TrustedHostMiddleware para evitar erro 400 nos testes
    app.user_middleware = [
        mw for mw in app.user_middleware if mw.cls is not TrustedHostMiddleware
    ]
    app.middleware_stack = app.build_middleware_stack()

    # Cria cliente de teste síncrono para fazer requisições à API sem servidor ativo
    with TestClient(app) as client:
        yield client


# Criando uma versão da API para testes com conexão ao banco de dados de teste
@pytest_asyncio.fixture(scope="module")
async def test_app_with_db():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override

    # Remove TrustedHostMiddleware para ambiente de teste
    app.user_middleware = [
        mw for mw in app.user_middleware if mw.cls is not TrustedHostMiddleware
    ]
    app.middleware_stack = app.build_middleware_stack()

    # Inicializa Tortoise ORM via RegisterTortoise (função que conecta a aplicação de teste ao banco de dados)
    RegisterTortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=True,
    )

    # Cria cliente assíncrono para teste
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.get("/")  # Garante que lifespan/startup sejam executados
        yield client
