from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(slots=True)
class ApiClientError(Exception):
    message: str
    status_code: int | None = None
    retryable: bool = False

    def __str__(self) -> str:
        return self.message


class ApiClient:
    def __init__(self, base_url: str, timeout_seconds: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def list_pages(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/api/pages")
        return data.get("items", [])

    def get_page(self, page_id: str) -> dict[str, Any]:
        data = self._request("GET", f"/api/pages/{page_id}")
        return data["item"]

    def create_page(self, title: str, content: str) -> dict[str, Any]:
        data = self._request(
            "POST",
            "/api/pages",
            json_body={"title": title, "content": content},
        )
        return data["item"]

    def update_page(self, page_id: str, title: str, content: str) -> dict[str, Any]:
        data = self._request(
            "PUT",
            f"/api/pages/{page_id}",
            json_body={"title": title, "content": content},
        )
        return data["item"]

    def delete_page(self, page_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/api/pages/{page_id}")

    def list_versions(self, page_id: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"/api/pages/{page_id}/versions")
        return data.get("items", [])

    def create_version(self, page_id: str, label: str, author: str = "manual") -> dict[str, Any]:
        data = self._request(
            "POST",
            f"/api/pages/{page_id}/versions",
            json_body={"label": label, "author": author},
        )
        return data["item"]

    def restore_version(self, page_id: str, version_id: str) -> dict[str, Any]:
        data = self._request("POST", f"/api/pages/{page_id}/versions/{version_id}/restore", json_body={})
        return data["item"]

    def list_comments(self, page_id: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"/api/pages/{page_id}/comments")
        return data.get("items", [])

    def create_comment(
        self,
        page_id: str,
        body: str,
        selection_label: str = "",
        author: str = "viewer",
    ) -> dict[str, Any]:
        data = self._request(
            "POST",
            f"/api/pages/{page_id}/comments",
            json_body={
                "body": body,
                "selectionLabel": selection_label,
                "author": author,
            },
        )
        return data["item"]

    def reply_to_comment(self, page_id: str, thread_id: str, body: str, author: str = "viewer") -> dict[str, Any]:
        data = self._request(
            "POST",
            f"/api/pages/{page_id}/comments/{thread_id}/replies",
            json_body={"body": body, "author": author},
        )
        return data["item"]

    def resolve_comment(self, page_id: str, thread_id: str, resolved: bool) -> dict[str, Any]:
        data = self._request(
            "POST",
            f"/api/pages/{page_id}/comments/{thread_id}/resolve",
            json_body={"resolved": resolved},
        )
        return data["item"]

    def toggle_comment_like(self, page_id: str, thread_id: str, author: str = "viewer") -> dict[str, Any]:
        data = self._request(
            "POST",
            f"/api/pages/{page_id}/comments/{thread_id}/like",
            json_body={"author": author},
        )
        return data["item"]

    def render_content(self, content: str) -> str:
        data = self._request("POST", "/api/render", json_body={"content": content})
        return data["html"]

    def get_insert_options(
        self,
        table_id: str | None = None,
        view_id: str | None = None,
    ) -> dict[str, Any]:
        query_parts: list[str] = []
        if table_id:
            query_parts.append(f"tableId={table_id}")
        if view_id:
            query_parts.append(f"viewId={view_id}")
        path = "/api/mws/insert-options"
        if query_parts:
            path += "?" + "&".join(query_parts)
        return self._request("GET", path)

    def suggest_insert(
        self,
        user_prompt: str,
        page_content: str,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "userPrompt": user_prompt,
            "pageContent": page_content,
        }
        if context is not None:
            payload["context"] = context

        data = self._request("POST", "/api/ai/suggest-insert", json_body=payload)
        return data.get("candidates", [])

    def _request(
        self,
        method: str,
        path: str,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json_body,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as exc:
            raise ApiClientError(
                f"Не удалось связаться с backend: {exc}",
                retryable=True,
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiClientError(
                f"Backend вернул не-JSON ответ со статусом {response.status_code}",
                status_code=response.status_code,
                retryable=False,
            ) from exc

        if response.ok and payload.get("success") is True:
            return payload.get("data", {})

        error = payload.get("error", {})
        raise ApiClientError(
            error.get("message", f"Запрос завершился ошибкой {response.status_code}"),
            status_code=response.status_code,
            retryable=bool(error.get("retryable", False)),
        )
