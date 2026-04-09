from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
BASE_URL = "https://tables.mws.ru/fusion/v1"


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


def main() -> None:
    env = load_env()
    token = env.get("MWS_TOKEN", "")
    data_table_id = env.get("MWS_TABLE_ID", "")
    data_view_id = env.get("MWS_VIEW_ID", "")
    wiki_table_id = env.get("WIKI_PAGES_TABLE_ID", "")
    wiki_view_id = env.get("WIKI_PAGES_VIEW_ID", "")

    if not all((token, data_table_id, data_view_id, wiki_table_id, wiki_view_id)):
        raise SystemExit("В .env не хватает MWS/WikiPages параметров.")

    existing_data_records = list_records(token, data_table_id, data_view_id)
    allowed_data_fields = pick_existing_fields(existing_data_records)

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

    demo_pages = []
    for index, record_id in enumerate(created_ids, start=1):
        demo_pages.append(
            {
                "fields": {
                    "pageId": f"demo-{record_id.lower()}",
                    "title": f"Демо-страница {index}",
                    "content": (
                        "## Короткая сводка\n"
                        f"Название: {{{{{data_table_id}:{record_id}:{primary_field}}}}}\n\n"
                        "> Важный статус\n"
                        f"{{{{{data_table_id}:{record_id}:{secondary_field}}}}}\n\n"
                        "---\n"
                        "Этот текст создан seed-скриптом и уже готов для демонстрации в UI."
                    ),
                    "createdAt": timestamp,
                    "updatedAt": timestamp,
                }
            }
        )

    create_records(token, wiki_table_id, wiki_view_id, demo_pages)

    print("Готово.")
    print(f"Создано demo records: {', '.join(created_ids)}")
    print(f"Создано demo pages: {len(demo_pages)}")


if __name__ == "__main__":
    main()
