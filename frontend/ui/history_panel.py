from __future__ import annotations

from html import escape

import streamlit as st


def render_history_panel(comments: list[dict], versions: list[dict]) -> None:
    st.markdown("<div class='wl-panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='wl-card-title'>История комментариев</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='wl-card-sub'>Здесь собираются resolved-ветки и события, которые удобно показывать жюри как audit trail.</div>",
        unsafe_allow_html=True,
    )

    resolved_threads = [item for item in comments if item.get("resolved")]
    if not resolved_threads and not versions:
        st.markdown("<div class='wl-subtle'>История пока пуста.</div>", unsafe_allow_html=True)

    for thread in resolved_threads:
        first = (thread.get("messages") or [{}])[0]
        st.markdown(
            f"""
            <div class="wl-history-card">
              <div class="wl-history-card__head">
                <div>
                  <div class="wl-history-card__title">{escape(str(thread.get("selectionLabel") or "Комментарий"))}</div>
                  <div class="wl-history-card__meta">Решена · {escape(str(thread.get("updatedAt", ""))[:16].replace("T", " "))}</div>
                </div>
                <span class="wl-thread-status wl-thread-status--resolved">resolved</span>
              </div>
              <div class="wl-history-card__body">{escape(str(first.get("body", "")))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for version in versions[:5]:
        st.markdown(
            f"""
            <div class="wl-history-card">
              <div class="wl-history-card__title">{escape(str(version.get("label", "Снимок")))}</div>
              <div class="wl-history-card__meta">{escape(str(version.get("author", "system")))} · {escape(str(version.get("createdAt", ""))[:19].replace("T", " "))}</div>
              <div class="wl-history-card__body">{escape(str(version.get("title", "")))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

