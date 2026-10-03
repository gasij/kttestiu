from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    user_id: UUID
    item: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0, le=1000)


class UserSummary(BaseModel):
    id: UUID
    name: str
    email: str


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    item: str
    quantity: int
    created_at: datetime


class OrderDetails(OrderRead):
    user: UserSummary