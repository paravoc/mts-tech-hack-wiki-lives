from __future__ import annotations

from html import escape

import streamlit as st

from ui.access_panel import render_access_panel
from ui.comments_panel import render_comments_panel
from ui.document_card import render_document_card
from ui.history_panel import render_history_panel
from ui.page_rail import render_page_rail
from ui.runtime import DEFAULT_BACKEND_URL, ensure_backend_running
from ui.state import (
    collect_backlinks,
    ensure_page_loaded,
    get_client,
    init_session_state,
    load_insert_options_cached,
    page_id_of,
    page_title_of,
    safe_api_call,
    sync_draft_history,
)
from ui.time_machine_panel import render_time_machine_panel


def render_workspace_app() -> None:
    init_session_state()

    backend_status = ensure_backend_running(DEFAULT_BACKEND_URL)
    if not backend_status.ready:
        st.error(backend_status.message or f"Backend недоступен: {backend_status.url}")
        st.stop()

    client = get_client()
    pages, error = safe_api_call(client.list_pages)
    if error:
        st.error(error)
        st.stop()
    pages = pages or []

    if not pages:
        created, create_error = safe_api_call(client.create_page, "Новая страница", "")
        if create_error:
            st.error(create_error)
            st.stop()
        pages = [created]

    current_id = st.session_state.get("current_page_id") or page_id_of(pages[0])
    page_summary = next((page for page in pages if page_id_of(page) == current_id), pages[0])
    page, error = safe_api_call(client.get_page, page_id_of(page_summary))
    if error:
        st.error(error)
        st.stop()

    ensure_page_loaded(page)
    sync_draft_history()

    comments, comment_error = safe_api_call(client.list_comments, page_id_of(page))
    versions, versions_error = safe_api_call(client.list_versions, page_id_of(page))
    try:
        insert_options = load_insert_options_cached(DEFAULT_BACKEND_URL)
        insert_error = None
    except Exception as exc:  # pragma: no cover
        insert_options = {}
        insert_error = str(exc)

    comments = comments or []
    versions = versions or []
    backlinks = collect_backlinks(pages, page)

    st.markdown("<div class='wl-shell'>", unsafe_allow_html=True)
    left, main, side = st.columns([0.22, 0.53, 0.25], gap="large")

    with left:
        st.markdown("<div class='wl-rail'>", unsafe_allow_html=True)
        render_page_rail(client, pages, page_id_of(page), backlinks)
        st.markdown("</div>", unsafe_allow_html=True)

    with main:
        _render_metrics(page, comments, versions, backlinks)
        render_document_card(client, page, pages, insert_options)

    with side:
        st.text_input("Автор", key="author_name")
        if comment_error:
            st.error(comment_error)
        if versions_error:
            st.error(versions_error)
        if insert_error:
            st.warning(f"MWS-вставки временно недоступны: {insert_error}")
        _render_active_panel(client, page, comments, versions)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_metrics(page: dict, comments: list[dict], versions: list[dict], backlinks: list[dict]) -> None:
    st.markdown(
        """
        <div class="wl-metric-grid">
          <div class="wl-metric">
            <div class="wl-metric__label">Комментарии</div>
            <div class="wl-metric__value">{comments_count}</div>
            <div class="wl-metric__sub">Открытые и решенные ветки по текущей странице.</div>
          </div>
          <div class="wl-metric">
            <div class="wl-metric__label">Снимки</div>
            <div class="wl-metric__value">{versions_count}</div>
            <div class="wl-metric__sub">История изменений и восстановление через машину времени.</div>
          </div>
          <div class="wl-metric">
            <div class="wl-metric__label">Backlinks</div>
            <div class="wl-metric__value">{backlinks_count}</div>
            <div class="wl-metric__sub">Страницы, которые ссылаются на “{title}”.</div>
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


def _render_active_panel(client, page: dict, comments: list[dict], versions: list[dict]) -> None:
    current = st.session_state.get("active_panel", "comments")
    panel_switch = st.columns(4, gap="small")
    for column, (panel_key, label) in zip(
        panel_switch,
        [("comments", "Комментарии"), ("history", "История"), ("time_machine", "Время"), ("access", "Доступ")],
    ):
        with column:
            if st.button(label, key=f"panel-switch-{panel_key}", use_container_width=True, type="primary" if current == panel_key else "secondary"):
                st.session_state["active_panel"] = panel_key
                st.rerun()

    if current == "comments":
        render_comments_panel(client, page, comments)
    elif current == "history":
        render_history_panel(comments, versions)
    elif current == "time_machine":
        render_time_machine_panel(client, page, versions)
    else:
        render_access_panel(client, page_id_of(page))
