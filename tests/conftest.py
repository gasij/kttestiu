import httpx
import pytest
from fastapi.testclient import TestClient

from services.orders.app.main import create_app as create_orders_app
from services.orders.app.user_client import UserClient
from services.users.app.main import create_app as create_users_app


@pytest.fixture
def users_app():
    return create_users_app()


@pytest.fixture
def orders_app(users_app):
    app = create_orders_app(users_url="http://users")
    app.dependency_overrides[app.state.get_user_client] = lambda: UserClient(
        "http://users", transport=httpx.ASGITransport(app=users_app)
    )
    return app


@pytest.fixture
def users_client(users_app):
    with TestClient(users_app) as client:
        yield client


@pytest.fixture
def orders_client(orders_app):
    with TestClient(orders_app) as client:
        yield client