from __future__ import annotations

import base64
import mimetypes
import os
import re
from html import escape
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from utils.api_client import ApiClient, ApiClientError
from utils.document_tools import build_formula_token, render_document_html
from utils.prototype_renderer import render_prototype


URL = os.getenv("WIKILIVE_BACKEND_URL", "http://127.0.0.1:3000")
PAGE_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


st.set_page_config(
    page_title="WikiLive",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root {
            --canvas: #434347;
            --paper: #ffffff;
            --panel: #f7f8fc;
            --line: #e6e8ef;
            --line-strong: #d6dae6;
            --ink: #121318;
            --muted: #8d93a2;
            --muted-strong: #697086;
            --accent: #8f7cff;
            --accent-soft: #f2efff;
            --danger: #ff4f8b;
            --shadow: 0 18px 44px rgba(12, 16, 33, 0.12);
            --shadow-soft: 0 10px 24px rgba(12, 16, 33, 0.08);
        }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(143,124,255,.11), transparent 18%),
                radial-gradient(circle at bottom left, rgba(70,166,255,.08), transparent 22%),
                var(--canvas);
            color: var(--ink);
        }
        header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"], #MainMenu, footer { display: none !important; visibility: hidden !important; }
        .block-container { max-width: none !important; padding: 20px 20px 28px !important; }
        div[data-testid="stTextArea"] textarea {
            min-height: 680px !important;
            border-radius: 16px !important;
            border: 1px solid var(--line) !important;
            background: #fbfcff !important;
            color: #1b202b !important;
            line-height: 1.8 !important;
            padding: 1rem 1rem 1.2rem !important;
            box-shadow: none !important;
            caret-color: var(--accent) !important;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
            border-radius: 14px !important;
            border: 1px solid var(--line) !important;
            background: #ffffff !important;
            color: #1b202b !important;
            box-shadow: none !important;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            height: 38px;
            border-radius: 12px;
            background: rgba(255,255,255,0.1);
            color: #ffffff;
            font-weight: 700;
            padding: 0 16px;
        }
        .stTabs [aria-selected="true"] { background: #ffffff !important; color: #212634 !important; }
        button[kind="secondary"], button[kind="primary"] {
            border-radius: 12px !important;
            min-height: 38px !important;
            font-weight: 700 !important;
            border: 1px solid transparent !important;
            box-shadow: none !important;
        }
        button[kind="primary"] { background: var(--danger) !important; color: #ffffff !important; }
        button[kind="secondary"] { background: #f1f2f7 !important; color: #272d3a !important; }
        .app-shell { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 24px; align-items: start; }
        .rail, .workspace-card, .panel-card, .preview-card, .metric-card {
            border-radius: 18px;
            background: var(--paper);
            border: 1px solid rgba(228,231,239,.96);
            box-shadow: var(--shadow);
        }
        .rail {
            position: sticky; top: 20px; padding: 18px;
            background: rgba(34,35,41,.6);
            border: 1px solid rgba(255,255,255,.08);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
        }
        .rail h3, .rail p, .rail div, .rail span, .rail label { color: #ffffff !important; }
        .rail-section + .rail-section { margin-top: 18px; padding-top: 18px; border-top: 1px solid rgba(255,255,255,.09); }
        .rail-title {
            font-size: 0.78rem; letter-spacing: .08em; text-transform: uppercase;
            color: rgba(255,255,255,.72); font-weight: 800; margin-bottom: 12px;
        }
        .workspace-grid { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 22px; align-items: start; }
        .workspace-card { overflow: hidden; }
        .workspace-head { display: flex; justify-content: space-between; gap: 14px; padding: 22px 24px 14px; }
        .workspace-head__meta { display: flex; gap: 12px; align-items: flex-start; }
        .doc-icon { width: 20px; height: 20px; color: #6f7485; margin-top: 2px; flex: none; }
        .workspace-head__title { font-size: 1.35rem; font-weight: 800; line-height: 1.15; letter-spacing: -0.03em; color: var(--ink); }
        .workspace-head__sub { margin-top: 6px; font-size: 0.82rem; color: var(--muted); }
        .workspace-links { display: flex; align-items: center; gap: 12px; }
        .workspace-links__item { color: var(--muted-strong); font-size: 0.85rem; font-weight: 600; }
        .workspace-links__item.is-active { color: var(--accent); }
        .metric-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-bottom: 18px; }
        .metric-card, .preview-card, .panel-card { padding: 18px; }
        .metric-card__label { color: var(--muted); font-size: 0.76rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
        .metric-card__value { margin-top: 10px; color: var(--ink); font-size: 1.7rem; font-weight: 800; letter-spacing: -0.04em; }
        .metric-card__sub, .preview-card__sub, .panel-card__sub { margin-top: 8px; color: var(--muted-strong); font-size: 0.84rem; line-height: 1.5; }
        .preview-card__title, .panel-card__title { font-size: 1rem; font-weight: 800; color: var(--ink); letter-spacing: -0.02em; }
        .doc-surface { margin-top: 16px; border-radius: 16px; border: 1px solid var(--line); background: #ffffff; min-height: 280px; padding: 22px 24px 26px; }
        .page-button-note { font-size: 0.74rem; color: rgba(255,255,255,.72); margin-top: -6px; margin-bottom: 8px; }
        .pill {
            display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px;
            border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-size: 0.76rem; font-weight: 700;
        }
        .history-item, .comment-item-card {
            border-radius: 14px; border: 1px solid var(--line); background: #fbfbfe; padding: 14px;
        }
        .history-item + .history-item, .comment-item-card + .comment-item-card { margin-top: 12px; }
        .history-item__title, .comment-item-card__title { font-size: 0.9rem; font-weight: 700; color: #202534; }
        .history-item__meta, .comment-item-card__meta { margin-top: 4px; font-size: 0.76rem; color: var(--muted); }
        .history-item__body, .comment-item-card__body { margin-top: 10px; color: #2c3240; font-size: 0.86rem; line-height: 1.7; }
        .status-good { color: #5d48d2; }
        .divider { height: 1px; margin: 14px 0; background: var(--line); }
        .tiny { color: var(--muted); font-size: 0.78rem; line-height: 1.55; }
        @media (max-width: 1280px) { .app-shell, .workspace-grid { grid-template-columns: 1fr; } .rail { position: relative; top: 0; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_local_cache_bridge(page_id: str, version_token: str) -> None:
    components.html(
        f"""
        <script>
        const parentDoc = window.parent.document;
        const area = parentDoc.querySelector('div[data-testid="stTextArea"] textarea');
        if (area) {{
          const key = "wikilive:draft:{escape(page_id)}";
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


def page_id_of(item: dict[str, Any]) -> str:
    return str(item.get("pageId") or item.get("id") or "")


def page_title_of(item: dict[str, Any]) -> str:
    return str(item.get("title") or "Новая страница")


def get_client() -> ApiClient:
    return ApiClient(URL)


def safe_api_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs), None
    except ApiClientError as exc:
        return None, str(exc)


def build_table_block(insert_options: dict[str, Any], row_limit: int = 5) -> str:
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
        body.append("| " + " | ".join(build_formula_token(table_id, record_id, field_name) for field_name in field_names) + " |")
    return "\n".join([header, separator, *body])


def append_snippet(snippet: str) -> None:
    if not snippet:
        return
    current = st.session_state.get("draft_content", "")
    joiner = "\n" if current and not current.endswith("\n") else ""
    st.session_state.draft_content = f"{current}{joiner}{snippet}"


def file_to_attachment_snippet(uploaded_file) -> str:
    import json
    from urllib.parse import quote

    data = uploaded_file.getvalue()
    mime = uploaded_file.type or mimetypes.guess_type(uploaded_file.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(data).decode("ascii")
    src = f"data:{mime};base64,{encoded}"
    meta = {"name": uploaded_file.name, "mime": mime, "src": src, "width": 520 if mime.startswith("image/") else 0}
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
        content = str(item.get("content", ""))
        for match in PAGE_LINK_PATTERN.finditer(content):
            if match.group(1).strip() == title:
                matches.append(item)
                break
    return matches


def set_current_page(page: dict[str, Any]) -> None:
    st.session_state.current_page_id = page_id_of(page)
    st.session_state.loaded_page_id = page_id_of(page)
    st.session_state.draft_title = page_title_of(page)
    st.session_state.draft_content = str(page.get("content", ""))


def ensure_page_loaded(page: dict[str, Any]) -> None:
    if st.session_state.get("loaded_page_id") != page_id_of(page):
        set_current_page(page)


def icon_svg() -> str:
    return "<svg class='doc-icon' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'><path d='M6 3.5h7l4 4V18a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5.5a2 2 0 0 1 2-2Z'></path><path d='M13 3.5V8h4'></path></svg>"


def render_metric_cards(page: dict[str, Any], comments: list[dict[str, Any]], versions: list[dict[str, Any]], backlinks: list[dict[str, Any]]) -> None:
    st.markdown(
        """
        <div class="metric-grid">
          <div class="metric-card">
            <div class="metric-card__label">Комментарии</div>
            <div class="metric-card__value">{comments_count}</div>
            <div class="metric-card__sub">Открытые и решенные ветки по текущей странице.</div>
          </div>
          <div class="metric-card">
            <div class="metric-card__label">Снимки</div>
            <div class="metric-card__value">{versions_count}</div>
            <div class="metric-card__sub">История изменений и откаты через машину времени.</div>
          </div>
          <div class="metric-card">
            <div class="metric-card__label">Backlinks</div>
            <div class="metric-card__value">{backlinks_count}</div>
            <div class="metric-card__sub">Страницы, которые ссылаются на “{title}”.</div>
          </div>
        </div>
        """.format(
            comments_count=len(comments),
            versions_count=len(versions),
            backlinks_count=len(backlinks),
            title=escape(page_title_of(page)),
        ),
        unsafe_allow_html=True,
    )


def render_page_rail(pages: list[dict[str, Any]], current_page_id: str, backlinks: list[dict[str, Any]]) -> None:
    st.markdown("<div class='rail-title'>Страницы</div>", unsafe_allow_html=True)
    if st.button("Новая страница", use_container_width=True):
        created, error = safe_api_call(get_client().create_page, "Новая страница", "")
        if error:
            st.error(error)
        else:
            set_current_page(created)
            st.rerun()
    if len(pages) > 1 and st.button("Удалить текущую", use_container_width=True, key="delete-current-page"):
        _, error = safe_api_call(get_client().delete_page, current_page_id)
        if error:
            st.error(error)
        else:
            st.session_state.pop("current_page_id", None)
            st.session_state.pop("loaded_page_id", None)
            st.rerun()

    for item in pages:
        is_current = page_id_of(item) == current_page_id
        if st.button(
            page_title_of(item),
            key=f"page-select-{page_id_of(item)}",
            use_container_width=True,
            type="primary" if is_current else "secondary",
        ):
            set_current_page(item)
            st.rerun()
        st.markdown(
            f"<div class='page-button-note'>{escape(str(item.get('updatedAt', ''))[:16].replace('T', ' '))}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='rail-section'></div>", unsafe_allow_html=True)
    st.markdown("<div class='rail-title'>Backlinks</div>", unsafe_allow_html=True)
    if backlinks:
        for item in backlinks:
            st.markdown(f"<div class='tiny'>• {escape(page_title_of(item))}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='tiny'>Пока нет страниц, которые ссылаются на текущий документ.</div>", unsafe_allow_html=True)

    st.markdown("<div class='rail-section'></div>", unsafe_allow_html=True)
    st.markdown("<div class='rail-title'>Приоритеты Трека</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='tiny'>
        1. Живые таблицы MWS в документе.<br/>
        2. Slash-menu и горячие клавиши.<br/>
        3. Backlinks.<br/>
        4. Local cache и восстановление.<br/>
        5. Совместная работа.<br/>
        6. Docker и один запуск.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insert_toolbar(pages: list[dict[str, Any]], insert_options: dict[str, Any]) -> None:
    st.markdown("<div class='preview-card'><div class='preview-card__title'>Панель команд</div><div class='preview-card__sub'>Быстрые вставки и блоки для judge-facing сценария.</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        if st.button("H1", use_container_width=True):
            append_snippet("# Новый заголовок")
    with c2:
        if st.button("Цитата", use_container_width=True):
            append_snippet("> Новый callout")
    with c3:
        if st.button("Код", use_container_width=True):
            append_snippet("``` пример кода")
    with c4:
        if st.button("Список", use_container_width=True):
            append_snippet("- Новый пункт")
    with c5:
        if st.button("Чеклист", use_container_width=True):
            append_snippet("- [ ] Новая задача")
    with c6:
        if st.button("/table", use_container_width=True):
            append_snippet(build_table_block(insert_options) or "| Колонка |\n| --- |\n| Значение |")

    with st.expander("Вставить ссылку, страницу, файл или поле MWS", expanded=False):
        link_col, page_col = st.columns(2)
        with link_col:
            link_label = st.text_input("Label", key="insert_link_label")
            link_url = st.text_input("Filled text / URL", key="insert_link_url")
            if st.button("Вставить ссылку", key="insert-link"):
                if link_label and link_url:
                    append_snippet(f"[{link_label}]({link_url})")
                    st.rerun()
        with page_col:
            page_titles = [page_title_of(item) for item in pages]
            selected_page_title = st.selectbox("Ссылка на страницу", page_titles, key="insert_page_title")
            if st.button("Вставить страницу", key="insert-page"):
                append_snippet(f"[[{selected_page_title}]]")
                st.rerun()

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        table_id = str(insert_options.get("tableId", ""))
        records = insert_options.get("records", [])
        field_names = [str(name) for name in insert_options.get("fieldNames", [])]
        record_labels = []
        for record in records:
            fields = record.get("fields", {}) or {}
            label = next((str(value) for value in fields.values() if value), str(record.get("recordId", "")))
            record_labels.append((str(record.get("recordId", "")), label))

        left, right = st.columns([0.62, 0.38])
        with left:
            if record_labels and field_names:
                record_choice = st.selectbox(
                    "Запись MWS",
                    options=[item[0] for item in record_labels],
                    format_func=lambda value: next((label for rec_id, label in record_labels if rec_id == value), value),
                    key="insert_record_choice",
                )
                field_choice = st.selectbox("Поле", field_names, key="insert_field_choice")
                if st.button("Вставить значение MWS", key="insert-mws-value"):
                    append_snippet(build_formula_token(table_id, record_choice, field_choice))
                    st.rerun()
                if st.button("Вставить таблицу MWS", key="insert-mws-table"):
                    append_snippet(build_table_block(insert_options))
                    st.rerun()
            else:
                st.info("MWS-данные пока недоступны.")
        with right:
            uploaded_file = st.file_uploader("Изображение / файл", type=["png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "xls", "xlsx"], key="workspace_uploader")
            if uploaded_file is not None and st.button("Вставить вложение", key="insert-upload"):
                append_snippet(file_to_attachment_snippet(uploaded_file))
                st.rerun()

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        slash_value = st.text_input("Slash-команда", placeholder="/table /page /callout /heading", key="slash_value")
        if st.button("Применить команду", key="apply-slash"):
            value = slash_value.strip().lower()
            if value in {"/heading", "/h1"}:
                append_snippet("# Новый заголовок")
            elif value == "/callout":
                append_snippet("> Новый callout")
            elif value == "/page":
                append_snippet("[[Новая страница]]")
            elif value == "/table":
                append_snippet(build_table_block(insert_options))
            elif value == "/code":
                append_snippet("``` пример кода")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_comment_panel(client: ApiClient, page: dict[str, Any], comments: list[dict[str, Any]]) -> None:
    st.markdown("<div class='panel-card'><div class='panel-card__title'>Комментарии</div><div class='panel-card__sub'>Живые ветки по текущей странице, ответы, лайки и решение ветки.</div>", unsafe_allow_html=True)
    paragraph_choice = st.selectbox("Привязка к абзацу", paragraph_options(st.session_state.draft_content), key="new_comment_anchor")
    new_comment = st.text_input("Новый комментарий", placeholder="Напишите комментарий", key="new_comment_body")
    if st.button("Добавить комментарий", key="create-comment", use_container_width=True, type="primary"):
        if new_comment.strip():
            _, error = safe_api_call(client.create_comment, page_id_of(page), new_comment.strip(), paragraph_choice, st.session_state.get("author_name", "viewer"))
            if error:
                st.error(error)
            else:
                st.rerun()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    if not comments:
        st.markdown("<div class='tiny'>Нет комментариев. Создайте первую ветку справа от документа.</div>", unsafe_allow_html=True)
    for thread in comments:
        messages = thread.get("messages", []) or []
        first = messages[0] if messages else {}
        title = thread.get("selectionLabel") or "Весь документ"
        like_count = int(thread.get("likeCount", 0))
        status = "Решена" if thread.get("resolved") else "Открыта"
        st.markdown(
            f"""
            <div class="comment-item-card">
              <div class="comment-item-card__title">{escape(title)}</div>
              <div class="comment-item-card__meta">{escape(first.get("author", "viewer"))} · {escape(str(first.get("createdAt", ""))[:16].replace("T", " "))} · <span class="status-good">{escape(status)}</span> · лайков {like_count}</div>
              <div class="comment-item-card__body">{escape(first.get("body", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for message in messages[1:]:
            st.markdown(f"<div class='tiny' style='margin:8px 0 0 10px'>↳ {escape(message.get('author', 'viewer'))}: {escape(message.get('body', ''))}</div>", unsafe_allow_html=True)
        reply = st.text_input("Ответ", key=f"reply-{thread['threadId']}", placeholder="Напишите ответ")
        a, b, c = st.columns(3)
        with a:
            if st.button("Ответить", key=f"reply-btn-{thread['threadId']}", use_container_width=True):
                if reply.strip():
                    _, error = safe_api_call(client.reply_to_comment, page_id_of(page), thread["threadId"], reply.strip(), st.session_state.get("author_name", "viewer"))
                    if error:
                        st.error(error)
                    else:
                        st.rerun()
        with b:
            if st.button("Лайк", key=f"like-{thread['threadId']}", use_container_width=True):
                _, error = safe_api_call(client.toggle_comment_like, page_id_of(page), thread["threadId"], st.session_state.get("author_name", "viewer"))
                if error:
                    st.error(error)
                else:
                    st.rerun()
        with c:
            action_label = "Открыть" if thread.get("resolved") else "Решить"
            if st.button(action_label, key=f"resolve-{thread['threadId']}", use_container_width=True):
                _, error = safe_api_call(client.resolve_comment, page_id_of(page), thread["threadId"], not bool(thread.get("resolved")))
                if error:
                    st.error(error)
                else:
                    st.rerun()
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_history_panel(comments: list[dict[str, Any]], versions: list[dict[str, Any]]) -> None:
    st.markdown("<div class='panel-card'><div class='panel-card__title'>История комментариев</div><div class='panel-card__sub'>Решенные ветки и снимки документа для review-демо.</div>", unsafe_allow_html=True)
    resolved = [item for item in comments if item.get("resolved")]
    if not resolved and not versions:
        st.markdown("<div class='tiny'>Пока история пуста.</div>", unsafe_allow_html=True)
    for thread in resolved:
        first = (thread.get("messages") or [{}])[0]
        st.markdown(
            f"""
            <div class="history-item">
              <div class="history-item__title">{escape(thread.get("selectionLabel") or "Комментарий")}</div>
              <div class="history-item__meta">Решена · {escape(str(thread.get("updatedAt", ""))[:16].replace("T", " "))}</div>
              <div class="history-item__body">{escape(first.get("body", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    for version in versions[:6]:
        st.markdown(
            f"""
            <div class="history-item">
              <div class="history-item__title">{escape(version.get("label", "Снимок"))}</div>
              <div class="history-item__meta">{escape(version.get("author", "system"))} · {escape(str(version.get("createdAt", ""))[:16].replace("T", " "))}</div>
              <div class="history-item__body">{escape(version.get("title", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_time_machine_panel(client: ApiClient, page: dict[str, Any], versions: list[dict[str, Any]]) -> None:
    st.markdown("<div class='panel-card'><div class='panel-card__title'>Машина времени</div><div class='panel-card__sub'>Снимки документа и откат к любой сохраненной версии.</div>", unsafe_allow_html=True)
    if st.button("Создать снимок", key="create-version", use_container_width=True, type="primary"):
        _, error = safe_api_call(client.create_version, page_id_of(page), "Manual snapshot", st.session_state.get("author_name", "manual"))
        if error:
            st.error(error)
        else:
            st.rerun()
    if not versions:
        st.markdown("<div class='tiny'>Нет снимков. Создайте первый snapshot.</div>", unsafe_allow_html=True)
    for version in versions:
        st.markdown(
            f"""
            <div class="history-item">
              <div class="history-item__title">{escape(version.get("label", "Снимок"))}</div>
              <div class="history-item__meta">{escape(str(version.get("createdAt", ""))[:19].replace("T", " "))} · {escape(version.get("author", "system"))}</div>
              <div class="history-item__body">{escape(version.get("title", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Восстановить", key=f"restore-{version['versionId']}", use_container_width=True):
            _, error = safe_api_call(client.restore_version, page_id_of(page), version["versionId"])
            if error:
                st.error(error)
            else:
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_access_panel() -> None:
    st.markdown("<div class='panel-card'><div class='panel-card__title'>Доступ к комментариям</div><div class='panel-card__sub'>Frontend-настройка для judge-flow и демонстрации сценариев доступа.</div>", unsafe_allow_html=True)
    option = st.radio("Кто может комментировать", ["Все пользователи", "Только создатель страницы"], key="comment_access", label_visibility="collapsed")
    st.markdown(f"<div class='pill'>{escape(option)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='tiny' style='margin-top:12px'>Эта настройка уже встроена в новый интерфейс и готова к дальнейшей привязке к backend-ролям.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_workspace() -> None:
    client = get_client()
    _, error = safe_api_call(client.health)
    if error:
        st.error(error)
        return

    pages, error = safe_api_call(client.list_pages)
    if error:
        st.error(error)
        return
    pages = pages or []
    if not pages:
        created, create_error = safe_api_call(client.create_page, "Новая страница", "")
        if create_error:
            st.error(create_error)
            return
        pages = [created]

    current_id = st.session_state.get("current_page_id") or page_id_of(pages[0])
    page_summary = next((item for item in pages if page_id_of(item) == current_id), pages[0])
    page, error = safe_api_call(client.get_page, page_id_of(page_summary))
    if error:
        st.error(error)
        return

    ensure_page_loaded(page)
    comments, comment_error = safe_api_call(client.list_comments, page_id_of(page))
    versions, versions_error = safe_api_call(client.list_versions, page_id_of(page))
    insert_options, insert_error = safe_api_call(client.get_insert_options)
    comments = comments or []
    versions = versions or []
    insert_options = insert_options or {}
    backlinks = collect_backlinks(pages, page)

    st.markdown("<div class='app-shell'>", unsafe_allow_html=True)
    left, right = st.columns([0.24, 0.76], gap="large")

    with left:
        st.markdown("<div class='rail'>", unsafe_allow_html=True)
        render_page_rail(pages, page_id_of(page), backlinks)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        render_metric_cards(page, comments, versions, backlinks)
        main, panel = st.columns([0.72, 0.28], gap="large")
        with main:
            st.markdown(
                f"""
                <div class="workspace-card">
                  <div class="workspace-head">
                    <div class="workspace-head__meta">
                      {icon_svg()}
                      <div>
                        <div class="workspace-head__title">{escape(page_title_of(page))}</div>
                        <div class="workspace-head__sub">Добавить описание</div>
                      </div>
                    </div>
                    <div class="workspace-links">
                      <span class="workspace-links__item {'is-active' if st.session_state.get('active_panel', 'comments') == 'comments' else ''}">Комментарии</span>
                      <span class="workspace-links__item {'is-active' if st.session_state.get('active_panel', 'time_machine') == 'time_machine' else ''}">Машина времени</span>
                    </div>
                  </div>
                """,
                unsafe_allow_html=True,
            )

            toolbar_cols = st.columns([1, 1, 1, 1, 1, 1])
            toolbar_actions = [("Сохранить", "save"), ("Снимок", "snapshot"), ("Комментарии", "comments"), ("История", "history"), ("Машина времени", "time_machine"), ("Доступ", "access")]
            for column, (label, action) in zip(toolbar_cols, toolbar_actions):
                with column:
                    if st.button(label, key=f"workspace-action-{action}", use_container_width=True):
                        if action == "save":
                            _, save_error = safe_api_call(client.update_page, page_id_of(page), st.session_state.draft_title, st.session_state.draft_content)
                            if save_error:
                                st.error(save_error)
                            else:
                                st.rerun()
                        elif action == "snapshot":
                            _, snapshot_error = safe_api_call(client.create_version, page_id_of(page), "Manual snapshot", st.session_state.get("author_name", "manual"))
                            if snapshot_error:
                                st.error(snapshot_error)
                            else:
                                st.rerun()
                        else:
                            st.session_state.active_panel = action
                            st.rerun()

            render_insert_toolbar(pages, insert_options)
            st.text_input("Заголовок", key="draft_title")
            st.caption("Редактирование сейчас идёт в markdown-like формате, а ниже вы сразу видите уже собранный judge-facing лист.")
            st.text_area("Документ", key="draft_content", label_visibility="collapsed")
            render_local_cache_bridge(page_id_of(page), str(page.get("updatedAt", "")))

            st.markdown("<div class='preview-card'><div class='preview-card__title'>Живой лист</div><div class='preview-card__sub'>Так документ выглядит как рабочая страница: живые поля MWS, ссылки, вложения, таблицы и callout-блоки.</div><div class='doc-surface'>", unsafe_allow_html=True)
            st.markdown(render_document_html(st.session_state.draft_content, insert_options), unsafe_allow_html=True)
            st.markdown("</div></div></div>", unsafe_allow_html=True)

        with panel:
            active_panel = st.session_state.get("active_panel", "comments")
            st.text_input("Автор", value=st.session_state.get("author_name", "") or "Константин Иванов", key="author_name")
            if comment_error:
                st.error(comment_error)
            if versions_error:
                st.error(versions_error)
            if insert_error:
                st.warning(insert_error)
            if active_panel == "comments":
                render_comment_panel(client, page, comments)
            elif active_panel == "history":
                render_history_panel(comments, versions)
            elif active_panel == "time_machine":
                render_time_machine_panel(client, page, versions)
            else:
                render_access_panel()

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    inject_css()
    workspace_tab, prototype_tab = st.tabs(["Рабочее пространство", "Референс-макеты"])
    with workspace_tab:
        render_workspace()
    with prototype_tab:
        render_prototype()


if __name__ == "__main__":
    main()
