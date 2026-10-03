# КТ2. Микросервисы и REST API

Материалы задания: [отчет](report.md) и [PDF-отчет](report.pdf).

Разработать REST-сервисы пользователей и заказов; проверить HTTP-взаимодействие Orders с Users, ошибки зависимости и время ответа.

Запуск связанных проверок из корня проекта: `python3 -m pytest -q`.

Для ручного запуска импортируйте `postman/Users-and-Orders.postman_collection.json` в Postman и выполняйте запросы сверху вниз. При установленном Node.js коллекция запускается командой `npx newman run postman/Users-and-Orders.postman_collection.json`.
