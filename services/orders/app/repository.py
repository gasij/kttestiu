from datetime import datetime, timezone
from uuid import UUID, uuid4

from services.orders.app.schemas import OrderCreate, OrderRead


class OrderRepository:
    def __init__(self) -> None:
        self._orders: dict[UUID, OrderRead] = {}

    def create(self, data: OrderCreate) -> OrderRead:
        order = OrderRead(
            id=uuid4(),
            user_id=data.user_id,
            item=data.item,
            quantity=data.quantity,
            created_at=datetime.now(timezone.utc),
        )
        self._orders[order.id] = order
        return order

    def get(self, order_id: UUID) -> OrderRead | None:
        return self._orders.get(order_id)