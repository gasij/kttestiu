import os
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status

from services.orders.app.repository import OrderRepository
from services.orders.app.schemas import OrderCreate, OrderDetails, OrderRead, UserSummary
from services.orders.app.user_client import UserClient


def create_app(
    repository: OrderRepository | None = None,
    users_url: str | None = None,
    user_timeout: float | None = None,
) -> FastAPI:
    orders = repository or OrderRepository()
    base_url = users_url or os.getenv("USERS_SERVICE_URL", "http://localhost:8001")
    timeout = user_timeout or float(os.getenv("USERS_SERVICE_TIMEOUT", "0.5"))
    app = FastAPI(title="Orders service", version="1.0.0")
    app.state.repository = orders

    def get_user_client() -> UserClient:
        return UserClient(base_url, timeout)

    app.state.get_user_client = get_user_client

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "orders"}

    @app.post("/orders", response_model=OrderDetails, status_code=status.HTTP_201_CREATED)
    async def create_order(
        data: OrderCreate,
        user_client: UserClient = Depends(get_user_client),
    ) -> OrderDetails:
        user_data = await user_client.get_user(str(data.user_id))
        order = orders.create(data)
        return OrderDetails(**order.model_dump(), user=UserSummary.model_validate(user_data))

    @app.get("/orders/{order_id}", response_model=OrderRead)
    def get_order(order_id: UUID) -> OrderRead:
        order = orders.get(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        return order

    return app


app = create_app()