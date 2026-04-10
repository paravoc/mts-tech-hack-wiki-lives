from __future__ import annotations

import json
import os
from html import escape
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from utils.api_client import ApiClient, ApiClientError
from utils.editor_shell import PAGE_BREAK_MARKER, render_editor_shell
from utils.document_tools import build_formula_token, count_words, describe_formula, extract_formula_tokens, render_document_html

URL = os.getenv("WIKILIVE_BACKEND_URL", "http://127.0.0.1:3000")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Onest:wght@400;500;700&display=swap');
        :root {
            --mts-red: #e30613;
            --mts-red-dark: #bf0812;
            --bg: #f6f7f9;
            --paper: #ffffff;
            --ink: #14171c;
            --muted: #7a828e;
            --line: rgba(20, 23, 28, 0.08);
            --soft: rgba(227, 6, 19, 0.07);
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(227, 6, 19, 0.10), transparent 20%),
                linear-gradient(180deg, #fafbfc 0%, #f1f3f6 100%);
            color: var(--ink);
            font-family: 'Manrope', sans-serif;
        }
        .block-container {
            max-width: 1120px;
            padding-top: 0.7rem;
            padding-bottom: 0.8rem;
        }
        div[data-testid="stTextArea"] {
            position: absolute !important;
            left: -10000px !important;
            top: 0 !important;
            width: 1px !important;
            height: 1px !important;
            opacity: 0 !important;
            pointer-events: none !important;
            overflow: hidden !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .stApp > header {
            display: none !important;
        }
        #MainMenu, footer {
            visibility: hidden !important;
        }
        [data-testid="stSidebar"] { display: none; }
        .toolbar {
            display: flex;
            gap: 0.6rem;
            align-items: center;
            margin-bottom: 0.75rem;
            padding: 0.22rem;
            border: 1px solid var(--line);
            border-radius: 20px;
            background: rgba(255,255,255,0.84);
            backdrop-filter: blur(14px);
            box-shadow: 0 14px 32px rgba(20, 23, 28, 0.06);
            animation: slideIn .45s cubic-bezier(.22,1,.36,1);
        }
        .sheet {
            position: relative;
            border: 1px solid var(--line);
            border-radius: 32px;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.96)),
                repeating-linear-gradient(180deg, transparent 0, transparent 35px, rgba(227, 6, 19, 0.05) 35px, rgba(227, 6, 19, 0.05) 36px);
            min-height: 260px;
            padding: 1.2rem 1.35rem 1.35rem;
            box-shadow: 0 22px 54px rgba(20, 23, 28, 0.07);
            animation: rise .55s cubic-bezier(.22,1,.36,1);
        }
        .editor-shell {
            position: relative;
            overflow: hidden;
        }
        .title-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.85rem;
        }
        .sheet-title {
            font-family: 'Onest', sans-serif;
            font-size: 1.2rem;
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }
        .panel {
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(255,255,255,0.92);
            padding: 0.85rem 0.95rem;
        }
        .value-box {
            border-radius: 18px;
            border: 1px solid rgba(227, 6, 19, 0.10);
            background: linear-gradient(180deg, rgba(227, 6, 19, 0.07), rgba(227, 6, 19, 0.04));
            padding: 0.9rem 1rem;
            line-height: 1.65;
            word-break: break-word;
        }
        .tiny {
            color: var(--muted);
            font-size: 0.76rem;
            line-height: 1.45;
        }
        .raw {
            font-family: Consolas, monospace;
            font-size: 0.75rem;
            color: var(--muted);
            margin-top: 0.45rem;
            word-break: break-word;
        }
        .formula {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.75rem 0.85rem;
            background: rgba(255,255,255,0.88);
            margin-top: 0.55rem;
            transition: transform .28s cubic-bezier(.22,1,.36,1), border-color .28s ease, background .28s ease;
        }
        .formula:hover {
            transform: translateY(-1px);
            border-color: rgba(227, 6, 19, 0.15);
            background: rgba(255,255,255,0.98);
        }
        .formula strong {
            display: block;
            margin-bottom: 0.22rem;
        }
        .doc-heading { font-family: 'Onest', sans-serif; }
        .doc-paragraph { line-height: 1.9; }
        .doc-callout {
            border-left: 4px solid var(--mts-red);
            background: rgba(227, 6, 19, 0.06);
            border-radius: 0 18px 18px 0;
            padding: 0.75rem 0.95rem;
        }
        .doc-divider {
            height: 1px;
            margin: 1rem 0;
            background: linear-gradient(90deg, rgba(227,6,19,0), rgba(227,6,19,.35), rgba(227,6,19,0));
        }
        .doc-formula-chip {
            display: inline-flex;
            gap: 0.35rem;
            align-items: center;
            padding: 0.18rem 0.46rem;
            border-radius: 999px;
            background: rgba(227, 6, 19, 0.08);
            border: 1px solid rgba(227, 6, 19, 0.10);
        }
        .doc-formula-chip__index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.3rem;
            height: 1.3rem;
            border-radius: 999px;
            background: #fff;
            color: var(--mts-red);
            font-size: 0.72rem;
            font-weight: 800;
        }
        .doc-formula-chip__label, .doc-formula-chip__value { font-size: 0.78rem; }
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
            background: rgba(255,255,255,0.97) !important;
            border: 1px solid var(--line) !important;
            border-radius: 20px !important;
            box-shadow: none !important;
            color: #14171c !important;
            -webkit-text-fill-color: #14171c !important;
        }
        div[data-testid="stTextArea"] textarea {
            min-height: 72vh !important;
            line-height: 1.8 !important;
            border-radius: 28px !important;
            padding: 1.25rem 1.3rem !important;
            caret-color: var(--mts-red) !important;
            transition: border-color .18s ease, box-shadow .18s ease !important;
            color: #14171c !important;
            -webkit-text-fill-color: #14171c !important;
        }
        div[data-testid="stTextArea"] textarea[data-wikilive-visual="true"] {
            position: relative !important;
            z-index: 2 !important;
            color: transparent !important;
            -webkit-text-fill-color: transparent !important;
            background: transparent !important;
            text-shadow: none !important;
        }
        div[data-testid="stTextArea"] textarea[data-wikilive-visual="true"]::selection {
            background: rgba(227, 6, 19, 0.14) !important;
            color: transparent !important;
            -webkit-text-fill-color: transparent !important;
        }
        div[data-testid="stTextInput"] input {
            color: #14171c !important;
            -webkit-text-fill-color: #14171c !important;
        }
        div[data-testid="stTextArea"] textarea:focus {
            border-color: rgba(227, 6, 19, 0.22) !important;
            box-shadow: 0 0 0 3px rgba(227, 6, 19, 0.06) !important;
        }
        button[data-baseweb="button"], .stButton > button, div[data-testid="stPopover"] > button, [data-testid="stPopoverButton"] > button, [data-testid^="stBaseButton"] {
            min-height: 2.55rem !important;
            border-radius: 18px !important;
            font-weight: 800 !important;
            border: 1px solid rgba(227, 6, 19, 0.28) !important;
            background: #ffffff !important;
            color: #1a1d22 !important;
            box-shadow: none !important;
            transition: transform .24s cubic-bezier(.22,1,.36,1), border-color .24s ease, background .24s ease, box-shadow .24s ease !important;
        }
        .toolbar button[data-baseweb="button"], .toolbar .stButton > button, .toolbar div[data-testid="stPopover"] > button, .toolbar [data-testid="stPopoverButton"] > button, .toolbar [data-testid^="stBaseButton"] {
            min-height: 2.35rem !important;
            padding-top: 0.2rem !important;
            padding-bottom: 0.2rem !important;
        }
        button[data-baseweb="button"] *,
        .stButton > button *,
        div[data-testid="stPopover"] > button *,
        [data-testid="stPopoverButton"] > button *,
        [data-testid^="stBaseButton"] * {
            color: inherit !important;
            fill: currentColor !important;
        }
        button[data-baseweb="button"]:hover, .stButton > button:hover, div[data-testid="stPopover"] > button:hover, [data-testid="stPopoverButton"] > button:hover, [data-testid^="stBaseButton"]:hover {
            transform: translateY(-1px);
            border-color: rgba(227, 6, 19, 0.55) !important;
            background: #ffffff !important;
            box-shadow: 0 10px 24px rgba(227, 6, 19, 0.08) !important;
        }
        .stButton button[kind="primary"] {
            background: #ffffff !important;
            color: var(--mts-red) !important;
            border: 1px solid rgba(227, 6, 19, 0.5) !important;
            box-shadow: 0 10px 22px rgba(227, 6, 19, 0.06) !important;
        }
        label[data-testid="stWidgetLabel"] {
            color: #323844 !important;
            font-weight: 700 !important;
        }
        div[data-testid="stTextInputRootElement"] > div,
        div[data-testid="stTextArea"] > div {
            border: 1px solid rgba(227, 6, 19, 0.18) !important;
            border-radius: 24px !important;
            box-shadow: none !important;
            background: #ffffff !important;
        }
        div[data-testid="stDataFrame"] * {
            color: #14171c !important;
        }
        div[data-testid="stDataFrame"] [role="gridcell"],
        div[data-testid="stDataFrame"] [role="columnheader"],
        div[data-testid="stDataFrame"] [role="rowheader"] {
            background: #ffffff !important;
            color: #14171c !important;
        }
        div[data-testid="stDataFrame"] [aria-selected="true"] {
            background: rgba(227, 6, 19, 0.12) !important;
        }
        .wikilive-visual-editor {
            position: absolute;
            inset: 0;
            z-index: 1;
            pointer-events: none;
            overflow: hidden;
            border-radius: 28px;
        }
        .wikilive-visual-editor__content {
            min-height: 72vh;
            padding: 1.25rem 1.3rem;
            line-height: 1.8;
            color: #14171c;
            white-space: normal;
            word-break: break-word;
        }
        .wikilive-visual-editor__line {
            min-height: 1.8em;
            white-space: pre-wrap;
        }
        .wikilive-visual-editor__line.h2 {
            font-family: 'Onest', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.45;
            margin: 0.2rem 0;
        }
        .wikilive-visual-editor__callout {
            border-left: 4px solid var(--mts-red);
            background: rgba(227, 6, 19, 0.06);
            border-radius: 0 18px 18px 0;
            padding: 0.55rem 0.8rem;
            margin: 0.25rem 0;
            white-space: pre-wrap;
        }
        .wikilive-visual-editor__table-wrap {
            margin: 0.45rem 0 0.7rem;
            overflow: auto;
            border: 1px solid rgba(20, 23, 28, 0.08);
            border-radius: 18px;
            background: #ffffff;
            pointer-events: auto;
            max-height: 18rem;
        }
        .wikilive-visual-editor__table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }
        .wikilive-visual-editor__table th,
        .wikilive-visual-editor__table td {
            padding: 0.72rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid rgba(20, 23, 28, 0.06);
            vertical-align: top;
        }
        .wikilive-visual-editor__table th {
            background: rgba(227, 6, 19, 0.05);
        }
        .wikilive-object {
            display: inline-flex;
            align-items: center;
            gap: 0.38rem;
            padding: 0.18rem 0.46rem;
            border-radius: 999px;
            background: rgba(227, 6, 19, 0.08);
            border: 1px solid rgba(227, 6, 19, 0.12);
            pointer-events: auto;
            cursor: pointer;
            transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
        }
        .wikilive-object:hover,
        .wikilive-object.is-active {
            transform: translateY(-1px);
            border-color: rgba(227, 6, 19, 0.35);
            box-shadow: 0 8px 18px rgba(227, 6, 19, 0.08);
        }
        .wikilive-object__index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 1.3rem;
            height: 1.3rem;
            border-radius: 999px;
            background: #ffffff;
            color: var(--mts-red);
            font-size: 0.72rem;
            font-weight: 800;
        }
        .wikilive-object__field {
            font-size: 0.78rem;
            font-weight: 800;
            color: #c10813;
        }
        .wikilive-object__value {
            font-size: 0.78rem;
            color: #4d5561;
            max-width: 14rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        @keyframes rise {
            from { opacity: 0; transform: translateY(14px) scale(.992); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_state() -> None:
    defaults: dict[str, Any] = {
        "selected_page_id": None,
        "editor_title": "",
        "editor_content": "",
        "preview_html": "",
        "last_error": "",
        "last_success": "",
        "presets": [],
        "catalog": {},
        "selected_table_keys": [],
        "active_table_key": "",
        "source_record_index": 0,
        "source_field_name": "",
        "page_search": "",
        "table_search": "",
        "active_panel": "",
        "insert_mode": "cells",
        "new_draft_id": 0,
        "latest_insert_snippet": "",
        "latest_insert_hint": "",
        "version_note": "",
        "comment_body": "",
        "comment_selection": "",
        "pages_cache": [],
        "pages_cache_loaded": False,
        "insert_row_limit": 100,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api() -> ApiClient:
    return ApiClient(URL)


def normalize_preset(preset: dict[str, Any]) -> dict[str, Any] | None:
    table_id = str(preset.get("tableId", "")).strip()
    if not table_id:
        return None
    view_id = str(preset.get("viewId", "")).strip()
    return {
        "key": str(preset.get("key", "")).strip() or f"{table_id}::{view_id}",
        "label": str(preset.get("label", "")).strip() or table_id,
        "tableId": table_id,
        "viewId": view_id,
    }


def merge_presets(items: list[dict[str, Any]] | None) -> None:
    if items is None:
        return
    merged = {
        preset["key"]: preset
        for preset in st.session_state.presets
        if isinstance(preset, dict) and preset.get("key")
    }
    for item in items:
        preset = normalize_preset(item)
        if preset is not None:
            merged[preset["key"]] = preset
    st.session_state.presets = list(merged.values())
    if not st.session_state.selected_table_keys and st.session_state.presets:
        first_key = st.session_state.presets[0]["key"]
        st.session_state.selected_table_keys = [first_key]
        st.session_state.active_table_key = first_key


def get_preset(key: str) -> dict[str, Any] | None:
    for preset in st.session_state.presets:
        if preset.get("key") == key:
            return preset
    return None


def fetch_insert_options(client: ApiClient, table_id: str | None = None, view_id: str | None = None, force: bool = False) -> dict[str, Any] | None:
    cache_key = "__default__" if not table_id else f"{table_id}::{view_id or ''}"
    if not force and cache_key in st.session_state.catalog:
        return st.session_state.catalog[cache_key]
    try:
        data = client.get_insert_options(table_id=table_id, view_id=view_id)
        merge_presets(data.get("tablePresets", []))
        st.session_state.catalog[f"{data.get('tableId', '')}::{data.get('viewId', '')}"] = data
        return data
    except ApiClientError as exc:
        st.session_state.last_error = str(exc)
        return None


def selected_presets() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key in st.session_state.selected_table_keys:
        preset = get_preset(key)
        if preset is not None:
            items.append(preset)
    return items


def selected_table_data(client: ApiClient) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for preset in selected_presets():
        data = fetch_insert_options(client, preset["tableId"], preset["viewId"] or None)
        if data is not None:
            output[preset["key"]] = data
    if output and st.session_state.active_table_key not in output:
        st.session_state.active_table_key = next(iter(output.keys()))
    return output


def active_table_payload(client: ApiClient) -> dict[str, Any] | None:
    presets = selected_presets()
    if not presets:
        return None
    allowed_keys = {preset["key"] for preset in presets}
    if st.session_state.active_table_key not in allowed_keys:
        st.session_state.active_table_key = presets[0]["key"]
    active_preset = get_preset(st.session_state.active_table_key)
    if active_preset is None:
        return None
    return fetch_insert_options(
        client,
        active_preset["tableId"],
        active_preset["viewId"] or None,
    )


def list_pages(client: ApiClient, force: bool = False) -> list[dict[str, Any]]:
    if not force and st.session_state.pages_cache_loaded:
        return list(st.session_state.pages_cache)
    try:
        pages = client.list_pages()
        st.session_state.pages_cache = pages
        st.session_state.pages_cache_loaded = True
        return pages
    except ApiClientError as exc:
        st.session_state.last_error = str(exc)
        return list(st.session_state.pages_cache)


def page_label(page: dict[str, Any]) -> str:
    return page.get("title") or page.get("pageId") or "Без названия"


def load_page(client: ApiClient, page_id: str) -> None:
    page = client.get_page(page_id)
    st.session_state.selected_page_id = page.get("pageId")
    st.session_state.editor_title = page.get("title", "")
    st.session_state.editor_content = page.get("content", "")
    st.session_state.preview_html = page.get("renderedHtml", "")


def save_page(client: ApiClient) -> None:
    content = st.session_state.editor_content
    title = st.session_state.editor_title.strip()
    if not title:
        for line in content.splitlines():
            if line.strip() == PAGE_BREAK_MARKER:
                continue
            candidate = line.strip().strip("#>").strip()
            if candidate:
                title = candidate[:80]
                break
    if not title:
        title = "Новая страница"
    if not title:
        st.session_state.last_error = "Нужен заголовок."
        return
    try:
        if st.session_state.selected_page_id:
            saved = client.update_page(st.session_state.selected_page_id, title, content)
        else:
            saved = client.create_page(title, content)
        st.session_state.selected_page_id = saved.get("pageId")
        st.session_state.editor_title = saved.get("title", title)
        st.session_state.editor_content = saved.get("content", content)
        st.session_state.preview_html = saved.get("renderedHtml", "")
        cached_pages = [page for page in st.session_state.pages_cache if page.get("pageId") != saved.get("pageId")]
        cached_pages.append(
            {
                "pageId": saved.get("pageId"),
                "title": saved.get("title", title),
                "content": saved.get("content", content),
                "updatedAt": saved.get("updatedAt", ""),
                "createdAt": saved.get("createdAt", ""),
            }
        )
        st.session_state.pages_cache = cached_pages
        st.session_state.pages_cache_loaded = True
        st.session_state.last_success = "Сохранено."
    except ApiClientError as exc:
        st.session_state.last_error = str(exc)


def render_preview(client: ApiClient) -> None:
    try:
        st.session_state.preview_html = client.render_content(st.session_state.editor_content)
        st.session_state.last_success = "Рендер готов."
    except ApiClientError as exc:
        st.session_state.last_error = str(exc)


def reset_document() -> None:
    st.session_state.selected_page_id = None
    st.session_state.editor_title = ""
    st.session_state.editor_content = ""
    st.session_state.preview_html = ""
    st.session_state.new_draft_id = int(st.session_state.get("new_draft_id", 0)) + 1


def delete_document(client: ApiClient) -> None:
    page_id = st.session_state.selected_page_id
    if not page_id:
        return
    try:
        client.delete_page(page_id)
        st.session_state.pages_cache = [page for page in st.session_state.pages_cache if page.get("pageId") != page_id]
        st.session_state.pages_cache_loaded = True
        reset_document()
        st.session_state.last_success = "Удалено."
    except ApiClientError as exc:
        st.session_state.last_error = str(exc)


def record_label(record: dict[str, Any]) -> str:
    for key in ("Название", "name", "title", "Статус", "status"):
        value = record.get("fields", {}).get(key)
        if value:
            return str(value)
    for value in record.get("fields", {}).values():
        if value:
            return str(value)
    return record.get("recordId", "record")


def install_editor_bridge(insert_lookup: dict[str, str], token: str, hint: str) -> None:
    html = r"""
        <script>
        const parentWindow = window.parent;
        const doc = parentWindow.document;
        const lookup = __WIKILIVE_LOOKUP__;
        const token = __WIKILIVE_TOKEN__;
        const hint = __WIKILIVE_HINT__;
        const menuId = "wikilive-ctx-menu";
        const buttonId = "wikilive-ctx-button";
        const pickerButtonId = "wikilive-ctx-open-picker";
        const editorId = "wikilive-visual-editor";
        const formulaRegex = /\{\{([^:}\n]+):([^:}\n]+):([^}\n]+)\}\}/g;
        const tableSeparatorRegex = /^:?-{3,}:?$/;

        function targetArea() {
            return (
                doc.querySelector('textarea[aria-label="Текст"]') ||
                doc.querySelector('div[data-testid="stTextArea"] textarea') ||
                doc.querySelector("textarea")
            );
        }

        function hideMenu() {
            const menu = doc.getElementById(menuId);
            if (menu) menu.style.display = "none";
        }

        function isPickerOpen() {
            return Boolean(doc.querySelector("#wikilive-picker-open"));
        }

        function findEditorWrapper(area) {
            return area.parentElement;
        }

        function findTableButton() {
            return Array.from(doc.querySelectorAll("button")).find((button) => {
                const text = (button.textContent || "").trim();
                return text === "Таблица" || text === "Скрыть таблицу";
            });
        }

        function openPicker() {
            if (isPickerOpen()) return;
            const button = findTableButton();
            if (button) button.click();
        }

        function escapeHtml(value) {
            return String(value ?? "")
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;");
        }

        function setTextareaValue(area, nextValue, selectionStart = null, selectionEnd = null) {
            const descriptor = Object.getOwnPropertyDescriptor(parentWindow.HTMLTextAreaElement.prototype, "value");
            if (descriptor && descriptor.set) {
                descriptor.set.call(area, nextValue);
            } else {
                area.value = nextValue;
            }
            area.focus();
            if (selectionStart !== null) area.selectionStart = selectionStart;
            if (selectionEnd !== null) area.selectionEnd = selectionEnd;
            area.dispatchEvent(new Event("input", { bubbles: true }));
            area.dispatchEvent(new Event("change", { bubbles: true }));
        }

        function replaceFormulaAtIndex(raw, targetIndex, replacement) {
            let currentIndex = 0;
            formulaRegex.lastIndex = 0;
            return raw.replace(formulaRegex, (match) => {
                if (currentIndex === targetIndex) {
                    currentIndex += 1;
                    return replacement;
                }
                currentIndex += 1;
                return match;
            });
        }

        function clearActiveObjects(area = null) {
            doc.querySelectorAll(".wikilive-object.is-active").forEach((node) => node.classList.remove("is-active"));
            if (area) delete area.dataset.wikiliveReplaceIndex;
        }

        function renderInline(text, tokenCounterRef) {
            formulaRegex.lastIndex = 0;
            let result = "";
            let lastIndex = 0;
            let match;
            while ((match = formulaRegex.exec(text)) !== null) {
                result += escapeHtml(text.slice(lastIndex, match.index));
                const raw = match[0];
                const tableId = match[1];
                const recordId = match[2];
                const fieldName = match[3];
                const lookupKey = `${tableId}::${recordId}::${fieldName}`;
                const value = lookup[lookupKey] || "живое поле";
                const index = tokenCounterRef.value++;
                result += `<span class="wikilive-object" contenteditable="false" data-raw="${escapeHtml(raw)}" data-index="${index}"><span class="wikilive-object__index">#${index + 1}</span><span class="wikilive-object__field">${escapeHtml(fieldName)}</span><span class="wikilive-object__value">${escapeHtml(value)}</span></span>`;
                lastIndex = formulaRegex.lastIndex;
            }
            result += escapeHtml(text.slice(lastIndex));
            return result;
        }

        function isTableLine(line) {
            const stripped = line.trim();
            return stripped.startsWith("|") && stripped.endsWith("|") && stripped.length > 2;
        }

        function parseTableCells(line) {
            return line.trim().slice(1, -1).split("|").map((cell) => cell.trim());
        }

        function isTableSeparator(line) {
            const cells = parseTableCells(line);
            return cells.length > 0 && cells.every((cell) => tableSeparatorRegex.test(cell));
        }

        function renderTableBlock(headerCells, bodyRows, tokenCounterRef) {
            const headerHtml = headerCells.map((cell) => `<th>${renderInline(cell, tokenCounterRef)}</th>`).join("");
            const bodyHtml = bodyRows.map((row) => {
                const cells = row.map((cell) => `<td>${renderInline(cell, tokenCounterRef)}</td>`).join("");
                return `<tr>${cells}</tr>`;
            }).join("");
            return `<div class="wikilive-visual-editor__table-wrap" contenteditable="false"><table class="wikilive-visual-editor__table"><thead><tr>${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`;
        }

        function buildVisualHtml(raw) {
            const lines = String(raw || "").split("\\n");
            const parts = [];
            const tokenCounterRef = { value: 0 };
            for (let i = 0; i < lines.length; ) {
                const line = lines[i];
                const trimmed = line.trim();

                if (isTableLine(trimmed) && i + 1 < lines.length && isTableLine(lines[i + 1].trim()) && isTableSeparator(lines[i + 1].trim())) {
                    const headerCells = parseTableCells(trimmed);
                    const bodyRows = [];
                    i += 2;
                    while (i < lines.length && isTableLine(lines[i].trim())) {
                        const rowCells = parseTableCells(lines[i]);
                        if (rowCells.length !== headerCells.length) break;
                        bodyRows.push(rowCells);
                        i += 1;
                    }
                    parts.push(renderTableBlock(headerCells, bodyRows, tokenCounterRef));
                    continue;
                }

                if (!trimmed) {
                    parts.push('<div class="wikilive-visual-editor__line"><br/></div>');
                    i += 1;
                    continue;
                }

                if (trimmed.startsWith("## ")) {
                    parts.push(`<div class="wikilive-visual-editor__line h2">${renderInline(trimmed.slice(3), tokenCounterRef)}</div>`);
                    i += 1;
                    continue;
                }

                if (trimmed.startsWith("> ")) {
                    parts.push(`<div class="wikilive-visual-editor__callout">${renderInline(trimmed.slice(2), tokenCounterRef)}</div>`);
                    i += 1;
                    continue;
                }

                parts.push(`<div class="wikilive-visual-editor__line">${renderInline(line, tokenCounterRef)}</div>`);
                i += 1;
            }
            return parts.join("");
        }

        function bindObjectClicks(area, overlay) {
            overlay.querySelectorAll(".wikilive-object").forEach((node) => {
                node.onclick = (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    clearActiveObjects();
                    node.classList.add("is-active");
                    area.dataset.wikiliveReplaceIndex = node.dataset.index || "";
                    openPicker();
                };
            });
        }

        function renderVisual(area) {
            const overlay = doc.getElementById(editorId);
            if (!overlay) return;
            const content = overlay.querySelector(".wikilive-visual-editor__content");
            if (!content) return;
            content.innerHTML = buildVisualHtml(area.value || "");
            content.style.transform = `translate(${-area.scrollLeft}px, ${-area.scrollTop}px)`;
            bindObjectClicks(area, overlay);
        }

        function insertToken(area, snippet) {
            if (!area || !snippet) return;
            const raw = area.value || "";
            const replaceIndexRaw = area.dataset.wikiliveReplaceIndex;
            let nextValue = raw;
            let nextCaret = (area.selectionStart ?? raw.length) + snippet.length;
            if (replaceIndexRaw !== undefined && replaceIndexRaw !== "") {
                const replaceIndex = Number(replaceIndexRaw);
                nextValue = replaceFormulaAtIndex(raw, replaceIndex, snippet);
                nextCaret = nextValue.length;
            } else {
                const start = area.selectionStart ?? raw.length;
                const end = area.selectionEnd ?? start;
                nextValue = raw.slice(0, start) + snippet + raw.slice(end);
                nextCaret = start + snippet.length;
            }
            clearActiveObjects(area);
            setTextareaValue(area, nextValue, nextCaret, nextCaret);
            renderVisual(area);
            hideMenu();
        }

        function ensureOverlay(area) {
            let overlay = doc.getElementById(editorId);
            const wrapper = findEditorWrapper(area);
            if (!wrapper) return null;
            wrapper.style.position = "relative";
            if (!overlay) {
                overlay = doc.createElement("div");
                overlay.id = editorId;
                overlay.className = "wikilive-visual-editor";
                overlay.innerHTML = '<div class="wikilive-visual-editor__content"></div>';
                wrapper.appendChild(overlay);
            }
            return overlay;
        }

        function ensureMenu() {
            let menu = doc.getElementById(menuId);
            if (!menu) {
                menu = doc.createElement("div");
                menu.id = menuId;
                menu.style.cssText = "position:fixed;z-index:999999;display:none;min-width:220px;padding:8px;border-radius:16px;background:#fffffff7;border:1px solid rgba(20,23,28,.08);box-shadow:0 18px 40px rgba(20,23,28,.16)";
                menu.innerHTML = `
                    <button id="${pickerButtonId}" type="button" style="width:100%;border:none;border-radius:12px;background:#ffffff;color:#14171c;padding:11px 12px;font-weight:800;text-align:left;cursor:pointer;border:1px solid rgba(227,6,19,.28);margin-bottom:6px">Выбрать из таблицы</button>
                    <button id="${buttonId}" type="button" style="width:100%;border:none;border-radius:12px;background:rgba(227,6,19,.08);color:#bf0812;padding:11px 12px;font-weight:800;text-align:left;cursor:pointer">Вставить значение</button>
                    <div data-wikilive-hint style="padding:8px 4px 2px 4px;color:#7a828e;font:500 12px/1.4 Manrope,sans-serif"></div>
                `;
                doc.body.appendChild(menu);
            }
            const insertButton = menu.querySelector(`#${buttonId}`);
            if (insertButton) {
                insertButton.disabled = !token;
                insertButton.style.opacity = token ? "1" : ".45";
                insertButton.style.cursor = token ? "pointer" : "default";
            }
            const hintNode = menu.querySelector("[data-wikilive-hint]");
            if (hintNode) hintNode.textContent = hint || "Выбери диапазон";
            return menu;
        }

        function attach() {
            const area = targetArea();
            if (!area) {
                setTimeout(attach, 400);
                return;
            }

            ensureOverlay(area);
            area.dataset.wikiliveVisual = "true";
            area.setAttribute("data-wikilive-visual", "true");
            area.dataset.wikiliveSnippet = token;
            area.dataset.wikiliveHint = hint;

            parentWindow.__wikiliveInsertSnippet = (snippet) => {
                const activeArea = targetArea();
                if (activeArea) insertToken(activeArea, snippet);
            };
            parentWindow.__wikiliveRefreshVisual = () => {
                const activeArea = targetArea();
                if (activeArea) renderVisual(activeArea);
            };

            const preparedMenu = ensureMenu();
            const pickerButton = preparedMenu.querySelector(`#${pickerButtonId}`);
            const insertButton = preparedMenu.querySelector(`#${buttonId}`);
            if (pickerButton) {
                pickerButton.onclick = () => {
                    openPicker();
                    hideMenu();
                };
            }
            if (insertButton) {
                insertButton.onclick = () => insertToken(area, area.dataset.wikiliveSnippet || "");
            }

            if (area.dataset.ctxAttached === "1") {
                renderVisual(area);
                return;
            }

            area.dataset.ctxAttached = "1";
            renderVisual(area);
            area.addEventListener("input", () => renderVisual(area));
            area.addEventListener("scroll", () => renderVisual(area));
            area.addEventListener("click", () => clearActiveObjects(area));
            area.addEventListener("contextmenu", (event) => {
                event.preventDefault();
                const menu = ensureMenu();
                menu.style.left = `${Math.min(event.clientX, parentWindow.innerWidth - 240)}px`;
                menu.style.top = `${Math.min(event.clientY, parentWindow.innerHeight - 120)}px`;
                menu.style.display = "block";
            });
            doc.addEventListener("click", hideMenu, true);
            doc.addEventListener("scroll", hideMenu, true);
            area.addEventListener("blur", hideMenu);
        }

        attach();
        </script>
    """
    html = html.replace("__WIKILIVE_LOOKUP__", json.dumps(insert_lookup, ensure_ascii=False))
    html = html.replace("__WIKILIVE_TOKEN__", json.dumps(token))
    html = html.replace("__WIKILIVE_HINT__", json.dumps(hint))
    components.html(html, height=0)
    return
    '''
        <script>
        const doc = window.parent.document;
        const lookup = {json.dumps(insert_lookup, ensure_ascii=False)};
        const token = {json.dumps(token)};
        const hint = {json.dumps(hint)};
        const menuId = "wikilive-ctx-menu";
        const buttonId = "wikilive-ctx-button";
        const pickerButtonId = "wikilive-ctx-open-picker";
        const editorId = "wikilive-visual-editor";
        const ob = String.fromCharCode(123);
        const cb = String.fromCharCode(125);
        const formulaRegex = new RegExp(ob + ob + "([^:" + cb + "\\\\n]+):([^:" + cb + "\\\\n]+):([^" + cb + "\\\\n]+)" + cb + cb, "g");
        const tableSeparatorRegex = /^:?-{{3,}}:?$/;

        function targetArea() {{
            return doc.querySelector('textarea[aria-label="Текст"]') || doc.querySelector("textarea");
        }}

        function hideMenu() {{
            const menu = doc.getElementById(menuId);
            if (menu) menu.style.display = "none";
        }}

        function isPickerOpen() {{
            return Boolean(doc.querySelector("#wikilive-picker-open"));
        }}

        function findEditorWrapper(area) {{
            return area.parentElement;
        }}

        function findTableButton() {{
            return Array.from(doc.querySelectorAll("button")).find((button) => {{
                const text = (button.textContent || "").trim();
                return text === "Таблица" || text === "Скрыть таблицу";
            }});
        }}

        function openPicker() {{
            if (isPickerOpen()) return;
            const button = findTableButton();
            hideMenu();
            if (button) button.click();
        }}

        function setTextareaValue(area, nextValue, selectionStart = null, selectionEnd = null) {{
            const descriptor = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value");
            if (descriptor && descriptor.set) {{
                descriptor.set.call(area, nextValue);
            }} else {{
                area.value = nextValue;
            }}
            area.focus();
            if (selectionStart !== null) area.selectionStart = selectionStart;
            if (selectionEnd !== null) area.selectionEnd = selectionEnd;
            area.dispatchEvent(new Event("input", {{ bubbles: true }}));
            area.dispatchEvent(new Event("change", {{ bubbles: true }}));
            if (typeof area.blur === "function") {{
                area.blur();
                area.focus();
            }}
        }}

        function replaceFormulaAtIndex(raw, targetIndex, replacement) {{
            let currentIndex = 0;
            return raw.replace(formulaRegex, (match) => {{
                if (currentIndex === targetIndex) {{
                    currentIndex += 1;
                    return replacement;
                }}
                currentIndex += 1;
                return match;
            }});
        }}

        function clearActiveObjects() {{
            doc.querySelectorAll(".wikilive-object.is-active").forEach((node) => node.classList.remove("is-active"));
        }}

        function insertToken(area, snippet) {{
            if (!area || !snippet) return;
            const raw = area.value || "";
            const replaceIndexRaw = area.dataset.wikiliveReplaceIndex;
            let nextValue = raw;
            let nextCaret = (area.selectionStart ?? raw.length) + snippet.length;
            if (replaceIndexRaw !== undefined && replaceIndexRaw !== "") {{
                const replaceIndex = Number(replaceIndexRaw);
                nextValue = replaceFormulaAtIndex(raw, replaceIndex, snippet);
                nextCaret = raw.length <= nextValue.length ? nextValue.length : Math.min(nextValue.length, area.selectionStart ?? nextValue.length);
            }} else {{
                const start = area.selectionStart ?? raw.length;
                const end = area.selectionEnd ?? start;
                nextValue = raw.slice(0, start) + snippet + raw.slice(end);
                nextCaret = start + snippet.length;
            }}
            delete area.dataset.wikiliveReplaceIndex;
            setTextareaValue(area, nextValue, nextCaret, nextCaret);
            renderVisual(area);
            hideMenu();
        }}

        function escapeHtml(value) {{
            return value
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;");
        }}

        function renderInline(text, tokenCounterRef) {{
            formulaRegex.lastIndex = 0;
            let result = "";
            let lastIndex = 0;
            let match;
            while ((match = formulaRegex.exec(text)) !== null) {{
                result += escapeHtml(text.slice(lastIndex, match.index));
                const raw = match[0];
                const tableId = match[1];
                const recordId = match[2];
                const fieldName = match[3];
                const lookupKey = `${{tableId}}::${{recordId}}::${{fieldName}}`;
                const value = lookup[lookupKey] || "живое поле";
                const index = tokenCounterRef.value++;
                result += `<span class="wikilive-object" contenteditable="false" data-raw="${{escapeHtml(raw)}}" data-index="${{index}}}"><span class="wikilive-object__index">#${{index + 1}}</span><span class="wikilive-object__field">${{escapeHtml(fieldName)}}</span><span class="wikilive-object__value">${{escapeHtml(String(value))}}</span></span>`;
                lastIndex = formulaRegex.lastIndex;
            }}
            result += escapeHtml(text.slice(lastIndex));
            return result;
        }}

        function isTableLine(line) {{
            const stripped = line.trim();
            return stripped.startsWith("|") && stripped.endsWith("|") && stripped.length > 2;
        }}

        function parseTableCells(line) {{
            return line.trim().slice(1, -1).split("|").map((cell) => cell.trim());
        }}

        function isTableSeparator(line) {{
            const cells = parseTableCells(line);
            return cells.length > 0 && cells.every((cell) => tableSeparatorRegex.test(cell));
        }}

        function renderTableBlock(headerCells, bodyRows, tokenCounterRef) {{
            const headerHtml = headerCells.map((cell) => `<th>${{renderInline(cell, tokenCounterRef)}}</th>`).join("");
            const bodyHtml = bodyRows.map((row) => {{
                const cells = row.map((cell) => `<td>${{renderInline(cell, tokenCounterRef)}}</td>`).join("");
                return `<tr>${{cells}}</tr>`;
            }}).join("");
            return `<div class="wikilive-visual-editor__table-wrap" contenteditable="false"><table class="wikilive-visual-editor__table"><thead><tr>${{headerHtml}}</tr></thead><tbody>${{bodyHtml}}</tbody></table></div>`;
        }}

        function buildVisualHtml(raw) {{
            const lines = String(raw || "").split("\\n");
            const parts = [];
            const tokenCounterRef = {{ value: 0 }};
            for (let i = 0; i < lines.length; ) {{
                const line = lines[i];
                const trimmed = line.trim();

                if (isTableLine(trimmed) && i + 1 < lines.length && isTableLine(lines[i + 1].trim()) && isTableSeparator(lines[i + 1].trim())) {{
                    const headerCells = parseTableCells(trimmed);
                    const bodyRows = [];
                    i += 2;
                    while (i < lines.length && isTableLine(lines[i].trim())) {{
                        const rowCells = parseTableCells(lines[i]);
                        if (rowCells.length !== headerCells.length) break;
                        bodyRows.push(rowCells);
                        i += 1;
                    }}
                    parts.push(renderTableBlock(headerCells, bodyRows, tokenCounterRef));
                    continue;
                }}

                if (!trimmed) {{
                    parts.push('<div class="wikilive-visual-editor__line"><br/></div>');
                    i += 1;
                    continue;
                }}

                if (trimmed.startsWith("## ")) {{
                    parts.push(`<div class="wikilive-visual-editor__line h2">${{renderInline(trimmed.slice(3), tokenCounterRef)}}</div>`);
                    i += 1;
                    continue;
                }}

                if (trimmed.startsWith("> ")) {{
                    parts.push(`<div class="wikilive-visual-editor__callout">${{renderInline(trimmed.slice(2), tokenCounterRef)}}</div>`);
                    i += 1;
                    continue;
                }}

                parts.push(`<div class="wikilive-visual-editor__line">${{renderInline(line, tokenCounterRef)}}</div>`);
                i += 1;
            }}
            return parts.join("");
        }}

        function bindObjectClicks(area, overlay) {{
            overlay.querySelectorAll(".wikilive-object").forEach((node) => {{
                node.onclick = (event) => {{
                    event.preventDefault();
                    event.stopPropagation();
                    clearActiveObjects();
                    node.classList.add("is-active");
                    area.dataset.wikiliveReplaceIndex = node.dataset.index || "";
                    openPicker();
                }};
            }});
        }}

        function renderVisual(area) {{
            const overlay = doc.getElementById(editorId);
            if (!overlay) return;
            const content = overlay.querySelector(".wikilive-visual-editor__content");
            if (!content) return;
            content.innerHTML = buildVisualHtml(area.value || "");
            content.style.transform = `translate(${{-area.scrollLeft}}px, ${{-area.scrollTop}}px)`;
            bindObjectClicks(area, overlay);
        }}

        function ensureOverlay(area) {{
            let overlay = doc.getElementById(editorId);
            const wrapper = findEditorWrapper(area);
            if (!wrapper) return null;
            wrapper.style.position = "relative";
            if (!overlay) {{
                overlay = doc.createElement("div");
                overlay.id = editorId;
                overlay.className = "wikilive-visual-editor";
                overlay.innerHTML = '<div class="wikilive-visual-editor__content"></div>';
                wrapper.appendChild(overlay);
            }}
            return overlay;
        }}

        function ensureMenu() {{
            let menu = doc.getElementById(menuId);
            if (!menu) {{
                menu = doc.createElement("div");
                menu.id = menuId;
                menu.style.cssText = "position:fixed;z-index:999999;display:none;min-width:210px;padding:8px;border-radius:16px;background:#fffffff7;border:1px solid rgba(20,23,28,.08);box-shadow:0 18px 40px rgba(20,23,28,.16)";
                menu.innerHTML = `
                    <button id="${{pickerButtonId}}" type="button" style="width:100%;border:none;border-radius:12px;background:#ffffff;color:#14171c;padding:11px 12px;font-weight:800;text-align:left;cursor:pointer;border:1px solid rgba(227,6,19,.28);margin-bottom:6px">Выбрать из таблицы</button>
                    <button id="${{buttonId}}" type="button" style="width:100%;border:none;border-radius:12px;background:rgba(227,6,19,.08);color:#bf0812;padding:11px 12px;font-weight:800;text-align:left;cursor:pointer">Вставить значение</button>
                    <div style="padding:8px 4px 2px 4px;color:#7a828e;font:500 12px/1.4 Manrope,sans-serif">${{hint}}</div>
                `;
                doc.body.appendChild(menu);
            }}
            return menu;
        }}

        function attach() {{
            const area = targetArea();
            if (!area) {{
                setTimeout(attach, 400);
                return;
            }}
            ensureOverlay(area);
            area.dataset.wikiliveVisual = "true";
            area.setAttribute("data-wikilive-visual", "true");
            area.dataset.wikiliveSnippet = token;
            area.dataset.wikiliveHint = hint;
            const preparedMenu = ensureMenu();
            const hintNode = preparedMenu.querySelector("div");
            if (hintNode) hintNode.textContent = hint;
            const pickerButton = doc.getElementById(pickerButtonId);
            if (pickerButton) pickerButton.onclick = () => {{ openPicker(); hideMenu(); }};
            if (area.dataset.ctxAttached === "1") return;
            area.dataset.ctxAttached = "1";
            renderVisual(area);
            area.addEventListener("input", () => renderVisual(area));
            area.addEventListener("scroll", () => renderVisual(area));
            area.addEventListener("contextmenu", (event) => {{
                event.preventDefault();
                openPicker();
                const menu = ensureMenu();
                menu.style.left = `${{Math.min(event.clientX, window.parent.innerWidth - 230)}}px`;
                menu.style.top = `${{Math.min(event.clientY, window.parent.innerHeight - 100)}}px`;
                menu.style.display = "block";
                const button = doc.getElementById(buttonId);
                if (button) button.onclick = () => {{ insertToken(area, area.dataset.wikiliveSnippet || ""); }};
            }});
            doc.addEventListener("click", hideMenu, true);
            doc.addEventListener("scroll", hideMenu, true);
            area.addEventListener("blur", hideMenu);
        }}

        attach();
        </script>
        """,
        height=0,
    )


    '''


def render_insert_button(snippet: str, hint: str) -> None:
    html = """
        <button id="wikilive-insert-direct" type="button" style="
            width:100%;
            min-height:44px;
            border-radius:16px;
            border:1px solid rgba(227,6,19,.35);
            background:#ffffff;
            color:#c10813;
            font:800 14px/1.2 Manrope,sans-serif;
            cursor:pointer;
        ">Вставить значение</button>
        <script>
        const snippet = __WIKILIVE_SNIPPET__;
        const hint = __WIKILIVE_HINT__;
        const button = document.getElementById("wikilive-insert-direct");
        if (typeof window.parent.__wikiliveSetActiveSnippet === "function") {
            window.parent.__wikiliveSetActiveSnippet(snippet, hint);
        }
        if (button) {
            button.onclick = () => {
                if (typeof window.parent.__wikiliveSetActiveSnippet === "function") {
                    window.parent.__wikiliveSetActiveSnippet(snippet, hint);
                }
                if (typeof window.parent.__wikiliveInsertSnippet === "function") {
                    window.parent.__wikiliveInsertSnippet(snippet);
                }
            };
        }
        </script>
    """
    html = html.replace("__WIKILIVE_SNIPPET__", json.dumps(snippet))
    html = html.replace("__WIKILIVE_HINT__", json.dumps(hint))
    components.html(html, height=52)
    return
    '''
        <button id="wikilive-insert-direct" type="button" style="
            width:100%;
            min-height:44px;
            border-radius:16px;
            border:1px solid rgba(227,6,19,.35);
            background:#ffffff;
            color:#c10813;
            font:800 14px/1.2 Manrope,sans-serif;
            cursor:pointer;
        ">Вставить значение</button>
        <script>
        const doc = window.parent.document;
        const snippet = {json.dumps(snippet)};
        const button = document.getElementById("wikilive-insert-direct");
        button.onclick = () => {{
            const area = doc.querySelector('textarea[aria-label="Текст"]') || doc.querySelector("textarea");
            if (!area) return;
            const formulaRegex = new RegExp("\\\\{\\\\{([^:\\\\}\\\\n]+):([^:\\\\}\\\\n]+):([^\\\\}\\\\n]+)\\\\}\\\\}", "g");
            const replaceIndexRaw = area.dataset.wikiliveReplaceIndex;
            const currentValue = area.value || "";
            let nextValue = currentValue;
            let nextCaret = (area.selectionStart ?? currentValue.length) + snippet.length;
            if (replaceIndexRaw !== undefined && replaceIndexRaw !== "") {{
                let currentIndex = 0;
                const replaceIndex = Number(replaceIndexRaw);
                nextValue = currentValue.replace(formulaRegex, (match) => {{
                    if (currentIndex === replaceIndex) {{
                        currentIndex += 1;
                        return snippet;
                    }}
                    currentIndex += 1;
                    return match;
                }});
                delete area.dataset.wikiliveReplaceIndex;
                nextCaret = nextValue.length;
            }} else {{
                const start = area.selectionStart ?? currentValue.length;
                const end = area.selectionEnd ?? start;
                nextValue = currentValue.slice(0, start) + snippet + currentValue.slice(end);
                nextCaret = start + snippet.length;
            }}
            const descriptor = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value");
            if (descriptor && descriptor.set) {{
                descriptor.set.call(area, nextValue);
            }} else {{
                area.value = nextValue;
            }}
            area.focus();
            area.selectionStart = nextCaret;
            area.selectionEnd = nextCaret;
            area.dispatchEvent(new Event("input", {{ bubbles: true }}));
            area.dispatchEvent(new Event("change", {{ bubbles: true }}));
        }};
        </script>
        """,
        height=52,
    )


    '''


def build_table_dataframe(payload: dict[str, Any]) -> tuple[pd.DataFrame, list[dict[str, Any]], list[str]]:
    records = payload.get("records", [])
    field_names = payload.get("fieldNames", [])
    rows: list[dict[str, Any]] = []
    index_labels: list[str] = []
    for record in records:
        row = {field_name: record.get("fields", {}).get(field_name, "") for field_name in field_names}
        rows.append(row)
        index_labels.append(record_label(record))
    dataframe = pd.DataFrame(rows, columns=field_names)
    if index_labels:
        dataframe.index = index_labels
    return dataframe, records, field_names


def extract_cells(selection_event: Any) -> list[tuple[int, str]]:
    if selection_event is None:
        return []
    selection = getattr(selection_event, "selection", None)
    if selection is None and isinstance(selection_event, dict):
        selection = selection_event.get("selection", {})
    if selection is None:
        return []
    cells = getattr(selection, "cells", None)
    if cells is None and isinstance(selection, dict):
        cells = selection.get("cells", [])
    if not isinstance(cells, list):
        return []
    normalized: list[tuple[int, str]] = []
    for cell in cells:
        if isinstance(cell, (list, tuple)) and len(cell) == 2 and isinstance(cell[0], int) and isinstance(cell[1], str):
            normalized.append((cell[0], cell[1]))
    return normalized


def build_selection_snippet(
    payload: dict[str, Any],
    cells: list[tuple[int, str]],
) -> tuple[str, str, str]:
    if not cells:
        return "", "", ""

    records = payload.get("records", [])
    field_order = payload.get("fieldNames", [])
    selected_rows = sorted({row_index for row_index, _ in cells})
    selected_columns = [field_name for field_name in field_order if any(column == field_name for _, column in cells)]
    selected_set = {(row_index, column_name) for row_index, column_name in cells}

    token_lines: list[str] = []
    value_lines: list[str] = []
    for row_index in selected_rows:
        if row_index < 0 or row_index >= len(records):
            continue
        record = records[row_index]
        token_parts: list[str] = []
        value_parts: list[str] = []
        for column_name in selected_columns:
            if (row_index, column_name) not in selected_set:
                continue
            token_parts.append(
                build_formula_token(
                    payload.get("tableId", ""),
                    record.get("recordId", ""),
                    column_name,
                )
            )
            value_parts.append(str(record.get("fields", {}).get(column_name, "")))
        if token_parts:
            token_lines.append("\t".join(token_parts))
            value_lines.append("\t".join(value_parts))

    snippet = "\n".join(token_lines)
    value_preview = "\n".join(value_lines)
    if len(selected_rows) == 1 and len(selected_columns) == 1:
        hint = f"{selected_rows[0] + 1} / {selected_columns[0]}"
    else:
        hint = f"{len(selected_rows)}x{len(selected_columns)}"
    return snippet, value_preview, hint


def build_table_selection_snippet(payload: dict[str, Any], cells: list[tuple[int, str]]) -> tuple[str, str, str]:
    if not cells:
        return "", "", ""

    records = payload.get("records", [])
    field_order = payload.get("fieldNames", [])
    selected_rows = sorted({row_index for row_index, _ in cells})
    selected_columns = [field_name for field_name in field_order if any(column == field_name for _, column in cells)]
    selected_set = {(row_index, column_name) for row_index, column_name in cells}
    if not selected_rows or not selected_columns:
        return "", "", ""

    header = "| " + " | ".join(selected_columns) + " |"
    separator = "| " + " | ".join(["---"] * len(selected_columns)) + " |"
    table_lines = [header, separator]
    preview_lines = [header.replace("|", "").strip()]

    for row_index in selected_rows:
        if row_index < 0 or row_index >= len(records):
            continue
        record = records[row_index]
        token_cells: list[str] = []
        preview_cells: list[str] = []
        for column_name in selected_columns:
            if (row_index, column_name) in selected_set:
                token_cells.append(
                    build_formula_token(payload.get("tableId", ""), record.get("recordId", ""), column_name)
                )
                preview_cells.append(str(record.get("fields", {}).get(column_name, "")))
            else:
                token_cells.append("")
                preview_cells.append("")
        table_lines.append("| " + " | ".join(token_cells) + " |")
        preview_lines.append("| " + " | ".join(preview_cells) + " |")

    return "\n".join(table_lines), "\n".join(preview_lines), f"{len(selected_rows)}x{len(selected_columns)} table"


def build_block_selection_snippet(payload: dict[str, Any], cells: list[tuple[int, str]]) -> tuple[str, str, str]:
    if not cells:
        return "", "", ""

    records = payload.get("records", [])
    field_order = payload.get("fieldNames", [])
    selected_rows = sorted({row_index for row_index, _ in cells})
    selected_columns = [field_name for field_name in field_order if any(column == field_name for _, column in cells)]
    selected_set = {(row_index, column_name) for row_index, column_name in cells}
    lines: list[str] = []
    previews: list[str] = []

    for row_index in selected_rows:
        if row_index < 0 or row_index >= len(records):
            continue
        record = records[row_index]
        row_title = record_label(record)
        lines.append(f"## {row_title}")
        previews.append(row_title)
        for column_name in selected_columns:
            if (row_index, column_name) not in selected_set:
                continue
            token = build_formula_token(payload.get("tableId", ""), record.get("recordId", ""), column_name)
            lines.append(f"{column_name}: {token}")
            previews.append(f"{column_name}: {record.get('fields', {}).get(column_name, '')}")
        lines.append("")
        previews.append("")

    return "\n".join(lines).strip(), "\n".join(previews).strip(), f"{len(selected_rows)} blocks"


def build_insert_lookup_payload(insert_options: Any) -> dict[str, str]:
    option_sets: list[dict[str, Any]] = []
    if isinstance(insert_options, dict) and "records" in insert_options:
        option_sets = [insert_options]
    elif isinstance(insert_options, dict):
        option_sets = [value for value in insert_options.values() if isinstance(value, dict) and "records" in value]
    elif isinstance(insert_options, list):
        option_sets = [value for value in insert_options if isinstance(value, dict) and "records" in value]

    lookup: dict[str, str] = {}
    for option_set in option_sets:
        table_id = str(option_set.get("tableId", ""))
        for record in option_set.get("records", []):
            record_id = str(record.get("recordId", ""))
            for field_name, value in record.get("fields", {}).items():
                lookup[f"{table_id}::{record_id}::{field_name}"] = str(value)
    return lookup


def build_editor_lookup_payload(insert_options: Any) -> dict[str, dict[str, Any]]:
    option_sets: list[dict[str, Any]] = []
    if isinstance(insert_options, dict) and "records" in insert_options:
        option_sets = [insert_options]
    elif isinstance(insert_options, dict):
        option_sets = [value for value in insert_options.values() if isinstance(value, dict) and "records" in value]
    elif isinstance(insert_options, list):
        option_sets = [value for value in insert_options if isinstance(value, dict) and "records" in value]

    lookup: dict[str, dict[str, Any]] = {}
    for option_set in option_sets:
        table_id = str(option_set.get("tableId", ""))
        for record in option_set.get("records", []):
            record_id = str(record.get("recordId", ""))
            field_meta = record.get("fieldMeta", {}) if isinstance(record.get("fieldMeta"), dict) else {}
            for field_name, value in record.get("fields", {}).items():
                meta = field_meta.get(field_name, {}) if isinstance(field_meta.get(field_name), dict) else {}
                resolved_value = str(meta.get("value", value))
                resource_url = str(meta.get("resourceUrl", ""))
                mime_type = str(meta.get("mimeType", ""))
                is_image = bool(meta.get("isImage", False))
                if not is_image:
                    probe = f"{resolved_value} {resource_url}".lower()
                    is_image = any(probe.endswith(ext) or ext in probe for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"))
                lookup[f"{table_id}::{record_id}::{field_name}"] = {
                    "value": resolved_value,
                    "resourceUrl": resource_url,
                    "mimeType": mime_type,
                    "isImage": is_image,
                    "fieldName": field_name,
                }
    return lookup


def render_rich_editor(
    insert_lookup: dict[str, dict[str, Any]],
    draft_key: str,
    active_snippet: str,
    active_hint: str,
) -> None:
    html = r"""
        <style>
        html, body {
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Manrope', sans-serif;
            color: #14171c;
        }
        .wikilive-rich-root {
            border: 1px solid rgba(20, 23, 28, 0.08);
            border-radius: 30px;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.99), rgba(255,255,255,0.97)),
                repeating-linear-gradient(180deg, transparent 0, transparent 35px, rgba(227, 6, 19, 0.045) 35px, rgba(227, 6, 19, 0.045) 36px);
            box-shadow: 0 22px 54px rgba(20, 23, 28, 0.07);
            min-height: 74vh;
            padding: 1.15rem 1.35rem 1.35rem;
            overflow: hidden;
        }
        #wikilive-editor {
            min-height: calc(74vh - 12px);
            outline: none;
            font: 500 18px/1.8 Manrope, sans-serif;
            color: #14171c;
            caret-color: #e30613;
            white-space: normal;
            word-break: break-word;
        }
        #wikilive-editor:empty::before {
            content: attr(data-placeholder);
            color: #9aa2ae;
        }
        .wl-line {
            min-height: 1.8em;
            white-space: pre-wrap;
        }
        .wl-line + .wl-line {
            margin-top: 0.02rem;
        }
        .wl-line[data-kind="heading"] {
            font: 700 1.18rem/1.55 'Onest', sans-serif;
        }
        .wl-line[data-kind="callout"] {
            padding: 0.35rem 0.75rem;
            margin: 0.18rem 0;
            border-left: 4px solid #e30613;
            border-radius: 0 16px 16px 0;
            background: rgba(227, 6, 19, 0.06);
        }
        .wl-object {
            display: inline-flex;
            align-items: center;
            gap: 0.36rem;
            padding: 0.18rem 0.46rem;
            margin: 0 0.16rem;
            border-radius: 999px;
            border: 1px solid rgba(227, 6, 19, 0.18);
            background: #ffffff;
            box-shadow: 0 10px 24px rgba(227, 6, 19, 0.07);
            vertical-align: baseline;
            cursor: pointer;
            transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
        }
        .wl-object:hover,
        .wl-object.is-selected {
            transform: translateY(-1px);
            border-color: rgba(227, 6, 19, 0.42);
            box-shadow: 0 12px 28px rgba(227, 6, 19, 0.12);
        }
        .wl-object__index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.35rem;
            height: 1.35rem;
            border-radius: 999px;
            background: #e30613;
            color: #ffffff;
            font-size: 0.7rem;
            font-weight: 800;
        }
        .wl-object__field {
            color: #bf0812;
            font-size: 0.78rem;
            font-weight: 800;
        }
        .wl-object__value {
            color: #4b5563;
            font-size: 0.78rem;
        }
        .wl-image {
            display: inline-flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.42rem;
            width: min(240px, 92%);
            margin: 0.2rem 0.32rem;
            padding: 0.45rem;
            border-radius: 20px;
            border: 1px solid rgba(227, 6, 19, 0.16);
            background: #ffffff;
            box-shadow: 0 14px 34px rgba(20, 23, 28, 0.08);
            vertical-align: top;
        }
        .wl-image img {
            width: 100%;
            max-height: 190px;
            object-fit: cover;
            border-radius: 14px;
            display: block;
            background: #f4f5f7;
        }
        .wl-image__meta {
            display: flex;
            align-items: center;
            gap: 0.38rem;
            flex-wrap: wrap;
        }
        .wl-image__name {
            font-size: 0.82rem;
            color: #303641;
            font-weight: 700;
        }
        .wl-table-block {
            margin: 0.45rem 0 0.75rem;
            overflow: auto;
            border-radius: 20px;
            border: 1px solid rgba(20, 23, 28, 0.08);
            background: #ffffff;
        }
        .wl-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }
        .wl-table th,
        .wl-table td {
            padding: 0.72rem 0.8rem;
            border-bottom: 1px solid rgba(20, 23, 28, 0.06);
            text-align: left;
            vertical-align: top;
        }
        .wl-table th {
            background: rgba(227, 6, 19, 0.05);
            font-weight: 800;
        }
        .wl-table .wl-image {
            width: 180px;
            max-width: 100%;
        }
        .wl-context-menu {
            position: fixed;
            z-index: 99999;
            display: none;
            min-width: 220px;
            padding: 8px;
            border-radius: 16px;
            border: 1px solid rgba(20, 23, 28, 0.08);
            background: rgba(255,255,255,0.98);
            box-shadow: 0 18px 40px rgba(20, 23, 28, 0.16);
        }
        .wl-context-menu button {
            width: 100%;
            border: 1px solid rgba(227, 6, 19, 0.22);
            background: #ffffff;
            color: #14171c;
            border-radius: 12px;
            padding: 0.72rem 0.85rem;
            text-align: left;
            font: 800 14px/1.2 Manrope, sans-serif;
            cursor: pointer;
            transition: border-color .16s ease, box-shadow .16s ease, transform .16s ease;
        }
        .wl-context-menu button + button {
            margin-top: 0.35rem;
        }
        .wl-context-menu button:hover:not(:disabled) {
            transform: translateY(-1px);
            border-color: rgba(227, 6, 19, 0.48);
            box-shadow: 0 10px 20px rgba(227, 6, 19, 0.08);
        }
        .wl-context-menu button:disabled {
            opacity: 0.45;
            cursor: default;
            box-shadow: none;
        }
        .wl-context-menu__hint {
            margin-top: 0.45rem;
            padding: 0 0.2rem;
            color: #818998;
            font: 500 12px/1.45 Manrope, sans-serif;
        }
        </style>
        <div class="wikilive-rich-root">
            <div id="wikilive-editor" contenteditable="true" spellcheck="false" data-placeholder="Пиши здесь"></div>
        </div>
        <div id="wikilive-context-menu" class="wl-context-menu">
            <button id="wikilive-context-open" type="button">Выбрать из таблицы</button>
            <button id="wikilive-context-insert" type="button">Вставить значение</button>
            <div id="wikilive-context-hint" class="wl-context-menu__hint"></div>
        </div>
        <script>
        const parentWindow = window.parent;
        const parentDoc = parentWindow.document;
        const lookup = __WIKILIVE_LOOKUP__;
        const draftKey = __WIKILIVE_DRAFT_KEY__;
        let activeSnippet = __WIKILIVE_ACTIVE_SNIPPET__;
        let activeHint = __WIKILIVE_ACTIVE_HINT__;
        const storageKey = `wikilive:draft:${draftKey}`;
        const selectedKey = `wikilive:selected:${draftKey}`;
        const snippetKey = `wikilive:active-snippet:${draftKey}`;
        const hintKey = `wikilive:active-hint:${draftKey}`;
        const tokenRegex = /\{\{([^:}\n]+):([^:}\n]+):([^}\n]+)\}\}/g;
        const tableSeparatorRegex = /^:?-{3,}:?$/;
        const editor = document.getElementById("wikilive-editor");
        const contextMenu = document.getElementById("wikilive-context-menu");
        const contextOpenButton = document.getElementById("wikilive-context-open");
        const contextInsertButton = document.getElementById("wikilive-context-insert");
        const contextHintNode = document.getElementById("wikilive-context-hint");
        let selectedObject = null;
        let lastRange = null;
        let dragRaw = "";
        let dragSourceNode = null;
        let isRendering = false;
        let storeTimer = null;
        let selectionTimer = null;

        function targetArea() {
            return (
                parentDoc.querySelector('textarea[aria-label="Текст"]') ||
                parentDoc.querySelector('div[data-testid="stTextArea"] textarea') ||
                parentDoc.querySelector("textarea")
            );
        }

        function getHiddenValue() {
            const area = targetArea();
            return area ? String(area.value || "") : "";
        }

        function setHiddenValue(value) {
            const area = targetArea();
            if (!area) return;
            const descriptor = Object.getOwnPropertyDescriptor(parentWindow.HTMLTextAreaElement.prototype, "value");
            if (descriptor && descriptor.set) {
                descriptor.set.call(area, value);
            } else {
                area.value = value;
            }
            area.dispatchEvent(new Event("input", { bubbles: true }));
            area.dispatchEvent(new Event("change", { bubbles: true }));
        }

        function loadDraft() {
            parentWindow.__wikiliveDrafts = parentWindow.__wikiliveDrafts || {};
            const parentDraft = parentWindow.__wikiliveDrafts[draftKey];
            if (typeof parentDraft === "string") {
                return parentDraft;
            }
            const stored = parentWindow.sessionStorage.getItem(storageKey);
            if (stored !== null) {
                return stored;
            }
            return getHiddenValue();
        }

        function storeDraft(raw) {
            parentWindow.__wikiliveDrafts = parentWindow.__wikiliveDrafts || {};
            parentWindow.__wikiliveDrafts[draftKey] = raw;
            parentWindow.sessionStorage.setItem(storageKey, raw);
        }

        function ensureActiveSnippetState() {
            parentWindow.__wikiliveActiveSnippets = parentWindow.__wikiliveActiveSnippets || {};
            if (typeof activeSnippet === "string" && activeSnippet) {
                parentWindow.__wikiliveActiveSnippets[draftKey] = activeSnippet;
                parentWindow.sessionStorage.setItem(snippetKey, activeSnippet);
            } else {
                activeSnippet = parentWindow.__wikiliveActiveSnippets[draftKey] || parentWindow.sessionStorage.getItem(snippetKey) || "";
            }

            parentWindow.__wikiliveActiveHints = parentWindow.__wikiliveActiveHints || {};
            if (typeof activeHint === "string" && activeHint) {
                parentWindow.__wikiliveActiveHints[draftKey] = activeHint;
                parentWindow.sessionStorage.setItem(hintKey, activeHint);
            } else {
                activeHint = parentWindow.__wikiliveActiveHints[draftKey] || parentWindow.sessionStorage.getItem(hintKey) || "";
            }
        }

        function syncHiddenState() {
            const raw = serializeEditor();
            storeDraft(raw);
            setHiddenValue(raw);
        }

        function attachSaveSync() {
            parentDoc.querySelectorAll("button").forEach((button) => {
                const text = (button.textContent || "").trim();
                if (text !== "Сохранить" || button.dataset.wikiliveSaveSync === "1") {
                    return;
                }
                button.dataset.wikiliveSaveSync = "1";
                button.addEventListener("mousedown", () => syncHiddenState(), true);
            });
        }

        function hideContextMenu() {
            contextMenu.style.display = "none";
        }

        function refreshContextMenu() {
            ensureActiveSnippetState();
            contextInsertButton.disabled = !activeSnippet;
            contextHintNode.textContent = activeHint || (activeSnippet ? "Готово к вставке" : "Сначала выбери диапазон в таблице");
        }

        function showContextMenu(x, y) {
            refreshContextMenu();
            contextMenu.style.left = `${Math.min(x, window.innerWidth - 240)}px`;
            contextMenu.style.top = `${Math.min(y, window.innerHeight - 140)}px`;
            contextMenu.style.display = "block";
        }

        function openPicker() {
            const button = Array.from(parentDoc.querySelectorAll("button")).find((node) => {
                const text = (node.textContent || "").trim();
                return text === "Таблица" || text === "Скрыть таблицу";
            });
            if (button) {
                button.click();
            }
        }

        function closestObjectNode(node) {
            if (!node) {
                return null;
            }
            if (node.nodeType === Node.ELEMENT_NODE) {
                return node.closest("[data-raw]");
            }
            if (node.parentElement) {
                return node.parentElement.closest("[data-raw]");
            }
            return null;
        }

        function clearSelectedObject() {
            if (selectedObject) {
                selectedObject.classList.remove("is-selected");
            }
            selectedObject = null;
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            delete parentWindow.__wikiliveSelectedObjects[draftKey];
            parentWindow.sessionStorage.removeItem(selectedKey);
        }

        function selectObject(node) {
            clearSelectedObject();
            selectedObject = node;
            selectedObject.classList.add("is-selected");
            const formulaIndex = selectedObject.dataset.formulaIndex || "";
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            parentWindow.__wikiliveSelectedObjects[draftKey] = formulaIndex;
            parentWindow.sessionStorage.setItem(selectedKey, formulaIndex);
        }

        function restoreSelectedObject() {
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            const storedIndex = parentWindow.__wikiliveSelectedObjects[draftKey] || parentWindow.sessionStorage.getItem(selectedKey);
            if (!storedIndex) {
                return;
            }
            const node = editor.querySelector(`[data-formula-index="${storedIndex}"]`);
            if (node) {
                selectedObject = node;
                selectedObject.classList.add("is-selected");
            }
        }

        function createTextNode(text) {
            return document.createTextNode(text);
        }

        function createObjectNode(raw, tableId, recordId, fieldName, formulaIndex) {
            const meta = lookup[`${tableId}::${recordId}::${fieldName}`] || {
                value: "живое поле",
                resourceUrl: "",
                mimeType: "",
                isImage: false,
            };

            if (meta.isImage && meta.resourceUrl) {
                const figure = document.createElement("figure");
                figure.className = "wl-object wl-image";
                figure.contentEditable = "false";
                figure.draggable = true;
                figure.dataset.raw = raw;
                figure.dataset.formulaIndex = String(formulaIndex);

                const image = document.createElement("img");
                image.src = meta.resourceUrl;
                image.alt = meta.value || fieldName;
                figure.appendChild(image);

                const metaRow = document.createElement("div");
                metaRow.className = "wl-image__meta";

                const indexNode = document.createElement("span");
                indexNode.className = "wl-object__index";
                indexNode.textContent = `#${formulaIndex + 1}`;
                metaRow.appendChild(indexNode);

                const fieldNode = document.createElement("span");
                fieldNode.className = "wl-object__field";
                fieldNode.textContent = fieldName;
                metaRow.appendChild(fieldNode);
                figure.appendChild(metaRow);

                const caption = document.createElement("div");
                caption.className = "wl-image__name";
                caption.textContent = meta.value || fieldName;
                figure.appendChild(caption);
                return figure;
            }

            const chip = document.createElement("span");
            chip.className = "wl-object";
            chip.contentEditable = "false";
            chip.draggable = true;
            chip.dataset.raw = raw;
            chip.dataset.formulaIndex = String(formulaIndex);

            const indexNode = document.createElement("span");
            indexNode.className = "wl-object__index";
            indexNode.textContent = `#${formulaIndex + 1}`;
            chip.appendChild(indexNode);

            const fieldNode = document.createElement("span");
            fieldNode.className = "wl-object__field";
            fieldNode.textContent = fieldName;
            chip.appendChild(fieldNode);

            const valueNode = document.createElement("span");
            valueNode.className = "wl-object__value";
            valueNode.textContent = meta.value || "живое поле";
            chip.appendChild(valueNode);
            return chip;
        }

        function renderInline(target, text, state) {
            tokenRegex.lastIndex = 0;
            let cursor = 0;
            let match;
            while ((match = tokenRegex.exec(text)) !== null) {
                if (match.index > cursor) {
                    target.appendChild(createTextNode(text.slice(cursor, match.index)));
                }
                target.appendChild(createObjectNode(match[0], match[1], match[2], match[3], state.formulaIndex++));
                cursor = tokenRegex.lastIndex;
            }
            if (cursor < text.length) {
                target.appendChild(createTextNode(text.slice(cursor)));
            }
            if (!target.childNodes.length) {
                target.appendChild(document.createElement("br"));
            }
        }

        function createLineBlock(kind, text, state) {
            const line = document.createElement("div");
            line.className = "wl-line";
            line.dataset.kind = kind;
            renderInline(line, text, state);
            return line;
        }

        function isTableLine(line) {
            const stripped = line.trim();
            return stripped.startsWith("|") && stripped.endsWith("|") && stripped.length > 2;
        }

        function parseTableCells(line) {
            return line.trim().slice(1, -1).split("|").map((cell) => cell.trim());
        }

        function isTableSeparator(line) {
            const cells = parseTableCells(line);
            return cells.length > 0 && cells.every((cell) => tableSeparatorRegex.test(cell));
        }

        function createTableBlock(blockRaw, headerCells, bodyRows, state) {
            const wrap = document.createElement("div");
            wrap.className = "wl-table-block";
            wrap.dataset.kind = "table";
            wrap.dataset.blockRaw = blockRaw;
            wrap.contentEditable = "false";

            const table = document.createElement("table");
            table.className = "wl-table";

            const thead = document.createElement("thead");
            const headRow = document.createElement("tr");
            headerCells.forEach((cell) => {
                const th = document.createElement("th");
                renderInline(th, cell, state);
                headRow.appendChild(th);
            });
            thead.appendChild(headRow);
            table.appendChild(thead);

            const tbody = document.createElement("tbody");
            bodyRows.forEach((row) => {
                const tr = document.createElement("tr");
                row.forEach((cell) => {
                    const td = document.createElement("td");
                    renderInline(td, cell, state);
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            wrap.appendChild(table);
            return wrap;
        }

        function renderRaw(raw) {
            isRendering = true;
            clearSelectedObject();
            editor.innerHTML = "";
            const state = { formulaIndex: 0 };
            const lines = String(raw || "").split("\n");
            let index = 0;
            while (index < lines.length) {
                const line = lines[index];
                const trimmed = line.trim();

                if (isTableLine(trimmed) && index + 1 < lines.length && isTableLine(lines[index + 1].trim()) && isTableSeparator(lines[index + 1].trim())) {
                    const blockLines = [line, lines[index + 1]];
                    const headerCells = parseTableCells(trimmed);
                    const bodyRows = [];
                    index += 2;
                    while (index < lines.length && isTableLine(lines[index].trim())) {
                        const rowLine = lines[index];
                        const rowCells = parseTableCells(rowLine);
                        if (rowCells.length !== headerCells.length) {
                            break;
                        }
                        blockLines.push(rowLine);
                        bodyRows.push(rowCells);
                        index += 1;
                    }
                    editor.appendChild(createTableBlock(blockLines.join("\n"), headerCells, bodyRows, state));
                    continue;
                }

                if (trimmed.startsWith("## ")) {
                    editor.appendChild(createLineBlock("heading", line.slice(line.indexOf("## ") + 3), state));
                } else if (trimmed.startsWith("> ")) {
                    editor.appendChild(createLineBlock("callout", line.slice(line.indexOf("> ") + 2), state));
                } else {
                    editor.appendChild(createLineBlock("line", line, state));
                }
                index += 1;
            }

            if (!editor.childNodes.length) {
                editor.appendChild(createLineBlock("line", "", state));
            }
            restoreSelectedObject();
            isRendering = false;
        }

        function serializeInlineNode(node) {
            if (node.nodeType === Node.TEXT_NODE) {
                return (node.textContent || "").replace(/\u00a0/g, " ");
            }
            if (node.nodeType !== Node.ELEMENT_NODE) {
                return "";
            }
            const element = node;
            if (element.dataset && element.dataset.raw) {
                return element.dataset.raw;
            }
            if (element.tagName === "BR") {
                return "";
            }
            return Array.from(element.childNodes).map(serializeInlineNode).join("");
        }

        function serializeBlockNode(node) {
            if (node.nodeType === Node.TEXT_NODE) {
                return (node.textContent || "").replace(/\u00a0/g, " ");
            }
            if (node.nodeType !== Node.ELEMENT_NODE) {
                return "";
            }
            const element = node;
            if (element.dataset && element.dataset.kind === "table") {
                return element.dataset.blockRaw || "";
            }
            const kind = element.dataset.kind || "line";
            const text = Array.from(element.childNodes).map(serializeInlineNode).join("");
            if (kind === "heading") {
                return `## ${text}`;
            }
            if (kind === "callout") {
                return `> ${text}`;
            }
            return text;
        }

        function serializeEditor() {
            const blocks = Array.from(editor.childNodes).map(serializeBlockNode);
            return blocks.join("\n");
        }

        function queueDraftStore() {
            if (storeTimer !== null) {
                window.clearTimeout(storeTimer);
            }
            storeTimer = window.setTimeout(() => {
                storeDraft(serializeEditor());
            }, 220);
        }

        function queueRememberSelection() {
            if (selectionTimer !== null) {
                window.clearTimeout(selectionTimer);
            }
            selectionTimer = window.setTimeout(() => {
                rememberSelection();
            }, 0);
        }

        function replaceFormulaAtIndex(raw, targetIndex, replacement) {
            let currentIndex = 0;
            tokenRegex.lastIndex = 0;
            return raw.replace(tokenRegex, (match) => {
                if (currentIndex === targetIndex) {
                    currentIndex += 1;
                    return replacement;
                }
                currentIndex += 1;
                return match;
            });
        }

        function renderAndStore(raw) {
            storeDraft(raw);
            renderRaw(raw);
            placeCaretAtEnd();
        }

        function placeCaretAtEnd() {
            editor.focus();
            const range = document.createRange();
            range.selectNodeContents(editor);
            range.collapse(false);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            lastRange = range.cloneRange();
        }

        function rememberSelection() {
            const selection = window.getSelection();
            if (!selection || selection.rangeCount === 0) {
                return;
            }
            const range = selection.getRangeAt(0);
            if (editor.contains(range.startContainer) && editor.contains(range.endContainer)) {
                lastRange = range.cloneRange();
            }
        }

        function restoreSelection() {
            if (!lastRange) {
                return false;
            }
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(lastRange);
            return true;
        }

        function rangeFromPoint(x, y) {
            if (document.caretRangeFromPoint) {
                return document.caretRangeFromPoint(x, y);
            }
            if (document.caretPositionFromPoint) {
                const position = document.caretPositionFromPoint(x, y);
                if (!position) {
                    return null;
                }
                const range = document.createRange();
                range.setStart(position.offsetNode, position.offset);
                range.collapse(true);
                return range;
            }
            return null;
        }

        function insertSnippet(snippet) {
            if (!snippet) {
                return;
            }

            if (selectedObject && selectedObject.dataset.formulaIndex !== undefined) {
                const raw = serializeEditor();
                const nextRaw = replaceFormulaAtIndex(raw, Number(selectedObject.dataset.formulaIndex), snippet);
                clearSelectedObject();
                renderAndStore(nextRaw);
                return;
            }

            editor.focus();
            if (!restoreSelection()) {
                placeCaretAtEnd();
            }
            document.execCommand("insertText", false, snippet);
            renderAndStore(serializeEditor());
            hideContextMenu();
        }

        editor.addEventListener("click", (event) => {
            const objectNode = closestObjectNode(event.target);
            if (objectNode && editor.contains(objectNode)) {
                event.preventDefault();
                event.stopPropagation();
                selectObject(objectNode);
                openPicker();
                return;
            }
            clearSelectedObject();
            hideContextMenu();
            rememberSelection();
        });

        editor.addEventListener("keydown", (event) => {
            if (selectedObject && (event.key === "Backspace" || event.key === "Delete")) {
                event.preventDefault();
                selectedObject.remove();
                clearSelectedObject();
                renderAndStore(serializeEditor());
                return;
            }
            queueRememberSelection();
        });

        editor.addEventListener("input", () => {
            if (isRendering) {
                return;
            }
            queueDraftStore();
            queueRememberSelection();
        });

        editor.addEventListener("paste", (event) => {
            event.preventDefault();
            const text = (event.clipboardData || window.clipboardData).getData("text/plain");
            document.execCommand("insertText", false, text);
            queueDraftStore();
        });

        editor.addEventListener("mouseup", rememberSelection);
        editor.addEventListener("keyup", queueRememberSelection);

        editor.addEventListener("dragstart", (event) => {
            const objectNode = closestObjectNode(event.target);
            if (!objectNode) {
                return;
            }
            dragSourceNode = objectNode;
            dragRaw = objectNode.dataset.raw || "";
            event.dataTransfer.setData("text/plain", dragRaw);
            event.dataTransfer.effectAllowed = "move";
        });

        editor.addEventListener("dragover", (event) => {
            if (dragRaw) {
                event.preventDefault();
            }
        });

        editor.addEventListener("drop", (event) => {
            if (!dragRaw) {
                return;
            }
            event.preventDefault();
            const range = rangeFromPoint(event.clientX, event.clientY);
            if (dragSourceNode) {
                dragSourceNode.remove();
            }
            if (range) {
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                lastRange = range.cloneRange();
            } else {
                placeCaretAtEnd();
            }
            document.execCommand("insertText", false, dragRaw);
            const nextRaw = serializeEditor();
            dragRaw = "";
            dragSourceNode = null;
            renderAndStore(nextRaw);
        });

        editor.addEventListener("contextmenu", (event) => {
            event.preventDefault();
            const objectNode = closestObjectNode(event.target);
            if (objectNode && editor.contains(objectNode)) {
                selectObject(objectNode);
            } else {
                clearSelectedObject();
                const range = rangeFromPoint(event.clientX, event.clientY);
                if (range) {
                    const selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                    lastRange = range.cloneRange();
                } else {
                    rememberSelection();
                }
            }
            showContextMenu(event.clientX, event.clientY);
        });

        contextOpenButton.addEventListener("click", () => {
            openPicker();
            hideContextMenu();
        });

        contextInsertButton.addEventListener("click", () => {
            ensureActiveSnippetState();
            if (activeSnippet) {
                insertSnippet(activeSnippet);
            }
        });

        document.addEventListener("click", (event) => {
            if (!contextMenu.contains(event.target)) {
                hideContextMenu();
            }
        }, true);
        document.addEventListener("scroll", hideContextMenu, true);

        parentWindow.__wikiliveInsertSnippet = insertSnippet;
        parentWindow.__wikiliveSyncEditor = syncHiddenState;
        parentWindow.__wikiliveSetActiveSnippet = (snippet, hint) => {
            activeSnippet = snippet || "";
            activeHint = hint || "";
            ensureActiveSnippetState();
            refreshContextMenu();
        };

        attachSaveSync();
        window.setTimeout(attachSaveSync, 300);
        window.setTimeout(attachSaveSync, 1200);

        ensureActiveSnippetState();
        const initialRaw = loadDraft();
        renderRaw(initialRaw);
        storeDraft(initialRaw);
        placeCaretAtEnd();
        </script>
    """
    html = html.replace("__WIKILIVE_LOOKUP__", json.dumps(insert_lookup, ensure_ascii=False))
    html = html.replace("__WIKILIVE_DRAFT_KEY__", json.dumps(draft_key))
    html = html.replace("__WIKILIVE_ACTIVE_SNIPPET__", json.dumps(active_snippet))
    html = html.replace("__WIKILIVE_ACTIVE_HINT__", json.dumps(active_hint))
    components.html(html, height=860)


def history_panel(client: ApiClient) -> None:
    page_id = st.session_state.selected_page_id
    if not page_id:
        st.markdown('<div class="tiny">Сначала сохрани страницу</div>', unsafe_allow_html=True)
        return

    version_label = st.text_input(" ", key="version_note", placeholder="Снимок версии", label_visibility="collapsed")
    if st.button("Создать снимок", use_container_width=True):
        try:
            save_page(client)
            client.create_version(page_id, version_label.strip() or "Manual snapshot")
            st.session_state.last_success = "Версия сохранена."
            st.rerun()
        except ApiClientError as exc:
            st.session_state.last_error = str(exc)
            st.rerun()

    try:
        versions = client.list_versions(page_id)
    except ApiClientError as exc:
        st.session_state.last_error = str(exc)
        return

    if not versions:
        st.markdown('<div class="tiny">История пока пуста</div>', unsafe_allow_html=True)
        return

    for version in versions[:12]:
        title = escape(version.get("label") or version.get("createdAt") or "Версия")
        meta = escape(version.get("createdAt", ""))
        author = escape(version.get("author", "system"))
        st.markdown(
            f'<div class="formula"><strong>{title}</strong><div class="tiny">{meta} · {author}</div></div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "Восстановить",
            key=f"restore-{version.get('versionId', '')}",
            use_container_width=True,
        ):
            try:
                restored = client.restore_version(page_id, version["versionId"])
                st.session_state.editor_title = restored.get("title", "")
                st.session_state.editor_content = restored.get("content", "")
                st.session_state.preview_html = restored.get("renderedHtml", "")
                st.session_state.last_success = "Версия восстановлена."
                st.rerun()
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
                st.rerun()


def comments_panel(client: ApiClient) -> None:
    page_id = st.session_state.selected_page_id
    if not page_id:
        st.markdown('<div class="tiny">Сначала сохрани страницу</div>', unsafe_allow_html=True)
        return

    st.text_input(" ", key="comment_selection", placeholder="Метка места", label_visibility="collapsed")
    st.text_area(" ", key="comment_body", placeholder="Комментарий", label_visibility="collapsed", height=96)
    if st.button("Добавить комментарий", use_container_width=True):
        body = st.session_state.comment_body.strip()
        if body:
            try:
                client.create_comment(page_id, body, st.session_state.comment_selection.strip())
                st.session_state.comment_body = ""
                st.session_state.comment_selection = ""
                st.session_state.last_success = "Комментарий добавлен."
                st.rerun()
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
                st.rerun()

    try:
        threads = client.list_comments(page_id)
    except ApiClientError as exc:
        st.session_state.last_error = str(exc)
        return

    if not threads:
        st.markdown('<div class="tiny">Комментариев пока нет</div>', unsafe_allow_html=True)
        return

    for thread in threads:
        thread_id = thread.get("threadId", "")
        messages = thread.get("messages", [])
        first = messages[0] if messages else {}
        selection = escape(comment_selection_preview(thread.get("selectionLabel", "")))
        header = escape(first.get("body", "Комментарий"))
        meta_bits = [escape(first.get("author", "viewer"))]
        if selection:
            meta_bits.append(selection)
        if thread.get("resolved"):
            meta_bits.append("resolved")
        meta_line = " · ".join(bit for bit in meta_bits if bit)
        st.markdown(
            f'<div class="formula"><strong>{header}</strong><div class="tiny">{meta_line}</div></div>',
            unsafe_allow_html=True,
        )
        if messages[1:]:
            for reply in messages[1:]:
                st.markdown(
                    f'<div class="tiny" style="margin:.25rem 0 .4rem 0">{escape(reply.get("author", ""))}: {escape(reply.get("body", ""))}</div>',
                    unsafe_allow_html=True,
                )

        action_left, action_mid, action_right = st.columns([1, 1, 1], gap="small")
        with action_left:
            if st.button(
                f"Лайк {int(thread.get('likeCount', 0))}",
                key=f"like-{thread_id}",
                use_container_width=True,
            ):
                try:
                    client.toggle_comment_like(page_id, thread_id)
                    st.rerun()
                except ApiClientError as exc:
                    st.session_state.last_error = str(exc)
                    st.rerun()
        with action_mid:
            resolve_label = "Открыть" if thread.get("resolved") else "Решить"
            if st.button(resolve_label, key=f"resolve-{thread_id}", use_container_width=True):
                try:
                    client.resolve_comment(page_id, thread_id, not bool(thread.get("resolved", False)))
                    st.rerun()
                except ApiClientError as exc:
                    st.session_state.last_error = str(exc)
                    st.rerun()
        with action_right:
            if st.button("Ответить", key=f"reply-send-{thread_id}", use_container_width=True):
                reply_key = f"reply-value-{thread_id}"
                reply_text = st.session_state.get(reply_key, "").strip()
                if reply_text:
                    try:
                        client.reply_to_comment(page_id, thread_id, reply_text)
                        st.session_state[reply_key] = ""
                        st.rerun()
                    except ApiClientError as exc:
                        st.session_state.last_error = str(exc)
                        st.rerun()
        st.text_input(
            " ",
            key=f"reply-value-{thread_id}",
            placeholder="Ответ",
            label_visibility="collapsed",
        )


def documents_popover(client: ApiClient, pages: list[dict[str, Any]]) -> None:
    documents_tab, history_tab, comments_tab = st.tabs(["Страницы", "История", "Комментарии"])

    with documents_tab:
        st.text_input(" ", key="page_search", placeholder="Поиск", label_visibility="collapsed")
        search = st.session_state.page_search.strip().lower()
        filtered = [page for page in pages if search in page_label(page).lower()]
        if st.session_state.selected_page_id and st.button("Удалить текущую", use_container_width=True):
            delete_document(client)
            st.rerun()
        for page in filtered:
            if st.button(page_label(page), key=f"page-{page.get('pageId', '')}", use_container_width=True):
                try:
                    load_page(client, page["pageId"])
                    st.rerun()
                except ApiClientError as exc:
                    st.session_state.last_error = str(exc)

    with history_tab:
        history_panel(client)

    with comments_tab:
        comments_panel(client)


def tables_popover(client: ApiClient) -> None:
    st.text_input(" ", key="table_search", placeholder="Таблицы", label_visibility="collapsed")
    visible = [preset for preset in st.session_state.presets if st.session_state.table_search.strip().lower() in preset["label"].lower()]
    st.multiselect(
        " ",
        options=[preset["key"] for preset in visible],
        format_func=lambda key: get_preset(key).get("label", key) if get_preset(key) else key,
        key="selected_table_keys",
        label_visibility="collapsed",
    )
    if st.button("Обновить", use_container_width=True):
        fetch_insert_options(client, force=True)
        for preset in selected_presets():
            fetch_insert_options(client, preset["tableId"], preset["viewId"] or None, force=True)
        st.rerun()


def preview_popover() -> None:
    body = st.session_state.preview_html.strip() or '<div class="tiny">пусто</div>'
    st.markdown(f'<div class="panel">{body}</div>', unsafe_allow_html=True)


def render_panel_shell(title: str) -> None:
    st.markdown(f'<div class="panel"><div class="tiny" style="margin-bottom:.55rem">{escape(title)}</div>', unsafe_allow_html=True)


def close_panel_shell() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def comment_selection_preview(label: str) -> str:
    raw = str(label or "").strip()
    if not raw:
        return ""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if not isinstance(parsed, dict):
        return raw
    return str(parsed.get("preview") or parsed.get("blockPreview") or "").strip()


def render_insert_workspace(client: ApiClient) -> tuple[str, str]:
    presets = selected_presets()
    if not presets:
        st.markdown('<div class="tiny">Выбери таблицу в кнопке Таблицы</div>', unsafe_allow_html=True)
        return "", ""

    if st.session_state.active_table_key not in {preset["key"] for preset in presets}:
        st.session_state.active_table_key = presets[0]["key"]

    outer_left, outer_center, outer_right = st.columns([0.06, 1, 0.06], gap="small")
    with outer_center:
        top_left, top_mid, top_right = st.columns([3, 1, 1], gap="small")
        with top_left:
            st.selectbox(
                " ",
                options=[preset["key"] for preset in presets],
                format_func=lambda key: get_preset(key).get("label", key) if get_preset(key) else key,
                key="active_table_key",
                label_visibility="collapsed",
            )
        with top_mid:
            if st.button("Обновить", use_container_width=True, key="refresh-active-table"):
                active_preset = get_preset(st.session_state.active_table_key)
                if active_preset is not None:
                    fetch_insert_options(
                        client,
                        active_preset["tableId"],
                        active_preset["viewId"] or None,
                        force=True,
                    )
                st.rerun()
        with top_right:
            if st.button("Скрыть", use_container_width=True, key="hide-insert-picker"):
                st.session_state.active_panel = ""
                st.rerun()

        st.radio(
            " ",
            options=["cells", "table", "blocks"],
            key="insert_mode",
            horizontal=True,
            format_func=lambda value: {
                "cells": "Ячейки",
                "table": "Таблица",
                "blocks": "Блоки",
            }.get(value, value),
            label_visibility="collapsed",
        )

        payload = active_table_payload(client)
        if payload is None:
            st.markdown('<div class="tiny">Не удалось загрузить таблицу</div>', unsafe_allow_html=True)
            return "", ""

        total_rows = len(payload.get("records", []))
        row_limit = max(50, int(st.session_state.insert_row_limit))
        visible_payload = dict(payload)
        visible_payload["records"] = payload.get("records", [])[:row_limit]
        dataframe, records, field_names = build_table_dataframe(visible_payload)
        if dataframe.empty or not field_names:
            st.markdown('<div class="tiny">В таблице нет данных</div>', unsafe_allow_html=True)
            return "", ""

        if total_rows > row_limit:
            st.markdown(
                f'<div class="tiny" style="margin:.1rem 0 .45rem">Показано {row_limit} из {total_rows}</div>',
                unsafe_allow_html=True,
            )
            if st.button("Еще 100", key=f"more-rows-{st.session_state.active_table_key}", use_container_width=True):
                st.session_state.insert_row_limit = row_limit + 100
                st.rerun()

        selection_event = st.dataframe(
            dataframe,
            width=860,
            height=360,
            on_select="rerun",
            selection_mode="multi-cell",
            key=f"insert-grid-{st.session_state.active_table_key}",
            row_height=34,
        )
        cells = extract_cells(selection_event)
        mode = st.session_state.insert_mode
        if mode == "table":
            snippet, _preview, hint = build_table_selection_snippet(visible_payload, cells)
        elif mode == "blocks":
            snippet, _preview, hint = build_block_selection_snippet(visible_payload, cells)
        else:
            snippet, _preview, hint = build_selection_snippet(visible_payload, cells)
        if not snippet:
            st.markdown('<div class="tiny">Выдели ячейку или диапазон</div>', unsafe_allow_html=True)
            return "", ""

        st.session_state.latest_insert_snippet = snippet
        st.session_state.latest_insert_hint = hint
        st.markdown(f'<div class="tiny" style="margin:.2rem 0 .45rem">{escape(hint)}</div>', unsafe_allow_html=True)
        render_insert_button(snippet, hint)
        return snippet, hint


def formulas_panel() -> None:
    tokens = extract_formula_tokens(st.session_state.editor_content)
    if not tokens:
        return
    for token in tokens[:6]:
        label, value = describe_formula(token, st.session_state.catalog)
        st.markdown(
            f"""
            <div class="formula">
                <strong>{escape(label)}</strong>
                <div class="tiny">{escape(value)}</div>
                <div class="raw">{escape(token.raw)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(page_title="WikiLive", page_icon="M", layout="wide", initial_sidebar_state="collapsed")
    inject_css()
    ensure_state()
    client = api()

    fetch_insert_options(client)
    pages: list[dict[str, Any]] = list(st.session_state.pages_cache) if st.session_state.pages_cache_loaded else []
    token = ""
    hint = ""

    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        st.session_state.last_error = ""
    if st.session_state.last_success:
        st.success(st.session_state.last_success)
        st.session_state.last_success = ""

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1], gap="small")
    with col1:
        if st.button("Новый", use_container_width=True):
            reset_document()
            st.rerun()
    with col2:
        if st.button("Сохранить", use_container_width=True, type="primary"):
            save_page(client)
            st.rerun()
    with col3:
        if st.button("Скрыть таблицу" if st.session_state.active_panel == "insert" else "Таблица", use_container_width=True):
            st.session_state.active_panel = "" if st.session_state.active_panel == "insert" else "insert"
            st.rerun()
    with col4:
        if st.button("Документы", use_container_width=True):
            st.session_state.active_panel = "" if st.session_state.active_panel == "documents" else "documents"
            st.rerun()
    with col5:
        if st.button("Таблицы", use_container_width=True):
            st.session_state.active_panel = "" if st.session_state.active_panel == "tables" else "tables"
            st.rerun()

    if st.session_state.active_panel == "documents":
        pages = list_pages(client)
        render_panel_shell("Документы")
        documents_popover(client, pages)
        close_panel_shell()
    elif st.session_state.active_panel == "tables":
        render_panel_shell("Таблицы")
        tables_popover(client)
        close_panel_shell()
    elif st.session_state.active_panel == "insert":
        st.markdown('<div id="wikilive-picker-open"></div>', unsafe_allow_html=True)
        render_panel_shell("Выбор из таблицы")
        token, hint = render_insert_workspace(client)
        close_panel_shell()

    draft_key = st.session_state.selected_page_id or f"new-{st.session_state.new_draft_id}"
    st.text_area("Текст", key="editor_content", placeholder="", label_visibility="collapsed")
    render_editor_shell(
        build_editor_lookup_payload(st.session_state.catalog),
        draft_key,
        st.session_state.latest_insert_snippet,
        st.session_state.latest_insert_hint,
        st.session_state.selected_page_id,
        URL,
    )


if __name__ == "__main__":
    main()
