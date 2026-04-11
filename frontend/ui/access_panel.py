from __future__ import annotations

import streamlit as st

from ui.state import safe_api_call


def render_access_panel(client, page_id: str) -> None:
    mode_key = f"comment-access-mode::{page_id}"
    if mode_key not in st.session_state:
        mode, error = safe_api_call(client.get_comment_access, page_id)
        st.session_state[mode_key] = "all_users" if error else mode
        if error:
            st.warning(error)

    current_mode = st.session_state.get(mode_key, "all_users")
    current_index = 0 if current_mode == "all_users" else 1

    st.markdown("<div class='wl-panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='wl-card-title'>Доступ к комментариям</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='wl-card-sub'>Настройка сохраняется в backend на уровне страницы и используется как часть demo flow.</div>",
        unsafe_allow_html=True,
    )
    selection = st.radio(
        "Кто может комментировать",
        ["Все пользователи", "Только создатель страницы"],
        index=current_index,
        key=f"comment-access-ui-{page_id}",
    )
    mapped_mode = "all_users" if selection == "Все пользователи" else "owner_only"
    if mapped_mode != current_mode:
        saved_mode, error = safe_api_call(client.set_comment_access, page_id, mapped_mode)
        if error:
            st.error(error)
        else:
            st.session_state[mode_key] = saved_mode
            st.rerun()

    st.markdown(f"<span class='wl-status-pill wl-status-pill--accent'>{selection}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
