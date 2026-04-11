from __future__ import annotations

from html import escape

import streamlit as st

from ui.state import paragraph_options, page_id_of, safe_api_call


AVATAR_CLASSES = ["wl-avatar--blue", "wl-avatar--violet", "wl-avatar--yellow"]


def _avatar_class(index: int) -> str:
    return AVATAR_CLASSES[index % len(AVATAR_CLASSES)]


def render_comments_panel(client, page: dict, comments: list[dict]) -> None:
    st.markdown("<div class='wl-panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='wl-card-title'>Комментарии</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='wl-card-sub'>Реальные ветки по странице: комментарии, ответы, лайки и перевод в resolved.</div>",
        unsafe_allow_html=True,
    )

    anchor = st.selectbox("Привязка", paragraph_options(st.session_state.get("draft_content", "")), key="comment-anchor")
    body = st.text_area("Новый комментарий", key="new-comment-body", height=100)
    if st.button("Добавить комментарий", key="comments-create", use_container_width=True, type="primary"):
        if body.strip():
            _, error = safe_api_call(
                client.create_comment,
                page_id_of(page),
                body.strip(),
                anchor,
                st.session_state.get("author_name", "viewer"),
            )
            if error:
                st.error(error)
            else:
                st.rerun()

    st.markdown("<div class='wl-divider'></div>", unsafe_allow_html=True)
    if not comments:
        st.markdown("<div class='wl-subtle'>Нет комментариев. Создайте первую ветку для нужного абзаца.</div>", unsafe_allow_html=True)

    for thread_index, thread in enumerate(comments):
        _render_thread_card(client, page, thread, thread_index)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_thread_card(client, page: dict, thread: dict, thread_index: int) -> None:
    messages = thread.get("messages", []) or []
    first = messages[0] if messages else {}
    status_class = "wl-thread-status wl-thread-status--resolved" if thread.get("resolved") else "wl-thread-status"
    like_count = int(thread.get("likeCount", 0))
    author = str(first.get("author", "viewer"))
    initial = (author[:1] or "?").upper()

    st.markdown(
        f"""
        <div class="wl-comment-card">
          <div class="wl-comment-card__head">
            <div style="display:flex;gap:10px;align-items:flex-start;">
              <span class="wl-avatar {_avatar_class(thread_index)}">{escape(initial)}</span>
              <div>
                <div class="wl-comment-card__title">{escape(str(thread.get("selectionLabel") or "Весь документ"))}</div>
                <div class="wl-comment-card__meta">{escape(author)} · {escape(str(first.get("createdAt", ""))[:16].replace("T", " "))}</div>
              </div>
            </div>
            <span class="{status_class}">{'Решена' if thread.get('resolved') else 'Открыта'}</span>
          </div>
          <div class="wl-comment-card__body">{escape(str(first.get("body", "")))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for reply in messages[1:]:
        st.markdown(
            f"<div class='wl-subtle' style='margin:8px 0 0 18px'>↳ <strong>{escape(str(reply.get('author', 'viewer')))}</strong>: {escape(str(reply.get('body', '')))}</div>",
            unsafe_allow_html=True,
        )

    reply = st.text_input("Ответ", key=f"thread-reply-{thread['threadId']}", placeholder="Напишите ответ")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Ответить", key=f"thread-reply-btn-{thread['threadId']}", use_container_width=True):
            if reply.strip():
                _, error = safe_api_call(
                    client.reply_to_comment,
                    page_id_of(page),
                    thread["threadId"],
                    reply.strip(),
                    st.session_state.get("author_name", "viewer"),
                )
                if error:
                    st.error(error)
                else:
                    st.rerun()
    with c2:
        if st.button(f"Лайк {like_count}", key=f"thread-like-{thread['threadId']}", use_container_width=True):
            _, error = safe_api_call(
                client.toggle_comment_like,
                page_id_of(page),
                thread["threadId"],
                st.session_state.get("author_name", "viewer"),
            )
            if error:
                st.error(error)
            else:
                st.rerun()
    with c3:
        toggle_label = "Открыть" if thread.get("resolved") else "Решить"
        if st.button(toggle_label, key=f"thread-resolve-{thread['threadId']}", use_container_width=True):
            _, error = safe_api_call(
                client.resolve_comment,
                page_id_of(page),
                thread["threadId"],
                not bool(thread.get("resolved")),
            )
            if error:
                st.error(error)
            else:
                st.rerun()

    st.markdown("<div class='wl-divider'></div>", unsafe_allow_html=True)
