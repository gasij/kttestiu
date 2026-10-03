from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)

REPORTS = {
    "KT2": {
        "title": "КТ2. Микросервисы и REST API",
        "objective": "Разработать REST-сервисы пользователей и заказов; проверить HTTP-взаимодействие Orders с Users, ошибки зависимости и время ответа.",
        "method": "Orders перед сохранением заказа выполняет GET /users/{user_id}. Users предоставляет POST /users и GET /users/{user_id}. Автотесты используют HTTPX ASGI transport, что позволяет связать оба приложения реальным HTTP-контрактом без сетевого запуска.",
        "tests": "tests/test_microservices_integration.py",
        "scenarios": [
            ("Успешный межсервисный вызов", "201; заказ содержит профиль владельца", "PASS"),
            ("Users не содержит пользователя", "404; заказ не сохраняется", "PASS"),
            ("Users недоступен", "503; заказ не сохраняется", "PASS"),
            ("Задержка вызова Users", "ответ менее 500 мс", "PASS"),
            ("Повторный email и невалидные данные", "409 и 422 соответственно", "PASS"),
        ],
        "result": "Все 9 API-тестов КТ2 прошли локально.",
        "finding": "При настройке проекта обнаружено невалидное имя пакета в pyproject.toml: pip отклонил сборку. Имя исправлено на PEP 508-совместимое; установка и тестирование после исправления прошли.",
        "conclusion": "Контракт между сервисами проверен вместе с позитивным и негативными ответами. In-memory хранилища предназначены для учебного стенда и очищаются после перезапуска.",
    },
    "KT4": {
        "title": "КТ4. Интеграционное тестирование методом «Большого взрыва»",
        "objective": "Объединить готовые модули Users, Orders, хранилища и HTTP-клиент на одном этапе и проверить систему как целое.",
        "method": "В один общий прогон включены оба API, репозитории и межсервисный HTTP-вызов. Сценарии не интегрируются по ступеням: сначала собран весь тестовый контур, затем запущен общий pytest suite.",
        "tests": "Полный набор tests/",
        "scenarios": [
            ("Создание и чтение пользователей", "API отвечает 201/200; неизвестный id дает 404", "PASS"),
            ("Создание заказа с существующим пользователем", "201 и встроенные данные пользователя", "PASS"),
            ("Ошибки зависимого сервиса", "404 для неизвестного user; 503 при отказе соединения", "PASS"),
            ("Сквозной latency", "вызов Users укладывается в 500 мс", "PASS"),
            ("Полная регрессия", "15 тестов после добавления всех уровней", "PASS"),
        ],
        "result": "Общий suite завершился без падений: 15 passed.",
        "finding": "Метод подтвердил работоспособность интегрированного стенда, но первоначальная ошибка метаданных пакета блокировала весь запуск до выполнения тестов. Диагностика нашла причину в pyproject.toml; исправление сняло блокировку.",
        "conclusion": "Big Bang уместен для небольшого учебного проекта из двух сервисов, но причины ранних интеграционных сбоев локализуются хуже. При росте системы нужны более ранние проверки контрактов и модулей.",
    },
    "KT5": {
        "title": "КТ5. Интеграционное тестирование сверху вниз",
        "objective": "Начать с верхнего уровня Orders API и контроллера, затем подключить реальный сервис Users и нижние модули.",
        "method": "Шаг 1: тест контроллера заказа с AsyncMock-заглушкой UserClient. Шаг 2: проверка передачи user_id и отображения данных владельца. Шаг 3: подключение настоящего Users приложения через ASGI transport и проверка сквозного сценария.",
        "tests": "tests/test_top_down.py; сквозной переход — tests/test_microservices_integration.py",
        "scenarios": [
            ("Контроллер + заглушка Users", "201; профиль добавлен в заказ", "PASS"),
            ("Заглушка сообщает 503", "ошибка возвращена клиенту, контроллер жив", "PASS"),
            ("Подключение реального Users API", "создание заказа проходит через HTTP-контракт", "PASS"),
        ],
        "result": "2 top-down теста прошли; переход к реальному сервису прошел в сквозном API тесте.",
        "finding": "Заглушка позволила проверить контроллер до подключения Users и отдельно зафиксировать передачу идентификатора. Она не проверяет сериализацию и реальный ответ Users; это покрыто следующим этапом.",
        "conclusion": "Top-down удобен для ранней проверки пользовательского API и потока управления. В проекте он быстро выявил бы расхождения DTO на границе, но для достоверной интеграции заглушку необходимо заменить нижним модулем.",
    },
    "KT6": {
        "title": "КТ6. Интеграционное тестирование снизу вверх",
        "objective": "Начать с базовых репозиториев, затем подключать API и проверять передачу данных на вышележащий слой.",
        "method": "Шаг 1: тестирование создания/чтения UserRepository и OrderRepository. Шаг 2: интеграция UserRepository с Users controller. Шаг 3: проверка созданных данных через HTTP GET.",
        "tests": "tests/test_bottom_up.py",
        "scenarios": [
            ("UserRepository: create/get", "получен тот же сохраненный пользователь", "PASS"),
            ("UserRepository: неизвестный id", "возвращается None", "PASS"),
            ("OrderRepository: create/get", "получен сохраненный заказ", "PASS"),
            ("Users controller + repository", "GET возвращает данные из внедренного репозитория", "PASS"),
        ],
        "result": "Все 4 bottom-up теста прошли.",
        "finding": "Репозитории изолированы от транспорта, поэтому их поведение проверяется быстро. На этом уровне еще не видны ошибки HTTP-контракта Orders и Users; для них подключен отдельный интеграционный набор.",
        "conclusion": "Bottom-up дает раннюю локализацию ошибок хранения и передачи модели. Он полезен как основание тестовой пирамиды, однако сам по себе не подтверждает корректность внешнего API.",
    },
    "KT7": {
        "title": "КТ7. Гибридное интеграционное тестирование",
        "objective": "Проверить критические сценарии сразу на нескольких уровнях: REST API, бизнес-правило заказа, межсервисный клиент и репозиторий.",
        "method": "Совмещены нижнеуровневые тесты репозиториев, top-down проверки Orders controller с заглушкой и сквозные вызовы двух приложений через HTTPX. Это сочетает раннюю изоляцию с проверкой контрактов.",
        "tests": "tests/test_bottom_up.py; tests/test_top_down.py; tests/test_microservices_integration.py",
        "scenarios": [
            ("Позитивный сквозной заказ", "Users профиль получен, заказ создан и прочитан", "PASS"),
            ("Отсутствующий пользователь", "заказ отклонен с 404", "PASS"),
            ("Недоступная зависимость", "возвращен 503, запись заказа отсутствует", "PASS"),
            ("Репозитории и контроллер", "нижний и верхний уровни проверены раздельно", "PASS"),
        ],
        "result": "Все уровни проверены локально; в полном наборе 15 passed.",
        "finding": "Разделение слоев локализует дефекты точнее Big Bang: repository, controller и сеть имеют самостоятельные проверки. Сквозная проверка при этом сохраняет доказательство работоспособности контракта между приложениями.",
        "conclusion": "Гибридный подход дал наиболее сбалансированное покрытие проекта: критический пользовательский поток проверен насквозь, а нижние и верхние слои можно диагностировать отдельно.",
    },
    "KT8": {
        "title": "КТ8. Непрерывное интеграционное тестирование",
        "objective": "Автоматически запускать интеграционный набор при каждом push и pull request и сохранять машиночитаемый результат.",
        "method": "GitHub Actions workflow .github/workflows/tests.yml выбирает Python 3.12, устанавливает editable package с test extras, запускает pytest с coverage и формирует JUnit XML. XML публикуется как artifact даже при падении тестов.",
        "tests": "Локальная проверка: python3 -m pytest -q",
        "scenarios": [
            ("Push / pull request", "workflow запускается на обоих типах события", "CONFIGURED"),
            ("Установка зависимостей", "pip устанавливает приложение и pytest extras", "PASS"),
            ("Локальный интеграционный прогон", "15 passed", "PASS"),
            ("Публикация результатов", "JUnit XML загружается как artifact с if: always()", "CONFIGURED"),
        ],
        "result": "Локально выполнено 15 passed. Синтаксис workflow задан; удаленный запуск GitHub Actions не подтвержден из локальной рабочей среды.",
        "finding": "Порог времени 500 мс проверяется интеграционным тестом локально и в CI. На загруженном runner возможна вариативность latency; при необходимости порог следует задавать исходя из SLA и распределения измерений.",
        "conclusion": "CI обеспечивает повторяемый запуск после изменений и сохраняет JUnit результат. Для завершенной демонстрации удаленного CI нужен push проекта в GitHub и просмотр статуса workflow.",
    },
}


def register_font() -> str:
    font_path = next((path for path in FONT_CANDIDATES if path.exists()), None)
    if font_path is None:
        raise RuntimeError("Не найден Unicode-шрифт Arial или DejaVu Sans для русскоязычного PDF")
    pdfmetrics.registerFont(TTFont("ReportFont", str(font_path)))
    return "ReportFont"


def markdown_for(code: str, report: dict[str, object]) -> str:
    lines = [
        f"# {report['title']}",
        "",
        f"**Цель:** {report['objective']}",
        "",
        f"**Ход тестирования:** {report['method']}",
        "",
        f"**Набор тестов:** `{report['tests']}`",
        "",
        "## Сценарии и результаты",
        "",
        "| Сценарий | Ожидаемый результат | Итог |",
        "|---|---|---|",
    ]
    lines.extend(f"| {name} | {expected} | {result} |" for name, expected, result in report["scenarios"])
    lines.extend(
        [
            "",
            "## Результат",
            "",
            str(report["result"]),
            "",
            "## Выявленные проблемы и ограничения",
            "",
            str(report["finding"]),
            "",
            "## Вывод",
            "",
            str(report["conclusion"]),
            "",
        ]
    )
    return "\n".join(lines)


def build_pdf(path: Path, report: dict[str, object], font_name: str) -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName=font_name, fontSize=17, leading=21, alignment=TA_LEFT, textColor=colors.HexColor("#17324d")))
    styles.add(ParagraphStyle(name="ReportBody", parent=styles["BodyText"], fontName=font_name, fontSize=9.5, leading=13, spaceAfter=5))
    styles.add(ParagraphStyle(name="ReportHeading", parent=styles["Heading2"], fontName=font_name, fontSize=12, leading=15, spaceBefore=9, spaceAfter=4))
    styles.add(ParagraphStyle(name="ReportCell", parent=styles["BodyText"], fontName=font_name, fontSize=8, leading=10))
    story = [Paragraph(escape(str(report["title"])), styles["ReportTitle"]), Spacer(1, 5 * mm)]
    sections = (
        ("Цель", report["objective"]),
        ("Ход тестирования", report["method"]),
        ("Набор тестов", report["tests"]),
    )
    for heading, body in sections:
        story.extend([Paragraph(heading, styles["ReportHeading"]), Paragraph(escape(str(body)), styles["ReportBody"])])
    story.append(Paragraph("Сценарии и результаты", styles["ReportHeading"]))
    rows = [["Сценарий", "Ожидаемый результат", "Итог"]]
    rows.extend([[Paragraph(escape(name), styles["ReportCell"]), Paragraph(escape(expected), styles["ReportCell"]), result] for name, expected, result in report["scenarios"]])
    table = Table(rows, colWidths=[49 * mm, 93 * mm, 20 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce8ed")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324d")),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b6c4cc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, Paragraph("Результат", styles["ReportHeading"]), Paragraph(escape(str(report["result"])), styles["ReportBody"]), Paragraph("Выявленные проблемы и ограничения", styles["ReportHeading"]), Paragraph(escape(str(report["finding"])), styles["ReportBody"]), Paragraph("Вывод", styles["ReportHeading"]), Paragraph(escape(str(report["conclusion"])), styles["ReportBody"])])
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm, topMargin=15 * mm, bottomMargin=15 * mm, title=str(report["title"])).build(story)


def main() -> None:
    font_name = register_font()
    for code, report in REPORTS.items():
        destination = ROOT / "assignments" / code
        destination.mkdir(parents=True, exist_ok=True)
        readme = f"# {report['title']}\n\nМатериалы задания: [отчет](report.md) и [PDF-отчет](report.pdf).\n\n{report['objective']}\n\nЗапуск связанных проверок из корня проекта: `python3 -m pytest -q`.\n"
        if code == "KT2":
            readme += "\nДля ручного запуска импортируйте `postman/Users-and-Orders.postman_collection.json` в Postman и выполняйте запросы сверху вниз. При установленном Node.js коллекция запускается командой `npx newman run postman/Users-and-Orders.postman_collection.json`.\n"
        (destination / "README.md").write_text(readme, encoding="utf-8")
        (destination / "report.md").write_text(markdown_for(code, report), encoding="utf-8")
        build_pdf(destination / "report.pdf", report, font_name)
        print(f"Сформированы {code}: README.md, report.md, report.pdf")


if __name__ == "__main__":
    main()