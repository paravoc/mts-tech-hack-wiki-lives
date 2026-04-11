from __future__ import annotations

from html import escape

import streamlit as st

from ui.state import page_id_of, safe_api_call


def render_time_machine_panel(client, page: dict, versions: list[dict]) -> None:
    st.markdown("<div class='wl-panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='wl-card-title'>Машина времени</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='wl-card-sub'>Снимки документа сохраняются в backend и позволяют быстро откатываться к нужному состоянию.</div>",
        unsafe_allow_html=True,
    )

    if st.button("Создать снимок", key="time-machine-create-version", use_container_width=True, type="primary"):
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

    if not versions:
        st.markdown("<div class='wl-subtle'>Нет снимков. Создайте первый snapshot и покажите откат на демо.</div>", unsafe_allow_html=True)

    for index, version in enumerate(versions):
        badge_class = "wl-thread-status" if index == 0 else "wl-status-pill"
        st.markdown(
            f"""
            <div class="wl-history-card">
              <div class="wl-history-card__head">
                <div>
                  <div class="wl-history-card__title">{escape(str(version.get("label", "Снимок")))}</div>
                  <div class="wl-history-card__meta">{escape(str(version.get("createdAt", ""))[:19].replace("T", " "))} · {escape(str(version.get("author", "system")))}</div>
                </div>
                <span class="{badge_class}">{'latest' if index == 0 else 'snapshot'}</span>
              </div>
              <div class="wl-history-card__body">{escape(str(version.get("title", "")))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Восстановить", key=f"restore-version-{version['versionId']}", use_container_width=True):
            _, error = safe_api_call(client.restore_version, page_id_of(page), version["versionId"])
            if error:
                st.error(error)
            else:
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

