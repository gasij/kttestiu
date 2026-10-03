from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, status

from services.users.app.repository import UserRepository
from services.users.app.schemas import UserCreate, UserRead


def create_app(repository: UserRepository | None = None) -> FastAPI:
    users = repository or UserRepository()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield

    app = FastAPI(title="Users service", version="1.0.0", lifespan=lifespan)
    app.state.repository = users

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "users"}

    @app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
    def create_user(data: UserCreate) -> UserRead:
        if users.email_exists(data.email):
            raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
        return users.create(data)

    @app.get("/users/{user_id}", response_model=UserRead)
    def get_user(user_id: UUID) -> UserRead:
        user = users.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    return app


app = create_app()