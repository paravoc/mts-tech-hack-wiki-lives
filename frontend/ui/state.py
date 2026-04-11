from __future__ import annotations

import base64
import json
import mimetypes
import re
from html import escape
from typing import Any
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

from ui.runtime import DEFAULT_BACKEND_URL
from utils.api_client import ApiClient, ApiClientError
from utils.document_tools import build_formula_token


PAGE_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
SUMMARY_LINE_PATTERN = re.compile(r"^%%summary:(.*?)%%\s*$")


def get_client() -> ApiClient:
    return ApiClient(DEFAULT_BACKEND_URL)


def safe_api_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs), None
    except ApiClientError as exc:
        return None, str(exc)


def page_id_of(item: dict[str, Any]) -> str:
    return str(item.get("pageId") or item.get("id") or "")


def page_title_of(item: dict[str, Any]) -> str:
    return str(item.get("title") or "Новая страница")


def split_document(raw_content: str) -> tuple[str, str]:
    if not raw_content:
        return "", ""
    first_line, separator, rest = raw_content.partition("\n")
    match = SUMMARY_LINE_PATTERN.match(first_line.strip())
    if not match:
        return "", raw_content
    return match.group(1).strip(), rest if separator else ""


def compose_document(summary: str, body: str) -> str:
    clean_body = body.rstrip()
    clean_summary = summary.strip()
    if not clean_summary:
        return clean_body
    if clean_body:
        return f"%%summary:{clean_summary}%%\n{clean_body}"
    return f"%%summary:{clean_summary}%%"


def stripped_content(raw_content: str) -> str:
    return split_document(raw_content)[1]


def init_session_state() -> None:
    defaults: dict[str, Any] = {
        "active_panel": "comments",
        "author_name": "Константин Иванов",
        "current_page_id": "",
        "loaded_page_id": "",
        "draft_title": "",
        "draft_summary": "",
        "draft_content": "",
        "page_search": "",
        "undo_stack": [],
        "redo_stack": [],
        "_last_draft_snapshot": "",
        "_saved_draft_snapshot": "",
        "_backend_boot_attempted": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def current_draft_snapshot() -> dict[str, str]:
    return {
        "title": st.session_state.get("draft_title", ""),
        "summary": st.session_state.get("draft_summary", ""),
        "content": st.session_state.get("draft_content", ""),
    }


def snapshot_string(snapshot: dict[str, str] | None = None) -> str:
    return json.dumps(snapshot or current_draft_snapshot(), ensure_ascii=False, sort_keys=True)


def mark_current_draft_as_saved() -> None:
    st.session_state["_saved_draft_snapshot"] = snapshot_string()


def draft_is_dirty() -> bool:
    return st.session_state.get("_saved_draft_snapshot", "") != snapshot_string()


def sync_draft_history() -> None:
    current_string = snapshot_string()
    last_snapshot = st.session_state.get("_last_draft_snapshot", "")
    if not last_snapshot:
        st.session_state["_last_draft_snapshot"] = current_string
        return
    if current_string == last_snapshot:
        return

    undo_stack = list(st.session_state.get("undo_stack", []))
    undo_stack.append(json.loads(last_snapshot))
    st.session_state["undo_stack"] = undo_stack[-60:]
    st.session_state["redo_stack"] = []
    st.session_state["_last_draft_snapshot"] = current_string


def apply_snapshot(snapshot: dict[str, str]) -> None:
    st.session_state["draft_title"] = snapshot.get("title", "")
    st.session_state["draft_summary"] = snapshot.get("summary", "")
    st.session_state["draft_content"] = snapshot.get("content", "")
    st.session_state["_last_draft_snapshot"] = snapshot_string(snapshot)


def undo_draft() -> bool:
    undo_stack = list(st.session_state.get("undo_stack", []))
    if not undo_stack:
        return False

    current = current_draft_snapshot()
    redo_stack = list(st.session_state.get("redo_stack", []))
    redo_stack.append(current)
    st.session_state["redo_stack"] = redo_stack[-60:]
    previous = undo_stack.pop()
    st.session_state["undo_stack"] = undo_stack
    apply_snapshot(previous)
    return True


def redo_draft() -> bool:
    redo_stack = list(st.session_state.get("redo_stack", []))
    if not redo_stack:
        return False

    current = current_draft_snapshot()
    undo_stack = list(st.session_state.get("undo_stack", []))
    undo_stack.append(current)
    st.session_state["undo_stack"] = undo_stack[-60:]
    next_snapshot = redo_stack.pop()
    st.session_state["redo_stack"] = redo_stack
    apply_snapshot(next_snapshot)
    return True


def set_current_page(page: dict[str, Any]) -> None:
    summary, body = split_document(str(page.get("content", "")))
    st.session_state["current_page_id"] = page_id_of(page)
    st.session_state["loaded_page_id"] = page_id_of(page)
    st.session_state["draft_title"] = page_title_of(page)
    st.session_state["draft_summary"] = summary
    st.session_state["draft_content"] = body
    st.session_state["undo_stack"] = []
    st.session_state["redo_stack"] = []
    st.session_state["_last_draft_snapshot"] = snapshot_string()
    st.session_state["_saved_draft_snapshot"] = snapshot_string()


def ensure_page_loaded(page: dict[str, Any]) -> None:
    if st.session_state.get("loaded_page_id") != page_id_of(page):
        set_current_page(page)


def build_table_block(insert_options: dict[str, Any], row_limit: int = 8) -> str:
    field_names = [str(name) for name in insert_options.get("fieldNames", [])]
    table_id = str(insert_options.get("tableId", ""))
    rows = insert_options.get("records", [])[:row_limit]
    if not field_names or not rows or not table_id:
        return ""

    header = f"| {' | '.join(field_names)} |"
    separator = f"| {' | '.join(['---'] * len(field_names))} |"
    body = []
    for record in rows:
        record_id = str(record.get("recordId", ""))
        cells = [build_formula_token(table_id, record_id, field_name) for field_name in field_names]
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, separator, *body])


def append_snippet(snippet: str) -> None:
    if not snippet:
        return
    current = st.session_state.get("draft_content", "")
    joiner = "\n" if current and not current.endswith("\n") else ""
    st.session_state["draft_content"] = f"{current}{joiner}{snippet}"


def file_to_attachment_snippet(uploaded_file) -> str:
    payload = uploaded_file.getvalue()
    mime = uploaded_file.type or mimetypes.guess_type(uploaded_file.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(payload).decode("ascii")
    src = f"data:{mime};base64,{encoded}"
    meta = {"name": uploaded_file.name, "mime": mime, "src": src, "width": 680 if mime.startswith("image/") else 0}
    return f"[[WL_ATTACHMENT:{quote(json.dumps(meta, ensure_ascii=False))}]]"


def paragraph_options(content: str) -> list[str]:
    options = []
    for part in re.split(r"\n\s*\n", content):
        text = " ".join(part.strip().split())
        if text:
            options.append(text[:120] + ("…" if len(text) > 120 else ""))
    return options or ["Весь документ"]


def collect_backlinks(pages: list[dict[str, Any]], current_page: dict[str, Any]) -> list[dict[str, Any]]:
    title = page_title_of(current_page)
    matches = []
    for item in pages:
        if page_id_of(item) == page_id_of(current_page):
            continue
        body = stripped_content(str(item.get("content", "")))
        for match in PAGE_LINK_PATTERN.finditer(body):
            if match.group(1).strip() == title:
                matches.append(item)
                break
    return matches


def render_local_cache_bridge(page_id: str, version_token: str) -> None:
    safe_page_id = escape(page_id)
    components.html(
        f"""
        <script>
        const parentDoc = window.parent.document;
        const area = parentDoc.querySelector('div[data-testid="stTextArea"] textarea');
        if (area) {{
          const key = "wikilive:draft:{safe_page_id}";
          const versionKey = key + ":version";
          const storedVersion = window.parent.localStorage.getItem(versionKey);
          const storedRaw = window.parent.localStorage.getItem(key);
          if (storedVersion === {version_token!r} && storedRaw && area.value !== storedRaw) {{
            const descriptor = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value");
            if (descriptor && descriptor.set) descriptor.set.call(area, storedRaw); else area.value = storedRaw;
            area.dispatchEvent(new Event("input", {{ bubbles: true }}));
            area.dispatchEvent(new Event("change", {{ bubbles: true }}));
          }} else {{
            window.parent.localStorage.setItem(key, area.value || "");
            window.parent.localStorage.setItem(versionKey, {version_token!r});
          }}
          area.addEventListener("input", () => {{
            window.parent.localStorage.setItem(key, area.value || "");
            window.parent.localStorage.setItem(versionKey, {version_token!r});
          }});
        }}
        window.parent.postMessage({{type: "streamlit:setFrameHeight", height: 0}}, "*");
        </script>
        """,
        height=0,
    )


@st.cache_data(ttl=45, show_spinner=False)
def load_insert_options_cached(base_url: str) -> dict[str, Any]:
    return ApiClient(base_url).get_insert_options()
