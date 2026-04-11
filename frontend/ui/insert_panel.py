from __future__ import annotations

from typing import Any

import streamlit as st

from ui.state import (
    append_snippet,
    build_table_block,
    file_to_attachment_snippet,
    page_title_of,
    redo_draft,
    undo_draft,
)
from utils.document_tools import build_formula_token


def _apply_snippet(snippet: str) -> None:
    append_snippet(snippet)
    st.rerun()


def render_insert_toolbar(pages: list[dict[str, Any]], insert_options: dict[str, Any]) -> None:
    toolbar = st.columns([0.72, 0.72, 0.72, 0.72, 0.78, 0.78, 0.78, 0.78, 0.9, 0.9, 0.9, 0.9])

    with toolbar[0]:
        if st.button("↶", key="toolbar-undo", help="Отменить\nCtrl+Z", use_container_width=True):
            if undo_draft():
                st.rerun()
    with toolbar[1]:
        if st.button("↷", key="toolbar-redo", help="Повторить\nCtrl+Shift+Z", use_container_width=True):
            if redo_draft():
                st.rerun()
    with toolbar[2]:
        if st.button("B", key="toolbar-bold", help="Жирный\nCtrl+B", use_container_width=True):
            _apply_snippet("**Жирный текст**")
    with toolbar[3]:
        if st.button("I", key="toolbar-italic", help="Курсив\nCtrl+I", use_container_width=True):
            _apply_snippet("*Курсив*")
    with toolbar[4]:
        if st.button("H1", key="toolbar-h1", help="Заголовок 1\nCtrl+Alt+1", use_container_width=True):
            _apply_snippet("# Новый заголовок")
    with toolbar[5]:
        if st.button("H2", key="toolbar-h2", help="Заголовок 2\nCtrl+Alt+2", use_container_width=True):
            _apply_snippet("## Новый заголовок")
    with toolbar[6]:
        if st.button("•", key="toolbar-list", help="Маркированный список\nCtrl+Shift+7", use_container_width=True):
            _apply_snippet("- Новый пункт")
    with toolbar[7]:
        if st.button("1.", key="toolbar-olist", help="Нумерованный список\nCtrl+Shift+8", use_container_width=True):
            _apply_snippet("1. Новый пункт")
    with toolbar[8]:
        with st.popover("@", use_container_width=True):
            _render_table_insert_popover(insert_options)
    with toolbar[9]:
        with st.popover("🔗", use_container_width=True):
            _render_link_insert_popover(pages)
    with toolbar[10]:
        if st.button("❝", key="toolbar-quote", help="Цитата\nCtrl+Shift+.", use_container_width=True):
            _apply_snippet("> Новый callout")
    with toolbar[11]:
        with st.popover("🖼", use_container_width=True):
            _render_file_insert_popover()

    st.markdown(
        "<div class='wl-toolbar-note'>Поддерживаются /table, /page, /callout, /heading, а также вставка живых полей MWS, ссылок и вложений.</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Slash-команды и быстрые блоки", expanded=False):
        left, right = st.columns([0.55, 0.45], gap="large")
        with left:
            slash_value = st.text_input(
                "Slash-команда",
                key="slash-command-value",
                placeholder="/table /page /callout /heading /code",
            )
            if st.button("Применить команду", key="apply-slash-command", use_container_width=True):
                command = slash_value.strip().lower()
                if command in {"/heading", "/h1"}:
                    _apply_snippet("# Новый заголовок")
                elif command == "/callout":
                    _apply_snippet("> Новый callout")
                elif command == "/page":
                    _apply_snippet("[[Новая страница]]")
                elif command == "/table":
                    _apply_snippet(build_table_block(insert_options))
                elif command == "/code":
                    _apply_snippet("```python\nprint('hello')\n```")
        with right:
            if st.button("Вставить чеклист", key="insert-checklist", use_container_width=True):
                _apply_snippet("- [ ] Новая задача")
            if st.button("Вставить код", key="insert-code-block", use_container_width=True):
                _apply_snippet("```python\nprint('hello')\n```")


def _render_table_insert_popover(insert_options: dict[str, Any]) -> None:
    table_id = str(insert_options.get("tableId", ""))
    records = insert_options.get("records", [])
    field_names = [str(name) for name in insert_options.get("fieldNames", [])]
    if not table_id or not records or not field_names:
        st.info("MWS-данные пока недоступны.")
        return

    record_map: list[tuple[str, str]] = []
    for record in records:
        fields = record.get("fields", {}) or {}
        label = next((str(value) for value in fields.values() if value), str(record.get("recordId", "")))
        record_map.append((str(record.get("recordId", "")), label))

    record_choice = st.selectbox(
        "Запись",
        options=[record_id for record_id, _ in record_map],
        format_func=lambda value: next((label for record_id, label in record_map if record_id == value), value),
        key="toolbar-record-choice",
    )
    field_choice = st.selectbox("Поле", field_names, key="toolbar-field-choice")
    row_limit = st.slider("Строк в таблице", min_value=3, max_value=20, value=8, key="toolbar-table-row-limit")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Вставить значение", key="toolbar-insert-mws-value", use_container_width=True):
            _apply_snippet(build_formula_token(table_id, record_choice, field_choice))
    with col2:
        if st.button("Вставить таблицу", key="toolbar-insert-mws-table", use_container_width=True):
            _apply_snippet(build_table_block(insert_options, row_limit=row_limit))


def _render_link_insert_popover(pages: list[dict[str, Any]]) -> None:
    label = st.text_input("Label", key="toolbar-link-label")
    url = st.text_input("Filled text / URL", key="toolbar-link-url")
    st.checkbox("Открывать в новой вкладке", value=True, key="toolbar-link-new-tab")
    if st.button("Вставить ссылку", key="toolbar-insert-link", type="primary", use_container_width=True):
        if label.strip() and url.strip():
            _apply_snippet(f"[{label.strip()}]({url.strip()})")

    st.markdown("<div class='wl-divider'></div>", unsafe_allow_html=True)
    page_titles = [page_title_of(page) for page in pages]
    if page_titles:
        selected = st.selectbox("Ссылка на страницу", page_titles, key="toolbar-page-link")
        if st.button("Вставить страницу", key="toolbar-insert-page-link", use_container_width=True):
            _apply_snippet(f"[[{selected}]]")


def _render_file_insert_popover() -> None:
    uploaded_file = st.file_uploader(
        "Файл изображения",
        type=["png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "xls", "xlsx"],
        key="toolbar-uploader",
    )
    if uploaded_file is not None:
        st.caption(f"{uploaded_file.name} · {round(uploaded_file.size / 1024 / 1024, 2)} МБ")
        if st.button("Подтвердить", key="toolbar-insert-file", type="primary", use_container_width=True):
            _apply_snippet(file_to_attachment_snippet(uploaded_file))
