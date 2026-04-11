from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from ui.state import page_id_of, page_title_of, safe_api_call, set_current_page


def render_page_rail(client, pages: list[dict[str, Any]], current_page_id: str, backlinks: list[dict[str, Any]]) -> None:
    st.markdown("<div class='wl-rail__title'>WikiLive</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='wl-rail__meta'>Рабочий hackathon-контур: страницы, живые вставки MWS, комментарии, история и машина времени.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='wl-rail__section'>", unsafe_allow_html=True)
    st.markdown("<div class='wl-rail__section-title'>Страницы</div>", unsafe_allow_html=True)

    if st.button("Новая страница", key="rail-new-page", use_container_width=True, type="primary"):
        created, error = safe_api_call(client.create_page, "Новая страница", "")
        if error:
            st.error(error)
        else:
            set_current_page(created)
            st.rerun()

    st.text_input("Поиск", key="page_search", placeholder="Найти страницу", label_visibility="collapsed")
    visible_pages = pages
    search_value = st.session_state.get("page_search", "").strip().lower()
    if search_value:
        visible_pages = [page for page in pages if search_value in page_title_of(page).lower()]

    for item in visible_pages:
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
            f"<div class='wl-subtle' style='margin:-6px 0 10px'>{escape(str(item.get('updatedAt', ''))[:16].replace('T', ' '))}</div>",
            unsafe_allow_html=True,
        )

    if len(pages) > 1 and st.button("Удалить текущую", key="rail-delete-page", use_container_width=True):
        _, error = safe_api_call(client.delete_page, current_page_id)
        if error:
            st.error(error)
        else:
            st.session_state["current_page_id"] = ""
            st.session_state["loaded_page_id"] = ""
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='wl-rail__section'>", unsafe_allow_html=True)
    st.markdown("<div class='wl-rail__section-title'>Backlinks</div>", unsafe_allow_html=True)
    if backlinks:
        for item in backlinks:
            st.markdown(f"<div class='wl-tiny-list'>• {escape(page_title_of(item))}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='wl-tiny-list'>Пока нет страниц, которые ссылаются на текущий документ.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='wl-rail__section'>", unsafe_allow_html=True)
    st.markdown("<div class='wl-rail__section-title'>Что уже закрыто</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='wl-tiny-list'>
        • CRUD страниц<br/>
        • Живые вставки MWS<br/>
        • Комментарии и ответы<br/>
        • Снимки версии и откат<br/>
        • Local draft cache<br/>
        • Backlinks
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
