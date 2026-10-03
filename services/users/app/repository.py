from uuid import UUID, uuid4

from services.users.app.schemas import UserCreate, UserRead


class UserRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, UserRead] = {}
        self._emails: set[str] = set()

    def create(self, data: UserCreate) -> UserRead:
        user = UserRead(id=uuid4(), name=data.name, email=data.email)
        self._users[user.id] = user
        self._emails.add(user.email)
        return user

    def get(self, user_id: UUID) -> UserRead | None:
        return self._users.get(user_id)

    def email_exists(self, email: str) -> bool:
        return email in self._emails