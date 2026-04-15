from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
BASE_URL = "https://tables.mws.ru/fusion/v1"
BACKEND_BASE_URL = "http://127.0.0.1:3000"


def load_env() -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def request_json(method: str, url: str, token: str, **kwargs: Any) -> dict[str, Any]:
    response = requests.request(
        method=method,
        url=url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=20,
        **kwargs,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(f"MWS error: {payload}")
    return payload


def list_records(token: str, table_id: str, view_id: str) -> list[dict[str, Any]]:
    payload = request_json(
        "GET",
        f"{BASE_URL}/datasheets/{table_id}/records",
        token,
        params={"viewId": view_id, "fieldKey": "name", "pageSize": 100},
    )
    return payload.get("data", {}).get("records", [])


def create_records(token: str, table_id: str, view_id: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = request_json(
        "POST",
        f"{BASE_URL}/datasheets/{table_id}/records?viewId={view_id}&fieldKey=name",
        token,
        data=json.dumps({"fieldKey": "name", "records": records}, ensure_ascii=False).encode("utf-8"),
    )
    return payload.get("data", {}).get("records", [])


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pick_existing_fields(records: list[dict[str, Any]]) -> set[str]:
    fields: set[str] = set()
    for record in records:
        fields.update(record.get("fields", {}).keys())
    return fields


def filter_fields(payload: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    if not allowed:
        return payload

    filtered: dict[str, Any] = {}
    for key, value in payload.items():
        if key not in allowed:
            continue

        if key.lower().startswith("опц") and not isinstance(value, list):
            filtered[key] = [value]
            continue

        filtered[key] = value

    return filtered


def list_pages_via_backend() -> list[dict[str, Any]]:
    response = requests.get(f"{BACKEND_BASE_URL}/api/pages", timeout=15)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(f"Backend pages list failed: {payload}")
    return payload.get("data", {}).get("items", [])


def delete_page_via_backend(page_id: str) -> None:
    response = requests.delete(f"{BACKEND_BASE_URL}/api/pages/{page_id}", timeout=15)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(f"Backend page delete failed: {payload}")


def create_page_via_backend(title: str, content: str) -> dict[str, Any]:
    response = requests.post(
        f"{BACKEND_BASE_URL}/api/pages",
        json={"title": title, "content": content},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(f"Backend page create failed: {payload}")
    return payload.get("data", {}).get("item", {})


def main() -> None:
    env = load_env()
    token = env.get("MWS_TOKEN", "")
    data_table_id = env.get("MWS_TABLE_ID", "")
    data_view_id = env.get("MWS_VIEW_ID", "")

    if not all((token, data_table_id, data_view_id)):
        raise SystemExit("В .env не хватает MWS параметров.")

    existing_data_records = list_records(token, data_table_id, data_view_id)
    allowed_data_fields = pick_existing_fields(existing_data_records)
    existing_pages = list_pages_via_backend()
    demo_titles = {"Оперативная сводка", "Паспорт релиза", "Медиа из таблицы"}
    for page in existing_pages:
        page_id = str(page.get("pageId", ""))
        title = str(page.get("title", ""))
        if title == "Debug page" or title in demo_titles:
            delete_page_via_backend(page_id)

    demo_data_templates = [
        {
            "Название": "WikiLive Demo / Релиз",
            "Опции": "Активен",
            "Статус": "В работе",
            "Описание": "Демонстрационный релиз для живых документов",
        },
        {
            "Название": "WikiLive Demo / Спринт",
            "Опции": "На ревью",
            "Статус": "Нужна проверка",
            "Описание": "Карточка для страницы со статусом и заметками",
        },
    ]

    data_records_payload = [{"fields": filter_fields(item, allowed_data_fields)} for item in demo_data_templates]
    data_records_payload = [item for item in data_records_payload if item["fields"]]
    if not data_records_payload:
        raise SystemExit("В таблице данных не нашлось подходящих полей. Добавь хотя бы Название или Опции и повтори.")

    created_data_records = create_records(token, data_table_id, data_view_id, data_records_payload)
    created_ids = [record.get("recordId", "") for record in created_data_records if record.get("recordId")]
    if not created_ids:
        raise SystemExit("MWS не вернул recordId для созданных демо-строк.")

    primary_field = "Название" if "Название" in allowed_data_fields else next(iter(allowed_data_fields), "Опции")
    secondary_field = "Опции" if "Опции" in allowed_data_fields else primary_field
    timestamp = now_iso()
    attachment_record_id = next(
        (
            record.get("recordId", "")
            for record in existing_data_records + created_data_records
            if record.get("fields", {}).get("Вложения")
        ),
        "",
    )

    demo_pages = [
        {
            "title": "Оперативная сводка",
            "content": (
                "## Что происходит сейчас\n"
                f"Проект: {{{{{data_table_id}:{created_ids[0]}:{primary_field}}}}}\n\n"
                "> Текущий статус\n"
                f"{{{{{data_table_id}:{created_ids[0]}:{secondary_field}}}}}\n\n"
                "---\n"
                "Этот документ показывает, как живая страница заменяет ручное копирование статусов из таблицы."
            ),
        },
        {
            "title": "Паспорт релиза",
            "content": (
                "## Карточка релиза\n"
                f"Релизный поток: {{{{{data_table_id}:{created_ids[1]}:{primary_field}}}}}\n\n"
                "> Что нужно проверить\n"
                f"{{{{{data_table_id}:{created_ids[1]}:{secondary_field}}}}}\n\n"
                "---\n"
                "Здесь удобно держать короткий текст, а все чувствительные к изменениям поля оставлять живыми."
            ),
        },
    ]

    if attachment_record_id and "Вложения" in allowed_data_fields:
        demo_pages.append(
            {
                "title": "Медиа из таблицы",
                "content": (
                    "## Визуальный блок\n"
                    "Ниже подтягивается изображение напрямую из MWS без отдельной загрузки в страницу.\n\n"
                    f"{{{{{data_table_id}:{attachment_record_id}:Вложения}}}}\n\n"
                    "---\n"
                    "Так можно собирать живые отчеты, документацию или карточки продукта."
                ),
            }
        )

    for page in demo_pages:
        create_page_via_backend(page["title"], page["content"])

    print("Готово.")
    print(f"Создано demo records: {', '.join(created_ids)}")
    print(f"Создано demo pages: {len(demo_pages)}")


if __name__ == "__main__":
    main()
