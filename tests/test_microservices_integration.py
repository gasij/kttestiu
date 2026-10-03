from time import perf_counter

import httpx
from fastapi.testclient import TestClient

from services.orders.app.main import create_app as create_orders_app
from services.orders.app.user_client import UserClient
from services.users.app.main import create_app as create_users_app


def test_orders_service_fetches_user_and_creates_order(users_client, orders_client):
    user_response = users_client.post("/users", json={"name": "Алексей", "email": "alex@example.test"})
    assert user_response.status_code == 201

    response = orders_client.post(
        "/orders",
        json={"user_id": user_response.json()["id"], "item": "Книга", "quantity": 2},
    )

    assert response.status_code == 201
    assert response.json()["user"]["id"] == user_response.json()["id"]
    assert response.json()["user"]["email"] == "alex@example.test"
    assert response.json()["item"] == "Книга"


def test_orders_service_returns_503_when_users_service_is_unavailable():
    app = create_orders_app(users_url="http://127.0.0.1:1", user_timeout=0.05)
    with TestClient(app) as client:
        response = client.post(
            "/orders",
            json={"user_id": "d9428888-122b-4b11-8b44-00b1fcd5b7aa", "item": "Книга", "quantity": 1},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Сервис пользователей недоступен"
    assert app.state.repository._orders == {}


def test_orders_service_returns_404_when_user_does_not_exist(orders_client):
    response = orders_client.post(
        "/orders",
        json={"user_id": "d9428888-122b-4b11-8b44-00b1fcd5b7aa", "item": "Книга", "quantity": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Пользователь не найден"


def test_orders_service_maps_users_server_error_to_503():
    app = create_orders_app(users_url="http://users")
    app.dependency_overrides[app.state.get_user_client] = lambda: UserClient(
        "http://users",
        transport=httpx.MockTransport(lambda _: httpx.Response(500, json={"detail": "internal error"})),
    )
    with TestClient(app) as client:
        response = client.post(
            "/orders",
            json={"user_id": "d9428888-122b-4b11-8b44-00b1fcd5b7aa", "item": "Книга", "quantity": 1},
        )

    assert response.status_code == 503


def test_created_order_can_be_retrieved(users_client, orders_client):
    user = users_client.post("/users", json={"name": "Нина", "email": "nina@example.test"}).json()
    created = orders_client.post(
        "/orders",
        json={"user_id": user["id"], "item": "Альбом", "quantity": 1},
    )

    response = orders_client.get(f"/orders/{created.json()['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created.json()["id"]


def test_orders_service_returns_404_for_unknown_order(orders_client):
    response = orders_client.get("/orders/d9428888-122b-4b11-8b44-00b1fcd5b7aa")

    assert response.status_code == 404


def test_interservice_response_time_is_below_500ms(users_client, orders_client):
    user_response = users_client.post("/users", json={"name": "Мария", "email": "maria@example.test"})
    started = perf_counter()
    response = orders_client.post(
        "/orders",
        json={"user_id": user_response.json()["id"], "item": "Тетрадь", "quantity": 1},
    )
    elapsed = perf_counter() - started

    assert response.status_code == 201
    assert 0 < elapsed < 0.5, f"Запрос занял {elapsed:.3f} с, лимит 0.5 с"


def test_users_service_rejects_duplicate_email(users_client):
    payload = {"name": "Иван", "email": "ivan@example.test"}
    assert users_client.post("/users", json=payload).status_code == 201
    assert users_client.post("/users", json=payload).status_code == 409


def test_users_service_validates_required_fields(users_client):
    response = users_client.post("/users", json={"name": "", "email": "not-an-email"})
    assert response.status_code == 422