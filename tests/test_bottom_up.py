from uuid import uuid4

from fastapi.testclient import TestClient

from services.orders.app.repository import OrderRepository
from services.orders.app.schemas import OrderCreate
from services.users.app.main import create_app
from services.users.app.repository import UserRepository
from services.users.app.schemas import UserCreate


def test_user_repository_create_and_get():
    repository = UserRepository()
    created = repository.create(UserCreate(name="Анна", email="anna@example.test"))

    assert repository.get(created.id) == created


def test_user_repository_returns_none_for_missing_id():
    assert UserRepository().get(uuid4()) is None


def test_order_repository_create_and_get():
    repository = OrderRepository()
    created = repository.create(
        OrderCreate(user_id=uuid4(), item="Ручка", quantity=3)
    )

    assert repository.get(created.id) == created


def test_users_controller_reads_user_created_in_repository():
    repository = UserRepository()
    user = repository.create(UserCreate(name="Олег", email="oleg@example.test"))
    with TestClient(create_app(repository)) as client:
        response = client.get(f"/users/{user.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Олег"