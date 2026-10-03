from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from services.orders.app.main import create_app


@pytest.fixture
def controller_client():
    app = create_app(users_url="http://users")
    gateway = AsyncMock()
    app.dependency_overrides[app.state.get_user_client] = lambda: gateway
    with TestClient(app) as client:
        yield client, gateway


def test_top_down_order_controller_with_users_stub(controller_client):
    client, gateway = controller_client
    gateway.get_user.return_value = {
        "id": "d9428888-122b-4b11-8b44-00b1fcd5b7aa",
        "name": "Тестовый пользователь",
        "email": "stub@example.test",
    }

    response = client.post(
        "/orders",
        json={"user_id": "d9428888-122b-4b11-8b44-00b1fcd5b7aa", "item": "Книга", "quantity": 1},
    )

    assert response.status_code == 201
    assert response.json()["user"]["email"] == "stub@example.test"
    gateway.get_user.assert_awaited_once_with("d9428888-122b-4b11-8b44-00b1fcd5b7aa")


def test_top_down_order_controller_propagates_dependency_failure(controller_client):
    client, gateway = controller_client
    gateway.get_user.side_effect = HTTPException(status_code=503, detail="Сервис пользователей недоступен")

    response = client.post(
        "/orders",
        json={"user_id": "d9428888-122b-4b11-8b44-00b1fcd5b7aa", "item": "Книга", "quantity": 1},
    )

    assert response.status_code == 503
    assert client.get("/health").json()["service"] == "orders"