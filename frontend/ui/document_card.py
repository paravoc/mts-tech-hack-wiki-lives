from __future__ import annotations

from html import escape

import streamlit as st

from ui.insert_panel import render_insert_toolbar
from ui.state import (
    compose_document,
    draft_is_dirty,
    mark_current_draft_as_saved,
    page_id_of,
    page_title_of,
    render_local_cache_bridge,
    safe_api_call,
)
from utils.document_tools import render_document_html


def icon_svg() -> str:
    return "<svg class='wl-doc-icon' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'><path d='M6 3.5h7l4 4V18a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5.5a2 2 0 0 1 2-2Z'></path><path d='M13 3.5V8h4'></path></svg>"


def persist_current_page(client, page_id: str) -> tuple[dict | None, str | None]:
    serialized_content = compose_document(
        st.session_state.get("draft_summary", ""),
        st.session_state.get("draft_content", ""),
    )
    item, error = safe_api_call(
        client.update_page,
        page_id,
        st.session_state.get("draft_title", "Новая страница"),
        serialized_content,
    )
    if not error:
        mark_current_draft_as_saved()
    return item, error


def render_document_card(client, page: dict, pages: list[dict], insert_options: dict) -> None:
    active_panel = st.session_state.get("active_panel", "comments")
    dirty = draft_is_dirty()
    status_class = "wl-status-pill wl-status-pill--danger" if dirty else "wl-status-pill wl-status-pill--accent"
    status_label = "Есть несохраненные изменения" if dirty else "Все изменения сохранены"

    st.markdown("<div class='wl-card wl-editor-card'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="wl-editor-head">
          <div class="wl-editor-head__meta">
            {icon_svg()}
            <div>
              <div class="wl-editor-head__title">{escape(page_title_of(page))}</div>
              <div class="wl-editor-head__sub">Добавить описание</div>
            </div>
          </div>
          <div class="wl-text-actions">
            <span class="wl-text-link {'wl-text-link--active' if active_panel == 'comments' else ''}">Комментарии</span>
            <span class="wl-text-link {'wl-text-link--active' if active_panel == 'history' else ''}">История</span>
            <span class="wl-text-link {'wl-text-link--active' if active_panel == 'time_machine' else ''}">Машина времени</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='wl-toolbar-wrap'>", unsafe_allow_html=True)
    render_insert_toolbar(pages, insert_options)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='wl-editor-body'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='wl-status-row'><span class='{status_class}'>{status_label}</span><span class='wl-subtle'>Local cache восстанавливает черновик после перезагрузки.</span></div>",
        unsafe_allow_html=True,
    )

    title_col, summary_col = st.columns([0.52, 0.48], gap="large")
    with title_col:
        st.text_input("Заголовок", key="draft_title", placeholder="Новая страница")
    with summary_col:
        st.text_input("Описание", key="draft_summary", placeholder="Добавить описание")

    st.text_area("Документ", key="draft_content", label_visibility="collapsed")
    render_local_cache_bridge(page_id_of(page), str(page.get("updatedAt", "")))

    actions = st.columns([0.24, 0.24, 0.24, 0.28], gap="small")
    with actions[0]:
        if st.button("Сохранить", key="page-save", use_container_width=True, type="primary"):
            _, error = persist_current_page(client, page_id_of(page))
            if error:
                st.error(error)
            else:
                st.rerun()
    with actions[1]:
        if st.button("Снимок", key="page-snapshot", use_container_width=True):
            _, error = safe_api_call(
                client.create_version,
                page_id_of(page),
                "Manual snapshot",
                st.session_state.get("author_name", "manual"),
            )
            if error:
                st.error(error)
            else:
                st.rerun()
    with actions[2]:
        if st.button("Комментарии", key="page-open-comments", use_container_width=True):
            st.session_state["active_panel"] = "comments"
            st.rerun()
    with actions[3]:
        if st.button("Машина времени", key="page-open-time-machine", use_container_width=True):
            st.session_state["active_panel"] = "time_machine"
            st.rerun()

    st.markdown(
        """
        <div class="wl-banner">
          <span>You can only view and comment on this file.</span>
          <span class="wl-banner__cta">Ask to edit</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='wl-preview-card'><div class='wl-card-title'>Живой лист</div><div class='wl-card-sub'>Текущий документ уже рендерится с живыми полями MWS, вложениями, ссылками и таблицами.</div><div class='wl-preview-surface'>",
        unsafe_allow_html=True,
    )
    st.markdown(render_document_html(st.session_state.get("draft_content", ""), insert_options), unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
