from __future__ import annotations

from html import escape
import os
import time
from typing import Any

import streamlit as st

from utils.api_client import ApiClient, ApiClientError
from utils.document_tools import (
    build_formula_token,
    count_words,
    describe_formula,
    extract_formula_tokens,
    render_document_html,
    replace_formula_token,
)

DEFAULT_BACKEND_URL = os.getenv("WIKILIVE_BACKEND_URL", "http://127.0.0.1:3000")
AUTO_PREVIEW_DELAY_SECONDS = 1.2
AUTO_SAVE_DELAY_SECONDS = 2.8


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Manrope:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:wght@400;600;700&display=swap');
            :root {
                --panel: rgba(255, 251, 246, 0.86); --ink: #271f1a; --muted: #6d6259;
                --line: rgba(92, 72, 56, 0.13); --accent: #bb5a32; --accent-strong: #8d3d22;
                --sage: #2f7e69; --paper-shadow: 0 22px 54px rgba(59, 43, 31, 0.10);
                --button-bg: linear-gradient(180deg, #252733 0%, #161823 100%);
                --button-bg-hover: linear-gradient(180deg, #2e3140 0%, #1b1d2a 100%);
            }
            .stApp {
                background: radial-gradient(circle at top left, rgba(187, 90, 50, 0.12), transparent 26%),
                    radial-gradient(circle at top right, rgba(47, 126, 105, 0.10), transparent 24%),
                    linear-gradient(180deg, #f8f2e8 0%, #efe5d8 100%);
                color: var(--ink); font-family: 'Manrope', sans-serif;
            }
            .block-container { max-width: 1520px; padding-top: 1rem; padding-bottom: 2rem; }
            [data-testid="stSidebar"] { background: linear-gradient(180deg, #232530 0%, #1a1c25 100%); }
            [data-testid="stSidebar"] * { color: #f6efe8; }
            .hero-card, .metric-card, .glass-card, .formula-card, .toolbar-card {
                border: 1px solid var(--line); border-radius: 28px; background: var(--panel);
                box-shadow: var(--paper-shadow); backdrop-filter: blur(12px);
            }
            .hero-card { padding: 1.45rem 1.6rem; margin-bottom: 1rem; }
            .hero-kicker { text-transform: uppercase; letter-spacing: 0.18em; color: var(--accent); font-size: 0.72rem; font-weight: 800; margin-bottom: 0.55rem; }
            .hero-title { font-family: 'Fraunces', serif; font-size: 2.35rem; line-height: 1.02; margin-bottom: 0.5rem; font-weight: 700; }
            .hero-text { color: var(--muted); line-height: 1.62; margin: 0; max-width: 980px; }
            .metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.9rem; margin-bottom: 1rem; }
            .metric-card { padding: 1rem 1.05rem; }
            .metric-label { color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 800; margin-bottom: 0.35rem; }
            .metric-value { font-size: 1.08rem; font-weight: 800; }
            .metric-value.serif { font-family: 'Fraunces', serif; font-size: 1.25rem; line-height: 1.1; }
            .glass-card, .toolbar-card { padding: 1rem 1.1rem 1.15rem 1.1rem; margin-bottom: 1rem; }
            .section-title { font-size: 1.02rem; font-weight: 800; margin-bottom: 0.22rem; }
            .section-subtitle { color: var(--muted); line-height: 1.55; font-size: 0.92rem; }
            .status-pill { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.48rem 0.74rem; border-radius: 999px; font-size: 0.82rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.06); }
            .status-pill.ok { color: #8de0be; } .status-pill.fail { color: #ffb29e; }
            .writer-shell { background: linear-gradient(180deg, rgba(255,255,255,0.56) 0%, rgba(255,252,246,0.35) 100%); border: 1px solid rgba(92, 72, 56, 0.12); border-radius: 34px; padding: 1.15rem; box-shadow: var(--paper-shadow); margin-bottom: 1rem; }
            .paper-sheet {
                background: linear-gradient(180deg, rgba(255, 253, 249, 0.98) 0%, rgba(255, 251, 246, 0.98) 100%),
                    repeating-linear-gradient(180deg, transparent 0, transparent 34px, rgba(206, 186, 166, 0.13) 34px, rgba(206, 186, 166, 0.13) 35px);
                border: 1px solid rgba(92, 72, 56, 0.12); border-radius: 28px; min-height: 300px; padding: 2rem 2.35rem;
            }
            .paper-heading { font-family: 'Fraunces', serif; font-size: 1.5rem; margin-bottom: 0.35rem; }
            .paper-meta { color: var(--muted); font-size: 0.88rem; margin-bottom: 1.4rem; }
            .doc-heading { font-family: 'Fraunces', serif; font-size: 1.45rem; line-height: 1.18; margin: 1.1rem 0 0.55rem 0; color: var(--ink); }
            .doc-paragraph { margin: 0 0 0.9rem 0; font-family: 'Source Serif 4', serif; font-size: 1.12rem; line-height: 1.9; color: #2a241f; }
            .doc-callout { border-left: 4px solid var(--accent); background: rgba(187, 90, 50, 0.08); border-radius: 0 18px 18px 0; padding: 0.95rem 1rem; font-family: 'Source Serif 4', serif; font-size: 1.04rem; line-height: 1.8; margin: 1rem 0; }
            .doc-divider { height: 1px; border-radius: 999px; margin: 1.2rem 0; background: linear-gradient(90deg, rgba(187,90,50,0), rgba(187,90,50,0.38), rgba(187,90,50,0)); }
            .doc-formula-chip { display: inline-flex; align-items: center; gap: 0.42rem; vertical-align: middle; padding: 0.22rem 0.54rem; border-radius: 999px; background: linear-gradient(180deg, rgba(47,126,105,0.16), rgba(47,126,105,0.10)); border: 1px solid rgba(47,126,105,0.18); margin: 0 0.12rem; font-family: 'Manrope', sans-serif; }
            .doc-formula-chip__index { display: inline-flex; align-items: center; justify-content: center; min-width: 1.45rem; height: 1.45rem; border-radius: 999px; background: rgba(255,255,255,0.72); color: var(--sage); font-size: 0.72rem; font-weight: 800; }
            .doc-formula-chip__label { color: #175848; font-size: 0.82rem; font-weight: 800; }
            .doc-formula-chip__value { color: #32594d; font-size: 0.82rem; max-width: 14rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .doc-empty-state__title { font-family: 'Fraunces', serif; font-size: 1.5rem; margin-bottom: 0.4rem; }
            .doc-empty-state__text { color: var(--muted); max-width: 34rem; line-height: 1.7; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
            div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
                background: rgba(255, 250, 244, 0.92) !important; color: #2b241d !important;
                border: 1px solid rgba(92,72,56,0.15) !important;
                box-shadow: inset 0 1px 1px rgba(255,255,255,0.8), 0 8px 22px rgba(59,43,31,0.06) !important;
            }
            div[data-testid="stTextInput"] input {
                font-family: 'Manrope', sans-serif !important; font-size: 1.02rem !important;
                border-radius: 20px !important; padding: 0.95rem 1rem !important;
            }
            div[data-testid="stTextArea"] textarea {
                font-family: 'Source Serif 4', serif !important; font-size: 1.12rem !important;
                line-height: 1.85 !important; min-height: 740px !important; border-radius: 28px !important;
                padding: 1.8rem 1.9rem !important; caret-color: var(--accent) !important;
            }
            label[data-testid="stWidgetLabel"] { color: #594d44 !important; font-weight: 700 !important; }
            button[data-baseweb="button"], .stButton > button, div[data-testid="stPopover"] > button {
                color: #fffaf4 !important; background: var(--button-bg) !important;
                border: 1px solid rgba(255, 248, 240, 0.12) !important; box-shadow: 0 14px 34px rgba(17, 18, 28, 0.24) !important;
                border-radius: 18px !important; font-weight: 800 !important; min-height: 3.2rem !important;
            }
            button[data-baseweb="button"] *, .stButton > button *, div[data-testid="stPopover"] > button * { color: inherit !important; }
            button[data-baseweb="button"]:hover, .stButton > button:hover, div[data-testid="stPopover"] > button:hover {
                background: var(--button-bg-hover) !important; border-color: rgba(255, 196, 167, 0.32) !important;
            }
            .preview-shell { border: 1px dashed rgba(92, 72, 56, 0.18); border-radius: 22px; background: rgba(255, 255, 255, 0.72); padding: 1.05rem 1rem; min-height: 320px; }
            .preview-shell img, .preview-shell .wikilive-attachment-image__img { max-width: 100%; height: auto; display: block; border-radius: 18px; border: 1px solid rgba(92,72,56,0.12); box-shadow: 0 18px 40px rgba(59,43,31,0.12); margin-bottom: 0.65rem; }
            .preview-shell .wikilive-insert, .preview-shell .wikilive-insert-link { color: var(--accent-strong); }
            .formula-card { padding: 0.85rem 0.95rem; margin-bottom: 0.75rem; background: rgba(255, 252, 247, 0.88); }
            .formula-title { display: flex; align-items: center; gap: 0.55rem; margin-bottom: 0.3rem; }
            .formula-index { width: 1.6rem; height: 1.6rem; border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; background: rgba(47,126,105,0.12); color: var(--sage); font-weight: 800; font-size: 0.74rem; }
            .formula-field { font-weight: 800; } .formula-help { color: var(--muted); font-size: 0.88rem; line-height: 1.5; margin-bottom: 0.45rem; }
            .formula-raw { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #5d5248; word-break: break-word; margin-bottom: 0.55rem; }
            .note-chip-row { display: flex; gap: 0.55rem; flex-wrap: wrap; margin-top: 0.25rem; margin-bottom: 0.45rem; }
            .note-chip { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.6rem; border-radius: 999px; background: rgba(255,255,255,0.72); border: 1px solid rgba(92,72,56,0.12); color: #4e463f; font-size: 0.8rem; font-weight: 700; }
            .sidebar-note { color: rgba(246,239,232,0.72); font-size: 0.88rem; line-height: 1.55; }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-weight: 800 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_client() -> ApiClient:
    return ApiClient(DEFAULT_BACKEND_URL)


def ensure_state() -> None:
    defaults: dict[str, Any] = {
        "selected_page_id": None,
        "editor_title": "",
        "editor_content": "",
        "preview_html": "",
        "ai_prompt": "",
        "ai_candidates": [],
        "last_error": "",
        "last_success": "",
        "loaded_page_snapshot": None,
        "live_updates_enabled": True,
        "live_refresh_seconds": 4,
        "auto_preview_enabled": True,
        "autosave_enabled": True,
        "last_live_sync_at": "",
        "last_remote_sync_epoch": 0.0,
        "insert_options_cache": None,
        "insert_options_catalog": {},
        "insert_options_cache_key": "",
        "insert_options_error": "",
        "saved_table_presets": [],
        "active_table_key": "",
        "custom_table_label": "Пользовательская таблица",
        "custom_table_id": "",
        "custom_view_id": "",
        "editor_dirty": False,
        "editor_dirty_at": 0.0,
        "last_preview_source": "",
        "last_saved_source": "",
        "last_saved_title": "",
        "worker_note": "Готов к вводу.",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def mark_editor_dirty() -> None:
    st.session_state.editor_dirty = True
    st.session_state.editor_dirty_at = time.time()
    st.session_state.worker_note = "Пишешь спокойно, фоновые задачи подождут короткую паузу."


def reset_editor() -> None:
    st.session_state.selected_page_id = None
    st.session_state.editor_title = ""
    st.session_state.editor_content = ""
    st.session_state.preview_html = ""
    st.session_state.ai_candidates = []
    st.session_state.loaded_page_snapshot = None
    st.session_state.editor_dirty = False
    st.session_state.last_preview_source = ""
    st.session_state.last_saved_source = ""
    st.session_state.last_saved_title = ""
    st.session_state.worker_note = "Открыт новый черновик."


def load_page(page: dict[str, Any]) -> None:
    st.session_state.selected_page_id = page.get("pageId")
    st.session_state.editor_title = page.get("title", "")
    st.session_state.editor_content = page.get("content", "")
    st.session_state.preview_html = page.get("renderedHtml", "")
    st.session_state.ai_candidates = []
    st.session_state.loaded_page_snapshot = {
        "title": st.session_state.editor_title,
        "content": st.session_state.editor_content,
        "updatedAt": page.get("updatedAt", ""),
    }
    st.session_state.editor_dirty = False
    st.session_state.last_preview_source = st.session_state.editor_content
    st.session_state.last_saved_source = st.session_state.editor_content
    st.session_state.last_saved_title = st.session_state.editor_title
    st.session_state.worker_note = "Страница синхронизирована с backend."


def insert_candidate(candidate_insert: str) -> None:
    current = st.session_state.editor_content.rstrip()
    if current:
        st.session_state.editor_content = f"{current}\n{candidate_insert}"
    else:
        st.session_state.editor_content = candidate_insert
    mark_editor_dirty()
    st.session_state.last_success = "Вставка добавлена в документ."


def insert_text_snippet(snippet: str, new_line: bool = True) -> None:
    current = st.session_state.editor_content
    if not current.strip():
        st.session_state.editor_content = snippet
    elif new_line:
        separator = "\n" if current.endswith("\n") else "\n\n"
        st.session_state.editor_content = f"{current}{separator}{snippet}"
    else:
        st.session_state.editor_content = f"{current}{snippet}"
    mark_editor_dirty()


def build_record_label(record: dict[str, Any]) -> str:
    fields = record.get("fields", {})
    for preferred in ("Название", "title", "name", "Статус", "status", "Опции"):
        value = fields.get(preferred)
        if value:
            return f"{record.get('recordId', 'record')} · {value}"
    for field_value in fields.values():
        if field_value:
            return f"{record.get('recordId', 'record')} · {field_value}"
    return record.get("recordId", "record")


def make_table_cache_key(table_id: str, view_id: str) -> str:
    return f"{table_id.strip()}::{view_id.strip()}"


def normalize_table_preset(preset: dict[str, Any]) -> dict[str, Any] | None:
    table_id = str(preset.get("tableId", "")).strip()
    if not table_id:
        return None

    view_id = str(preset.get("viewId", "")).strip()
    key = str(preset.get("key", "")).strip() or make_table_cache_key(table_id, view_id)
    label = str(preset.get("label", "")).strip() or table_id
    return {
        "key": key,
        "label": label,
        "tableId": table_id,
        "viewId": view_id,
        "role": str(preset.get("role", "data")).strip() or "data",
    }


def merge_table_presets(presets: list[dict[str, Any]] | None) -> None:
    if presets is None:
        return

    merged: dict[str, dict[str, Any]] = {
        preset["key"]: preset
        for preset in st.session_state.saved_table_presets
        if isinstance(preset, dict) and preset.get("key")
    }
    for preset in presets:
        normalized = normalize_table_preset(preset)
        if normalized is not None:
            merged[normalized["key"]] = normalized

    st.session_state.saved_table_presets = list(merged.values())
    if not st.session_state.active_table_key and st.session_state.saved_table_presets:
        st.session_state.active_table_key = st.session_state.saved_table_presets[0]["key"]


def get_saved_table_presets() -> list[dict[str, Any]]:
    return [preset for preset in st.session_state.saved_table_presets if isinstance(preset, dict)]


def get_active_table_settings() -> dict[str, Any] | None:
    presets = {preset["key"]: preset for preset in get_saved_table_presets() if preset.get("key")}
    active_key = st.session_state.active_table_key
    if active_key in presets:
        return presets[active_key]

    custom_table_id = st.session_state.custom_table_id.strip()
    if active_key == "custom":
        if custom_table_id:
            return {
                "key": "custom",
                "label": st.session_state.custom_table_label.strip() or "Пользовательская таблица",
                "tableId": custom_table_id,
                "viewId": st.session_state.custom_view_id.strip(),
                "role": "custom",
            }
        return None

    if custom_table_id:
        return {
            "key": "custom",
            "label": st.session_state.custom_table_label.strip() or "Пользовательская таблица",
            "tableId": custom_table_id,
            "viewId": st.session_state.custom_view_id.strip(),
            "role": "custom",
        }

    if presets:
        fallback = next(iter(presets.values()))
        st.session_state.active_table_key = fallback["key"]
        return fallback

    return None


def set_active_table_from_response(insert_options: dict[str, Any]) -> None:
    active_table = insert_options.get("activeTable", {})
    table_id = str(active_table.get("tableId", "")).strip()
    view_id = str(active_table.get("viewId", "")).strip()
    if not table_id:
        return

    cache_key = make_table_cache_key(table_id, view_id)
    for preset in get_saved_table_presets():
        if preset.get("tableId") == table_id and preset.get("viewId", "") == view_id:
            st.session_state.active_table_key = preset["key"]
            return

    if st.session_state.active_table_key == "custom":
        st.session_state.custom_table_id = table_id
        st.session_state.custom_view_id = view_id
        if not st.session_state.custom_table_label.strip():
            st.session_state.custom_table_label = active_table.get("label", "Пользовательская таблица") or "Пользовательская таблица"
        return

    st.session_state.active_table_key = cache_key


def get_cached_insert_options_for_table(table_id: str) -> dict[str, Any] | None:
    active_options = st.session_state.insert_options_cache
    if isinstance(active_options, dict) and active_options.get("tableId") == table_id:
        return active_options

    for option_set in st.session_state.insert_options_catalog.values():
        if isinstance(option_set, dict) and option_set.get("tableId") == table_id:
            return option_set

    return None


def backend_status(client: ApiClient) -> tuple[bool, str]:
    try:
        health = client.health()
        return True, f"Сервер отвечает: {health.get('status', 'ok')}"
    except ApiClientError as exc:
        return False, str(exc)


def fetch_pages(client: ApiClient) -> tuple[list[dict[str, Any]], str | None]:
    try:
        return client.list_pages(), None
    except ApiClientError as exc:
        return [], str(exc)


def ensure_insert_options_loaded(
    client: ApiClient,
    force_refresh: bool = False,
    table_id: str | None = None,
    view_id: str | None = None,
    adopt_active_selection: bool = True,
) -> dict[str, Any] | None:
    requested_table_id = table_id
    requested_view_id = view_id

    if requested_table_id is None and requested_view_id is None:
        active_table = get_active_table_settings()
        if active_table is not None:
            requested_table_id = active_table.get("tableId", "").strip() or None
            requested_view_id = active_table.get("viewId", "").strip() or None

    cache_key = "__default__"
    if requested_table_id:
        cache_key = make_table_cache_key(requested_table_id, requested_view_id or "")

    if not force_refresh and cache_key in st.session_state.insert_options_catalog:
        cached = st.session_state.insert_options_catalog[cache_key]
        st.session_state.insert_options_cache = cached
        st.session_state.insert_options_cache_key = cache_key
        st.session_state.insert_options_error = ""
        return cached

    try:
        response = client.get_insert_options(requested_table_id, requested_view_id)
        merge_table_presets(response.get("tablePresets", []))
        response_key = make_table_cache_key(response.get("tableId", ""), response.get("viewId", ""))
        st.session_state.insert_options_catalog[response_key] = response
        st.session_state.insert_options_cache = response
        st.session_state.insert_options_cache_key = response_key
        st.session_state.insert_options_error = ""
        if adopt_active_selection:
            set_active_table_from_response(response)
        return response
    except ApiClientError as exc:
        if requested_table_id is None and requested_view_id is None:
            st.session_state.insert_options_cache = None
        st.session_state.insert_options_error = str(exc)
        return None

def has_unsaved_local_changes() -> bool:
    snapshot = st.session_state.loaded_page_snapshot or {}
    return (
        st.session_state.editor_title != snapshot.get("title", "")
        or st.session_state.editor_content != snapshot.get("content", "")
    )


def persist_page(client: ApiClient, *, auto: bool = False) -> bool:
    title = st.session_state.editor_title.strip()
    content = st.session_state.editor_content
    if not title:
        if not auto:
            st.session_state.last_error = "Заголовок не должен быть пустым."
        return False
    if auto and not content.strip():
        return False
    try:
        if st.session_state.selected_page_id:
            saved = client.update_page(st.session_state.selected_page_id, title, content)
            if not auto:
                st.session_state.last_success = "Страница обновлена."
        else:
            saved = client.create_page(title, content)
            if not auto:
                st.session_state.last_success = "Страница создана."
        load_page(saved)
        if auto:
            st.session_state.worker_note = "Черновик мягко сохранен в фоне."
        return True
    except ApiClientError as exc:
        if auto:
            st.session_state.worker_note = f"Автосохранение пропустили: {exc}"
        else:
            st.session_state.last_error = str(exc)
        return False


def refresh_preview(client: ApiClient, *, auto: bool = False) -> bool:
    content = st.session_state.editor_content
    if auto and content == st.session_state.last_preview_source:
        return False
    try:
        st.session_state.preview_html = client.render_content(content)
        st.session_state.last_preview_source = content
        st.session_state.worker_note = "Живой просмотр обновлен без лишних кликов." if auto else st.session_state.worker_note
        if not auto:
            st.session_state.last_success = "Предпросмотр обновлен."
        return True
    except ApiClientError as exc:
        if auto:
            st.session_state.worker_note = f"Автопредпросмотр пока пропущен: {exc}"
        else:
            st.session_state.last_error = str(exc)
        return False


def sync_selected_page_if_needed(client: ApiClient) -> bool:
    if not st.session_state.selected_page_id:
        return False
    try:
        server_page = client.get_page(st.session_state.selected_page_id)
    except ApiClientError as exc:
        st.session_state.worker_note = f"Live sync пропущен: {exc}"
        return False
    snapshot = st.session_state.loaded_page_snapshot or {}
    current_updated_at = snapshot.get("updatedAt", "")
    server_updated_at = server_page.get("updatedAt", "")
    if server_updated_at and server_updated_at != current_updated_at:
        if has_unsaved_local_changes():
            st.session_state.last_live_sync_at = "локальные правки важнее"
            st.session_state.worker_note = "На сервере есть новая версия, но твои локальные правки не перезаписаны."
            return False
        load_page(server_page)
        st.session_state.last_live_sync_at = server_updated_at
        st.session_state.worker_note = "Открытая страница подтянула свежую версию с сервера."
        return True
    st.session_state.last_live_sync_at = server_updated_at or "проверено"
    return False


def render_background_worker(client: ApiClient) -> None:
    @st.fragment(run_every=1)
    def worker_fragment() -> None:
        now = time.time()
        dirty = st.session_state.editor_dirty
        performed_action = False
        if dirty:
            idle_for = now - st.session_state.editor_dirty_at
            title = st.session_state.editor_title.strip()
            content = st.session_state.editor_content
            can_autosave = bool(title) and (bool(st.session_state.selected_page_id) or bool(content.strip()))
            pending_save = (
                st.session_state.autosave_enabled
                and can_autosave
                and (title != st.session_state.last_saved_title or content != st.session_state.last_saved_source)
            )
            pending_preview = st.session_state.auto_preview_enabled and content != st.session_state.last_preview_source
            if pending_save and idle_for >= AUTO_SAVE_DELAY_SECONDS:
                performed_action = persist_page(client, auto=True)
            elif pending_preview and idle_for >= AUTO_PREVIEW_DELAY_SECONDS:
                performed_action = refresh_preview(client, auto=True)
        elif st.session_state.live_updates_enabled and st.session_state.selected_page_id:
            if now - st.session_state.last_remote_sync_epoch >= st.session_state.live_refresh_seconds:
                st.session_state.last_remote_sync_epoch = now
                performed_action = sync_selected_page_if_needed(client)
        st.caption(st.session_state.worker_note)
        if performed_action:
            st.rerun()
    worker_fragment()


def render_preview_panel() -> None:
    preview_html = st.session_state.preview_html.strip()
    if preview_html:
        st.markdown(f'<div class="preview-shell">{preview_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div class="preview-shell">
                <strong>Живой HTML пока пуст.</strong><br/>
                Как только ты сделаешь паузу в наборе, backend сам обновит этот блок.
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_source_snapshot_html(
    insert_options: dict[str, Any],
    selected_record_id: str,
    selected_field_name: str,
) -> str:
    records = insert_options.get("records", [])
    field_names = insert_options.get("fieldNames", [])
    if not records or not field_names:
        return ""

    visible_fields: list[str] = []
    if selected_field_name and selected_field_name in field_names:
        visible_fields.append(selected_field_name)
    for field_name in field_names:
        if field_name not in visible_fields:
            visible_fields.append(field_name)
        if len(visible_fields) >= 4:
            break

    header_html = "".join(
        f'<th style="padding:0.6rem 0.7rem; text-align:left; color:#5b5148; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.06em; border-bottom:1px solid rgba(92,72,56,0.12);">{escape(field_name)}</th>'
        for field_name in visible_fields
    )

    row_html: list[str] = []
    for record in records[:6]:
        row_id = record.get("recordId", "")
        row_background = "rgba(47,126,105,0.10)" if row_id == selected_record_id else "rgba(255,255,255,0.76)"
        cells = []
        for field_name in visible_fields:
            value = str(record.get("fields", {}).get(field_name, "—"))
            cell_background = "rgba(187,90,50,0.10)" if row_id == selected_record_id and field_name == selected_field_name else "transparent"
            cells.append(
                f'<td style="padding:0.68rem 0.7rem; border-bottom:1px solid rgba(92,72,56,0.08); background:{cell_background}; vertical-align:top;">{escape(value)}</td>'
            )
        row_html.append(
            f'<tr style="background:{row_background};"><td style="padding:0.68rem 0.7rem; border-bottom:1px solid rgba(92,72,56,0.08); font-family:IBM Plex Mono, monospace; color:#5b5148;">{escape(row_id)}</td>{"".join(cells)}</tr>'
        )

    return (
        '<div style="border:1px solid rgba(92,72,56,0.12); border-radius:18px; overflow:hidden; background:rgba(255,255,255,0.88);">'
        '<table style="width:100%; border-collapse:collapse; font-size:0.9rem; color:#2b241d;">'
        '<thead><tr>'
        '<th style="padding:0.6rem 0.7rem; text-align:left; color:#5b5148; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.06em; border-bottom:1px solid rgba(92,72,56,0.12);">Record</th>'
        f'{header_html}'
        '</tr></thead>'
        f'<tbody>{"".join(row_html)}</tbody>'
        '</table></div>'
    )


def render_insert_builder(client: ApiClient) -> None:
    presets = get_saved_table_presets()
    selector_options = [preset["key"] for preset in presets]
    if "custom" not in selector_options:
        selector_options.append("custom")
    if not st.session_state.active_table_key and selector_options:
        st.session_state.active_table_key = selector_options[0]

    def format_table_option(option_key: str) -> str:
        if option_key == "custom":
            return "Подключить другую таблицу"
        for preset in presets:
            if preset.get("key") == option_key:
                return preset.get("label", option_key)
        return option_key

    st.selectbox(
        "Активная таблица",
        options=selector_options,
        key="active_table_key",
        format_func=format_table_option,
        help="Сначала выбираем источник данных, затем точную строку и поле. Так вставка становится осмысленной, а не технической.",
    )

    options: dict[str, Any] | None = None
    if st.session_state.active_table_key == "custom":
        st.text_input("Название в интерфейсе", key="custom_table_label", placeholder="Например, Проекты / KPI")
        st.text_input("Table ID", key="custom_table_id", placeholder="dst...")
        st.text_input("View ID", key="custom_view_id", placeholder="viw... (можно оставить пустым)")
        custom_cols = st.columns(2)
        if custom_cols[0].button("Подключить таблицу", key="connect-custom-table", use_container_width=True):
            if not st.session_state.custom_table_id.strip():
                st.session_state.last_error = "Сначала укажи Table ID для пользовательской таблицы."
                st.rerun()
            options = ensure_insert_options_loaded(
                client,
                force_refresh=True,
                table_id=st.session_state.custom_table_id.strip(),
                view_id=st.session_state.custom_view_id.strip() or None,
            )
            if options is not None:
                st.session_state.last_success = "Пользовательская таблица подключена."
                st.rerun()
        if custom_cols[1].button("Сохранить в быстрый доступ", key="save-custom-table", use_container_width=True):
            normalized = normalize_table_preset(
                {
                    "key": make_table_cache_key(st.session_state.custom_table_id, st.session_state.custom_view_id),
                    "label": st.session_state.custom_table_label or st.session_state.custom_table_id,
                    "tableId": st.session_state.custom_table_id,
                    "viewId": st.session_state.custom_view_id,
                    "role": "custom",
                }
            )
            if normalized is None:
                st.session_state.last_error = "Нельзя сохранить пустую таблицу. Укажи хотя бы Table ID."
            else:
                merge_table_presets([normalized])
                st.session_state.active_table_key = normalized["key"]
                st.session_state.last_success = "Таблица добавлена в быстрый доступ."
            st.rerun()

        custom_cache_key = make_table_cache_key(st.session_state.custom_table_id, st.session_state.custom_view_id)
        if custom_cache_key in st.session_state.insert_options_catalog:
            options = st.session_state.insert_options_catalog[custom_cache_key]
        elif st.session_state.custom_table_id.strip():
            st.info("Таблица указана, но еще не подключена. Нажми «Подключить таблицу», чтобы увидеть строки и поля.")
            return
        else:
            st.info("Здесь можно вручную подключить любую MWS-таблицу по `tableId` и `viewId`, а затем выбрать конкретную ячейку.")
            return
    else:
        options = ensure_insert_options_loaded(client)

    if st.session_state.insert_options_error:
        st.error(st.session_state.insert_options_error)
        return
    if options is None:
        st.info("Сначала выбери или подключи таблицу, из которой будем брать данные.")
        return

    active_info = options.get("activeTable", {})
    table_label = active_info.get("label") or options.get("tableId", "Таблица")
    table_id = options.get("tableId", "")
    view_id = options.get("viewId", "")
    records = options.get("records", [])
    field_names = options.get("fieldNames", [])

    st.markdown(
        f"""
        <div class="formula-card">
            <div class="formula-title">
                <span class="formula-index">T</span>
                <span class="formula-field">{escape(str(table_label))}</span>
            </div>
            <div class="note-chip-row">
                <span class="note-chip">Table: {escape(str(table_id))}</span>
                <span class="note-chip">View: {escape(str(view_id or 'без view'))}</span>
                <span class="note-chip">Строк: {len(records)}</span>
                <span class="note-chip">Полей: {len(field_names)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not records or not field_names:
        st.info("У выбранной таблицы пока нет доступных строк или полей. Попробуй обновить источник или проверить view.")
        return

    widget_suffix = st.session_state.insert_options_cache_key or make_table_cache_key(table_id, view_id)
    selected_record_index = st.selectbox(
        "Строка",
        options=list(range(len(records))),
        format_func=lambda index: build_record_label(records[index]),
        key=f"insert-record-index-{widget_suffix}",
        help="Это конкретная запись, из которой будет взято значение.",
    )
    selected_record = records[selected_record_index]
    record_fields = selected_record.get("fields", {})
    sorted_fields = sorted(field_names, key=lambda field_name: (field_name not in record_fields, field_name.lower()))
    selected_field = st.selectbox(
        "Поле / ячейка",
        options=sorted_fields,
        key=f"insert-field-name-{widget_suffix}",
        help="После выбора поля ниже сразу покажется живое значение этой ячейки.",
    )

    selected_value = str(record_fields.get(selected_field, "—"))
    st.markdown(
        f"""
        <div class="formula-card">
            <div class="formula-title">
                <span class="formula-index">#</span>
                <span class="formula-field">Предпросмотр выбранной ячейки</span>
            </div>
            <div class="formula-help">Сначала смотришь реальное значение, только потом вставляешь его в документ.</div>
            <div class="note-chip-row">
                <span class="note-chip">Record: {escape(str(selected_record.get('recordId', 'record')))}</span>
                <span class="note-chip">Поле: {escape(str(selected_field))}</span>
            </div>
            <div style="padding:0.95rem 1rem; border-radius:18px; background:rgba(187,90,50,0.08); border:1px solid rgba(187,90,50,0.14); color:#3a2b20; font-family:'Source Serif 4', serif; font-size:1.05rem; line-height:1.7;">{escape(selected_value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(build_source_snapshot_html(options, selected_record.get("recordId", ""), selected_field), unsafe_allow_html=True)

    token = build_formula_token(table_id, selected_record.get("recordId", "recordId"), selected_field)
    with st.expander("Техническая формула под капотом", expanded=False):
        st.code(token, language="text")

    helper_cols = st.columns(2)
    if helper_cols[0].button("Вставить в курс документа", key=f"insert-token-inline-{widget_suffix}", use_container_width=True):
        insert_text_snippet(token, new_line=False)
        st.session_state.last_success = "Ячейка вставлена в документ как живая привязка."
        st.rerun()
    if helper_cols[1].button("Вставить отдельным блоком", key=f"insert-token-block-{widget_suffix}", use_container_width=True):
        insert_text_snippet(token, new_line=True)
        st.session_state.last_success = "Ячейка добавлена отдельным блоком."
        st.rerun()


def render_formula_studio(client: ApiClient) -> None:
    tokens = extract_formula_tokens(st.session_state.editor_content)
    if not tokens:
        st.info("В тексте пока нет живых формул. Добавить их можно через конструктор над документом.")
        return

    options_by_table: dict[str, dict[str, Any] | None] = {}
    for token in tokens:
        if token.table_id not in options_by_table:
            cached = get_cached_insert_options_for_table(token.table_id)
            if cached is None:
                cached = ensure_insert_options_loaded(client, table_id=token.table_id, adopt_active_selection=False)
            options_by_table[token.table_id] = cached

    for token in tokens:
        token_options = options_by_table.get(token.table_id)
        label, preview_value = describe_formula(token, st.session_state.insert_options_catalog)
        st.markdown(
            f"""
            <div class="formula-card">
                <div class="formula-title">
                    <span class="formula-index">{token.index + 1}</span>
                    <span class="formula-field">{escape(label)}</span>
                </div>
                <div class="formula-help">Формула уже живет в тексте. Здесь можно переназначить точную запись и поле без ручного редактирования идентификаторов.</div>
                <div class="note-chip-row">
                    <span class="note-chip">Таблица: {escape(token.table_id)}</span>
                    <span class="note-chip">Значение: {escape(preview_value)}</span>
                    <span class="note-chip">Record: {escape(token.record_id)}</span>
                </div>
                <div class="formula-raw">{escape(token.raw)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if token_options is None:
            st.info("Для этой формулы таблица еще не загружена. Открой ее через конструктор вставки, и студия сможет показать точные записи и поля.")
            continue

        records = token_options.get("records", [])
        field_names = token_options.get("fieldNames", [])
        if not records or not field_names:
            st.info("У этой формулы источник пока не отдает строки или поля. Проверь выбранную таблицу и ее view.")
            continue

        matching_record_index = next((index for index, record in enumerate(records) if record.get("recordId") == token.record_id), 0)
        popover_key = f"formula-{token.index}-{token.table_id}"
        with st.popover(f"Настроить формулу #{token.index + 1}", use_container_width=True):
            selected_record_index = st.selectbox(
                "Запись",
                options=list(range(len(records))),
                index=matching_record_index,
                format_func=lambda index: build_record_label(records[index]),
                key=f"{popover_key}-record",
            )
            selected_record = records[selected_record_index]
            record_fields = selected_record.get("fields", {})
            sorted_fields = sorted(field_names, key=lambda field_name: (field_name not in record_fields, field_name.lower()))
            selected_field = st.selectbox(
                "Поле",
                options=sorted_fields,
                index=sorted_fields.index(token.field_name) if token.field_name in sorted_fields else 0,
                key=f"{popover_key}-field",
            )
            st.markdown(build_source_snapshot_html(token_options, selected_record.get("recordId", ""), selected_field), unsafe_allow_html=True)
            rebuilt_token = build_formula_token(token_options.get("tableId", token.table_id), selected_record.get("recordId", token.record_id), selected_field)
            st.code(rebuilt_token, language="text")
            cols = st.columns(2)
            if cols[0].button("Применить", key=f"{popover_key}-apply", use_container_width=True):
                st.session_state.editor_content = replace_formula_token(st.session_state.editor_content, token.index, rebuilt_token)
                mark_editor_dirty()
                st.session_state.last_success = f"Формула #{token.index + 1} обновлена."
                st.rerun()
            if cols[1].button("Удалить", key=f"{popover_key}-remove", use_container_width=True):
                st.session_state.editor_content = replace_formula_token(st.session_state.editor_content, token.index, "")
                mark_editor_dirty()
                st.session_state.last_success = f"Формула #{token.index + 1} удалена из текста."
                st.rerun()

def render_ai_panel(client: ApiClient) -> None:
    st.text_input("Что нужно вставить", key="ai_prompt", placeholder="Например, вставь статус проекта")
    if st.button("Подобрать живое поле", use_container_width=True):
        prompt = st.session_state.ai_prompt.strip()
        if not prompt:
            st.session_state.last_error = "Сначала опиши, что именно нужно вставить."
        else:
            try:
                st.session_state.ai_candidates = client.suggest_insert(user_prompt=prompt, page_content=st.session_state.editor_content)
                if st.session_state.ai_candidates:
                    st.session_state.last_success = "AI собрал кандидатов для вставки."
                else:
                    st.session_state.last_error = "AI не нашел подходящих вставок."
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
        st.rerun()
    if st.session_state.ai_candidates:
        for index, candidate in enumerate(st.session_state.ai_candidates):
            st.markdown(
                f"""
                <div class="formula-card">
                    <div class="formula-title">
                        <span class="formula-index">{index + 1}</span>
                        <span class="formula-field">{candidate.get('fieldName', 'Поле')}</span>
                    </div>
                    <div class="formula-help">{candidate.get('reason', 'Без пояснения')}</div>
                    <div class="note-chip-row"><span class="note-chip">Уверенность: {candidate.get('confidence', 0):.2f}</span></div>
                    <div class="formula-raw">{candidate.get('insert', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Вставить в документ", key=f"insert-candidate-{index}", use_container_width=True):
                insert_candidate(candidate.get("insert", ""))
                st.rerun()
    else:
        st.info("AI-панель ждет запроса. Она помогает именно с подбором живых полей, а не заменяет весь документ.")


def main() -> None:
    st.set_page_config(page_title="WikiLive", page_icon="W", layout="wide", initial_sidebar_state="expanded")
    inject_styles()
    ensure_state()
    client = build_client()
    backend_ok, backend_message = backend_status(client)
    pages, pages_error = fetch_pages(client)
    ensure_insert_options_loaded(client)

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">WikiLive / Document Studio</div>
            <div class="hero-title">Документ, который живет вместе с таблицей</div>
            <p class="hero-text">
                Слева ты пишешь человеческий текст, сверху видишь красивый лист документа, справа следишь за живым HTML и редактируешь привязанные поля.
                Формулы остаются техническим слоем под капотом, а основной режим становится ближе к нормальному редактору, чем к админке.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Навигация")
        status_class = "ok" if backend_ok else "fail"
        st.markdown(f'<div class="status-pill {status_class}">{"ONLINE" if backend_ok else "OFFLINE"} · {backend_message}</div>', unsafe_allow_html=True)
        st.caption(f"Backend: `{DEFAULT_BACKEND_URL}`")
        st.toggle("Live sync страницы", key="live_updates_enabled")
        st.toggle("Автопредпросмотр", key="auto_preview_enabled")
        st.toggle("Автосохранение", key="autosave_enabled")
        st.slider("Проверка обновлений, сек", min_value=2, max_value=15, key="live_refresh_seconds")
        if st.button("Обновить страницы", use_container_width=True):
            st.rerun()
        if st.button("Новая страница", use_container_width=True):
            reset_editor()
            st.session_state.last_success = "Открыт новый черновик."
            st.rerun()
        st.markdown("### Страницы")
        if pages_error is not None:
            st.error(pages_error)
        elif not pages:
            st.info("Пока нет ни одной страницы. Можно начать с чистого черновика справа.")
        else:
            for index, page in enumerate(pages):
                label = page.get("title") or f"Без названия #{index + 1}"
                is_active = page.get("pageId") == st.session_state.selected_page_id
                button_label = label if not is_active else f"● {label}"
                if st.button(button_label, key=f"page-btn-{page['pageId']}", use_container_width=True):
                    try:
                        load_page(client.get_page(page["pageId"]))
                        st.session_state.last_success = f"Страница «{label}» загружена."
                    except ApiClientError as exc:
                        st.session_state.last_error = str(exc)
                    st.rerun()
        st.markdown("---")
        st.markdown('<div class="sidebar-note">Веб-интерфейс остается главным, но эту же схему потом можно завернуть в desktop-оболочку без переписывания backend.</div>', unsafe_allow_html=True)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        st.session_state.last_error = ""
    if st.session_state.last_success:
        st.success(st.session_state.last_success)
        st.session_state.last_success = ""

    formula_count = len(extract_formula_tokens(st.session_state.editor_content))
    word_count = count_words(st.session_state.editor_content)
    selected_label = st.session_state.editor_title or "Новый черновик"
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="metric-label">Текущий документ</div><div class="metric-value serif">{selected_label}</div></div>
            <div class="metric-card"><div class="metric-label">Живые формулы</div><div class="metric-value">{formula_count}</div></div>
            <div class="metric-card"><div class="metric-label">Слов в тексте</div><div class="metric-value">{word_count}</div></div>
            <div class="metric-card"><div class="metric-label">Страниц в системе</div><div class="metric-value">{len(pages)}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    active_table = get_active_table_settings()
    if active_table is not None:
        st.markdown(
            f"""
            <div class="glass-card" style="padding:0.85rem 1rem; margin-top:-0.15rem; margin-bottom:1rem;">
                <div class="section-title">Активный источник живых данных</div>
                <div class="note-chip-row">
                    <span class="note-chip">{escape(active_table.get('label', 'Таблица'))}</span>
                    <span class="note-chip">Table: {escape(active_table.get('tableId', ''))}</span>
                    <span class="note-chip">View: {escape(active_table.get('viewId', '') or 'без view')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    render_background_worker(client)

    main_col, rail_col = st.columns([1.8, 1.0], gap="large")
    with main_col:
        st.markdown(
            """
            <div class="toolbar-card">
                <div class="section-title">Панель набора</div>
                <div class="section-subtitle">
                    Документ можно писать обычным текстом, а живые формулы собирать визуально и редактировать уже без ручного копания в идентификаторах.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        toolbar_col1, toolbar_col2, toolbar_col3, toolbar_col4, toolbar_col5 = st.columns([1.45, 1.0, 0.75, 0.75, 0.75])
        with toolbar_col1:
            with st.popover("Выбрать ячейку из таблицы", use_container_width=True):
                render_insert_builder(client)
        with toolbar_col2:
            if st.button("Обновить активную таблицу", use_container_width=True):
                ensure_insert_options_loaded(client, force_refresh=True)
                st.session_state.last_error = st.session_state.insert_options_error if st.session_state.insert_options_error else ""
                st.session_state.last_success = "Активная таблица перечитана." if not st.session_state.insert_options_error else ""
                st.rerun()
        with toolbar_col3:
            if st.button("## Раздел", use_container_width=True):
                insert_text_snippet("## Новый раздел")
                st.session_state.last_success = "Добавлен шаблон заголовка раздела."
                st.rerun()
        with toolbar_col4:
            if st.button("> Акцент", use_container_width=True):
                insert_text_snippet("> Важное замечание")
                st.session_state.last_success = "Добавлен акцентный блок."
                st.rerun()
        with toolbar_col5:
            if st.button("Линия", use_container_width=True):
                insert_text_snippet("---")
                st.session_state.last_success = "Добавлен разделитель."
                st.rerun()
        st.markdown('<div class="writer-shell">', unsafe_allow_html=True)
        st.markdown(f'<div class="paper-sheet"><div class="paper-heading">{selected_label}</div><div class="paper-meta">Это локальный читабельный слой: формулы показаны как живые карточки, а не как сырые идентификаторы.</div>{render_document_html(st.session_state.editor_content, st.session_state.insert_options_catalog)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.text_input("Заголовок", key="editor_title", placeholder="Например, Статус релиза или Операционная сводка", on_change=mark_editor_dirty)
        st.text_area("Текст документа", key="editor_content", height=760, placeholder="Пиши свободный текст. Формулы можно вставлять через конструктор, а сверху ты всегда видишь более человечную версию листа.", on_change=mark_editor_dirty)
        st.caption("После короткой паузы предпросмотр обновится сам. Автосохранение не перетирает локальные правки и не дергает сервер на каждом символе.")
        action_col1, action_col2, action_col3, action_col4 = st.columns([1.15, 1.15, 1.2, 1.0])
        if action_col1.button("Сохранить сейчас", use_container_width=True, type="primary"):
            persist_page(client, auto=False)
            st.rerun()
        if action_col2.button("Обновить живой HTML", use_container_width=True):
            refresh_preview(client, auto=False)
            st.rerun()
        if action_col3.button("Перечитать страницу", use_container_width=True, disabled=not st.session_state.selected_page_id):
            try:
                load_page(client.get_page(st.session_state.selected_page_id))
                st.session_state.last_success = "Страница перечитана с сервера."
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
            st.rerun()
        if action_col4.button("Удалить", use_container_width=True, disabled=not st.session_state.selected_page_id):
            try:
                client.delete_page(st.session_state.selected_page_id)
                reset_editor()
                st.session_state.last_success = "Страница удалена."
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
            st.rerun()
    with rail_col:
        preview_tab, formula_tab, ai_tab = st.tabs(["Живой HTML", "Студия формул", "AI"])
        with preview_tab:
            st.markdown('<div class="glass-card"><div class="section-title">Автообновляемый предпросмотр</div><div class="section-subtitle">Здесь уже показан реальный HTML от backend. Он нужен как честная проверка того, что увидит пользователь после рендера из MWS.</div></div>', unsafe_allow_html=True)
            render_preview_panel()
        with formula_tab:
            st.markdown('<div class="glass-card"><div class="section-title">Связанные живые поля</div><div class="section-subtitle">Формулы живут внутри текста, но управлять ими удобнее здесь: можно быстро пересобрать запись, поле или удалить привязку совсем.</div></div>', unsafe_allow_html=True)
            render_formula_studio(client)
        with ai_tab:
            st.markdown('<div class="glass-card"><div class="section-title">AI-помощник</div><div class="section-subtitle">Ассистент не пишет документ вместо тебя, а помогает найти правильную живую вставку по смыслу запроса.</div></div>', unsafe_allow_html=True)
            render_ai_panel(client)


if __name__ == "__main__":
    main()











