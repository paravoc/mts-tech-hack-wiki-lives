from __future__ import annotations

import os
from typing import Any

import streamlit as st

from utils.api_client import ApiClient, ApiClientError


DEFAULT_BACKEND_URL = os.getenv("WIKILIVE_BACKEND_URL", "http://127.0.0.1:3000")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

            :root {
                --bg: #f7f3ec;
                --panel: rgba(255, 251, 245, 0.9);
                --panel-strong: #fffaf3;
                --ink: #1f1a17;
                --muted: #655b55;
                --line: rgba(72, 56, 43, 0.12);
                --accent: #bf4f2f;
                --accent-soft: rgba(191, 79, 47, 0.12);
                --green: #2a7f62;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(191, 79, 47, 0.10), transparent 28%),
                    radial-gradient(circle at top right, rgba(42, 127, 98, 0.08), transparent 26%),
                    linear-gradient(180deg, #f9f5ef 0%, #f2ece3 100%);
                color: var(--ink);
                font-family: 'Manrope', sans-serif;
            }

            .block-container {
                max-width: 1380px;
                padding-top: 1.4rem;
                padding-bottom: 2rem;
            }

            .hero-card,
            .panel-card,
            .metric-card {
                border: 1px solid var(--line);
                border-radius: 24px;
                background: var(--panel);
                box-shadow: 0 18px 50px rgba(49, 36, 28, 0.08);
                backdrop-filter: blur(10px);
            }

            .hero-card {
                padding: 1.5rem 1.6rem;
                margin-bottom: 1rem;
            }

            .hero-kicker {
                color: var(--accent);
                text-transform: uppercase;
                letter-spacing: 0.16em;
                font-size: 0.72rem;
                font-weight: 800;
                margin-bottom: 0.55rem;
            }

            .hero-title {
                font-size: 2rem;
                line-height: 1.02;
                font-weight: 800;
                margin-bottom: 0.45rem;
            }

            .hero-text {
                color: var(--muted);
                font-size: 0.98rem;
                line-height: 1.55;
                margin: 0;
            }

            .panel-card {
                padding: 1rem 1.1rem 1.15rem 1.1rem;
                margin-bottom: 1rem;
            }

            .panel-title {
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }

            .panel-subtitle {
                color: var(--muted);
                font-size: 0.9rem;
                margin-bottom: 1rem;
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.8rem;
                margin-bottom: 1rem;
            }

            .metric-card {
                padding: 0.9rem 1rem;
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.8rem;
                margin-bottom: 0.3rem;
            }

            .metric-value {
                font-size: 1.1rem;
                font-weight: 800;
            }

            .status-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.45rem 0.7rem;
                border-radius: 999px;
                font-size: 0.82rem;
                font-weight: 700;
                border: 1px solid var(--line);
                background: var(--panel-strong);
            }

            .status-pill.ok {
                color: var(--green);
            }

            .status-pill.fail {
                color: var(--accent);
            }

            .preview-shell {
                border: 1px dashed rgba(72, 56, 43, 0.2);
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.72);
                padding: 1rem 1rem;
                min-height: 260px;
            }

            .preview-shell code {
                font-family: 'IBM Plex Mono', monospace;
            }

            .candidate-card {
                border: 1px solid var(--line);
                border-radius: 18px;
                background: rgba(255, 248, 240, 0.92);
                padding: 0.85rem 0.9rem;
                margin-bottom: 0.7rem;
            }

            .candidate-label {
                color: var(--muted);
                font-size: 0.76rem;
                margin-bottom: 0.28rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 800;
            }

            .candidate-insert {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.86rem;
                word-break: break-word;
                margin-bottom: 0.5rem;
            }

            .sidebar-note {
                color: var(--muted);
                font-size: 0.88rem;
                line-height: 1.5;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_client() -> ApiClient:
    return ApiClient(DEFAULT_BACKEND_URL)


def ensure_state() -> None:
    defaults: dict[str, Any] = {
        "selected_page_id": None,
        "editor_title": "",
        "editor_content": "",
        "preview_html": "",
        "ai_prompt": "",
        "ai_candidates": [],
        "last_error": "",
        "last_success": "",
        "loaded_page_snapshot": None,
        "live_updates_enabled": True,
        "live_refresh_seconds": 3,
        "last_live_sync_at": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_editor() -> None:
    st.session_state.selected_page_id = None
    st.session_state.editor_title = ""
    st.session_state.editor_content = ""
    st.session_state.preview_html = ""
    st.session_state.ai_candidates = []
    st.session_state.loaded_page_snapshot = None


def load_page(page: dict[str, Any]) -> None:
    st.session_state.selected_page_id = page.get("pageId")
    st.session_state.editor_title = page.get("title", "")
    st.session_state.editor_content = page.get("content", "")
    st.session_state.preview_html = page.get("renderedHtml", "")
    st.session_state.ai_candidates = []
    st.session_state.loaded_page_snapshot = {
        "title": st.session_state.editor_title,
        "content": st.session_state.editor_content,
        "updatedAt": page.get("updatedAt", ""),
    }


def insert_candidate(candidate_insert: str) -> None:
    current = st.session_state.editor_content.strip()
    if current:
        st.session_state.editor_content = f"{current}\n{candidate_insert}"
    else:
        st.session_state.editor_content = candidate_insert
    st.session_state.preview_html = ""
    st.session_state.last_success = "Вставка добавлена в редактор."


def backend_status(client: ApiClient) -> tuple[bool, str]:
    try:
        health = client.health()
        status = health.get("status", "ok")
        return True, f"Backend доступен: {status}"
    except ApiClientError as exc:
        return False, str(exc)


def fetch_pages(client: ApiClient) -> tuple[list[dict[str, Any]], str | None]:
    try:
        return client.list_pages(), None
    except ApiClientError as exc:
        return [], str(exc)


def render_preview_panel() -> None:
    preview_html = st.session_state.preview_html.strip()
    if preview_html:
        st.markdown(
            f'<div class="preview-shell">{preview_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="preview-shell">
                <strong>Предпросмотр пока пуст.</strong><br/>
                Нажми <code>Обновить предпросмотр</code> или открой существующую страницу.
            </div>
            """,
            unsafe_allow_html=True,
        )


def has_unsaved_local_changes() -> bool:
    snapshot = st.session_state.loaded_page_snapshot or {}
    return (
        st.session_state.editor_title != snapshot.get("title", "")
        or st.session_state.editor_content != snapshot.get("content", "")
    )


def sync_selected_page_if_needed(client: ApiClient) -> None:
    selected_page_id = st.session_state.selected_page_id
    if not selected_page_id:
        return

    try:
        server_page = client.get_page(selected_page_id)
    except ApiClientError:
        return

    snapshot = st.session_state.loaded_page_snapshot or {}
    current_updated_at = snapshot.get("updatedAt", "")
    server_updated_at = server_page.get("updatedAt", "")

    if server_updated_at and server_updated_at != current_updated_at:
        if has_unsaved_local_changes():
            st.session_state.last_live_sync_at = "локальные правки не перезаписаны"
            return
        load_page(server_page)
        st.session_state.last_success = "Открытая страница обновилась с сервера."
        st.rerun()

    st.session_state.last_live_sync_at = server_updated_at or "checked"


def render_live_sync_fragment(client: ApiClient) -> None:
    run_every = None
    if st.session_state.live_updates_enabled and st.session_state.selected_page_id:
        run_every = st.session_state.live_refresh_seconds

    @st.fragment(run_every=run_every)
    def live_sync_fragment() -> None:
        sync_selected_page_if_needed(client)
        if st.session_state.selected_page_id:
            st.caption(
                f"Live sync: каждые {st.session_state.live_refresh_seconds} сек. "
                f"Последняя отметка: {st.session_state.last_live_sync_at or 'ожидание'}"
            )
        else:
            st.caption("Live sync включится автоматически, когда будет выбрана страница.")

    live_sync_fragment()


def main() -> None:
    st.set_page_config(
        page_title="WikiLive",
        page_icon="W",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()
    ensure_state()

    client = build_client()
    backend_ok, backend_message = backend_status(client)
    pages, pages_error = fetch_pages(client)

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">WikiLive / Web Console</div>
            <div class="hero-title">Живые страницы поверх MWS Tables</div>
            <p class="hero-text">
                Интерфейс работает как тонкий клиент: backend хранит страницы, рендерит вставки и подключает AI,
                а frontend остается легким и готовым к будущей desktop-обертке.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Навигация")
        status_class = "ok" if backend_ok else "fail"
        st.markdown(
            f'<div class="status-pill {status_class}">{"ONLINE" if backend_ok else "OFFLINE"} · {backend_message}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Backend: `{DEFAULT_BACKEND_URL}`")

        st.toggle("Live sync", key="live_updates_enabled")
        st.slider(
            "Интервал обновления, сек",
            min_value=2,
            max_value=15,
            key="live_refresh_seconds",
        )

        if st.button("Обновить страницы", use_container_width=True):
            st.rerun()

        if st.button("Новая страница", use_container_width=True):
            reset_editor()
            st.session_state.last_success = "Открыт чистый черновик."
            st.rerun()

        st.markdown("### Страницы")
        if pages_error is not None:
            st.error(pages_error)
        elif not pages:
            st.info("Пока нет ни одной страницы. Можно создать первую справа.")
        else:
            for index, page in enumerate(pages):
                label = page.get("title") or f"Без названия #{index + 1}"
                is_active = page.get("pageId") == st.session_state.selected_page_id
                button_label = f"● {label}" if is_active else label
                if st.button(button_label, key=f"page-btn-{page['pageId']}", use_container_width=True):
                    try:
                        load_page(client.get_page(page["pageId"]))
                        st.session_state.last_success = f"Страница «{label}» загружена."
                    except ApiClientError as exc:
                        st.session_state.last_error = str(exc)
                    st.rerun()

        st.markdown("---")
        st.markdown(
            '<div class="sidebar-note">Desktop-версию потом будет удобно завернуть поверх этого же интерфейса: backend и API-контракт уже отделены от UI.</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        st.session_state.last_error = ""

    if st.session_state.last_success:
        st.success(st.session_state.last_success)
        st.session_state.last_success = ""

    selected_label = st.session_state.editor_title or "Новый черновик"
    page_count = len(pages)
    metric_cards = f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Активный документ</div>
                <div class="metric-value">{selected_label}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Страниц в системе</div>
                <div class="metric-value">{page_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Режим хранения</div>
                <div class="metric-value">WikiPages / MWS</div>
            </div>
        </div>
    """
    st.markdown(metric_cards, unsafe_allow_html=True)
    render_live_sync_fragment(client)

    editor_col, side_col = st.columns([1.25, 0.95], gap="large")

    with editor_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-title">Редактор страницы</div>
                <div class="panel-subtitle">
                    Здесь живет исходный текст, включая вставки вида <code>{{tableId:recordId:fieldName}}</code>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.text_input("Заголовок", key="editor_title", placeholder="Например, Статус проекта")
        st.text_area(
            "Содержимое",
            key="editor_content",
            height=380,
            placeholder="Пиши текст страницы и вставляй живые значения из MWS Tables.",
        )

        action_col1, action_col2, action_col3, action_col4 = st.columns([1.2, 1.2, 1.2, 1.1])

        if action_col1.button("Сохранить", use_container_width=True, type="primary"):
            title = st.session_state.editor_title.strip()
            content = st.session_state.editor_content
            if not title:
                st.session_state.last_error = "Заголовок не должен быть пустым."
            else:
                try:
                    if st.session_state.selected_page_id:
                        saved = client.update_page(st.session_state.selected_page_id, title, content)
                        st.session_state.last_success = "Страница обновлена."
                    else:
                        saved = client.create_page(title, content)
                        st.session_state.last_success = "Страница создана."

                    load_page(saved)
                except ApiClientError as exc:
                    st.session_state.last_error = str(exc)
            st.rerun()

        if action_col2.button("Обновить предпросмотр", use_container_width=True):
            try:
                st.session_state.preview_html = client.render_content(st.session_state.editor_content)
                st.session_state.last_success = "Предпросмотр обновлен."
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
            st.rerun()

        if action_col3.button("Перезагрузить страницу", use_container_width=True, disabled=not st.session_state.selected_page_id):
            try:
                reloaded = client.get_page(st.session_state.selected_page_id)
                load_page(reloaded)
                st.session_state.last_success = "Страница перечитана с сервера."
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
            st.rerun()

        if action_col4.button("Удалить", use_container_width=True, disabled=not st.session_state.selected_page_id):
            try:
                client.delete_page(st.session_state.selected_page_id)
                reset_editor()
                st.session_state.last_success = "Страница удалена."
            except ApiClientError as exc:
                st.session_state.last_error = str(exc)
            st.rerun()

    with side_col:
        preview_tab, ai_tab = st.tabs(["Предпросмотр", "AI-помощник"])

        with preview_tab:
            st.markdown(
                """
                <div class="panel-card">
                    <div class="panel-title">Живой просмотр</div>
                    <div class="panel-subtitle">
                        Backend уже подставляет значения из MWS и возвращает готовый HTML.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_preview_panel()

        with ai_tab:
            st.markdown(
                """
                <div class="panel-card">
                    <div class="panel-title">Подсказки по вставкам</div>
                    <div class="panel-subtitle">
                        AI может подобрать подходящую живую вставку по смыслу запроса. Если модель временно недоступна,
                        backend вернет понятную ошибку и не сломает редактор.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.text_input(
                "Что нужно вставить",
                key="ai_prompt",
                placeholder="Например, вставь статус проекта",
            )

            if st.button("Предложить вставку", use_container_width=True):
                prompt = st.session_state.ai_prompt.strip()
                if not prompt:
                    st.session_state.last_error = "Сначала опиши, что именно нужно вставить."
                else:
                    try:
                        st.session_state.ai_candidates = client.suggest_insert(
                            user_prompt=prompt,
                            page_content=st.session_state.editor_content,
                        )
                        if st.session_state.ai_candidates:
                            st.session_state.last_success = "AI подготовил кандидатов для вставки."
                        else:
                            st.session_state.last_error = "AI не нашел подходящих вставок."
                    except ApiClientError as exc:
                        st.session_state.last_error = str(exc)
                st.rerun()

            if st.session_state.ai_candidates:
                for index, candidate in enumerate(st.session_state.ai_candidates):
                    st.markdown(
                        f"""
                        <div class="candidate-card">
                            <div class="candidate-label">Кандидат {index + 1}</div>
                            <div class="candidate-insert">{candidate.get("insert", "")}</div>
                            <div><strong>Поле:</strong> {candidate.get("fieldName", "—")}</div>
                            <div><strong>Причина:</strong> {candidate.get("reason", "—")}</div>
                            <div><strong>Уверенность:</strong> {candidate.get("confidence", 0):.2f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Вставить в редактор", key=f"insert-candidate-{index}", use_container_width=True):
                        insert_candidate(candidate.get("insert", ""))
                        st.rerun()
            else:
                st.info("Пока нет AI-кандидатов. Запрос можно сделать даже на пустом черновике.")


if __name__ == "__main__":
    main()
