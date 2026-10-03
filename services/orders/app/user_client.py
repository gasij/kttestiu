import httpx
from fastapi import HTTPException


class UserClient:
    def __init__(self, base_url: str, timeout: float = 0.5, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._transport = transport

    async def get_user(self, user_id: str) -> dict[str, object]:
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.get(f"/users/{user_id}")
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as error:
            raise HTTPException(status_code=503, detail="Сервис пользователей недоступен") from error

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if response.is_error:
            raise HTTPException(status_code=503, detail="Ошибка сервиса пользователей")
        return response.json()