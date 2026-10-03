# Учебная система микросервисов

Учебный проект для заданий КТ2 и КТ4–КТ8 по интеграционному тестированию. В системе два REST-сервиса: Users отвечает за создание и получение пользователей, Orders создает и получает заказы и перед сохранением запрашивает пользователя у Users по HTTP.

## Запуск

Требуется Python 3.11 или новее.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test,reports]"
uvicorn services.users.app.main:app --port 8001
```

Во втором терминале из корня проекта:

```bash
source .venv/bin/activate
uvicorn services.orders.app.main:app --port 8002
```

Swagger UI доступен на `/docs` каждого сервиса. Orders обращается к `USERS_SERVICE_URL` (по умолчанию `http://localhost:8001`); таймаут настраивается через `USERS_SERVICE_TIMEOUT` (секунды, по умолчанию 0.5).

## Проверки

```bash
pytest
python scripts/generate_reports.py
```

Сценарии включают успешное получение пользователя Orders-сервисом, 404 при отсутствующем пользователе, 503 при недоступном Users, измерение времени ответа, валидацию и конфликт email. Хранилища в учебной версии in-memory: данные сбрасываются при перезапуске.

## REST API и Postman

- `POST http://localhost:8001/users` — создать пользователя (`name`, `email`); возвращает `201` и UUID.
- `GET http://localhost:8001/users/{user_id}` — получить пользователя.
- `POST http://localhost:8002/orders` — создать заказ (`user_id`, `item`, `quantity`); Users вызывается до сохранения заказа.
- `GET http://localhost:8002/orders/{order_id}` — получить заказ.

Импортируйте `postman/Users-and-Orders.postman_collection.json` в Postman и выполните запросы коллекции сверху вниз: идентификаторы создаваемых сущностей сохраняются в переменных коллекции. Для запуска той же коллекции из терминала при установленном Node.js: `npx newman run postman/Users-and-Orders.postman_collection.json`.

## Материалы КТ

Папки `assignments/KT2`, `KT4`, `KT5`, `KT6`, `KT7`, `KT8` содержат README и отчет по соответствующему заданию в Markdown и PDF. В КТ4 реализован Big Bang; КТ5 — сверху вниз; КТ6 — снизу вверх; КТ7 — гибридное тестирование; КТ8 — непрерывный CI. Postman-коллекция находится в `postman/`.