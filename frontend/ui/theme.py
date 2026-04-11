from __future__ import annotations

import streamlit as st


def configure_page() -> None:
    st.set_page_config(
        page_title="WikiLive",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --canvas: #434347;
            --canvas-strong: #3f3f43;
            --paper: #ffffff;
            --paper-soft: #f8f9fc;
            --panel: #f5f6fa;
            --line: #e6e8ef;
            --line-strong: #d6dae6;
            --ink: #151821;
            --muted: #8b91a1;
            --muted-strong: #697086;
            --accent: #8f7cff;
            --accent-soft: #f2efff;
            --danger: #ff4f8b;
            --danger-soft: #fff1f6;
            --blue: #5ea3ff;
            --blue-soft: #eef5ff;
            --shadow-lg: 0 24px 48px rgba(12, 16, 33, 0.14);
            --shadow-md: 0 14px 28px rgba(12, 16, 33, 0.09);
            --shadow-sm: 0 8px 18px rgba(12, 16, 33, 0.06);
        }

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(143,124,255,.12), transparent 22%),
                radial-gradient(circle at bottom left, rgba(94,163,255,.10), transparent 24%),
                linear-gradient(180deg, var(--canvas) 0%, var(--canvas-strong) 100%);
            color: var(--ink);
        }

        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stSidebar"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
        }

        .block-container {
            max-width: none !important;
            padding: 20px 20px 32px !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
            border-radius: 14px !important;
            border: 1px solid var(--line) !important;
            background: #ffffff !important;
            box-shadow: none !important;
            color: #1b202b !important;
        }

        div[data-testid="stTextInput"] input { min-height: 42px !important; }

        div[data-testid="stTextArea"] textarea {
            min-height: 620px !important;
            line-height: 1.8 !important;
            padding: 1.05rem 1rem 1.15rem !important;
            caret-color: var(--accent) !important;
        }

        div[data-testid="stTextArea"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stFileUploader"] label {
            color: var(--muted-strong) !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
        }

        button[kind="secondary"], button[kind="primary"] {
            border-radius: 12px !important;
            min-height: 38px !important;
            font-weight: 700 !important;
            box-shadow: none !important;
            transition: background .18s ease, border-color .18s ease, color .18s ease, transform .18s ease !important;
        }

        button[kind="secondary"] {
            border: 1px solid var(--line) !important;
            background: var(--paper-soft) !important;
            color: #283040 !important;
        }

        button[kind="secondary"]:hover {
            border-color: var(--line-strong) !important;
            background: #ffffff !important;
            transform: translateY(-1px);
        }

        button[kind="primary"] {
            border: 1px solid transparent !important;
            background: var(--danger) !important;
            color: #ffffff !important;
        }

        button[kind="primary"]:hover {
            background: #ff3f81 !important;
            transform: translateY(-1px);
        }

        [data-testid="stPopover"] button {
            border-radius: 12px !important;
            min-height: 38px !important;
            border: 1px solid var(--line) !important;
            background: var(--paper-soft) !important;
            color: #283040 !important;
            font-weight: 700 !important;
            box-shadow: none !important;
        }

        [data-testid="stPopover"] button:hover {
            background: #ffffff !important;
            border-color: var(--line-strong) !important;
        }

        .wl-shell {
            display: grid;
            grid-template-columns: 280px minmax(0, 1fr) 360px;
            gap: 22px;
            align-items: start;
        }

        .wl-rail {
            position: sticky;
            top: 20px;
            border-radius: 22px;
            background: rgba(28, 29, 34, 0.62);
            border: 1px solid rgba(255,255,255,.08);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
            padding: 18px;
            min-height: calc(100vh - 48px);
        }

        .wl-rail * { color: #ffffff; }
        .wl-rail__title { font-size: 1.08rem; font-weight: 800; letter-spacing: -0.02em; }
        .wl-rail__meta { margin-top: 6px; color: rgba(255,255,255,.68); font-size: 0.82rem; line-height: 1.5; }
        .wl-rail__section { margin-top: 18px; padding-top: 18px; border-top: 1px solid rgba(255,255,255,.08); }
        .wl-rail__section-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.72); font-weight: 800; margin-bottom: 12px; }

        .wl-card {
            background: var(--paper);
            border: 1px solid rgba(228,231,239,.96);
            border-radius: 24px;
            box-shadow: var(--shadow-lg);
        }

        .wl-metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 18px;
        }

        .wl-metric {
            background: rgba(255,255,255,.98);
            border: 1px solid rgba(228,231,239,.96);
            border-radius: 18px;
            padding: 18px;
            box-shadow: var(--shadow-sm);
        }

        .wl-metric__label { color: var(--muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; }
        .wl-metric__value { margin-top: 8px; font-size: 1.75rem; font-weight: 800; color: var(--ink); letter-spacing: -0.05em; }
        .wl-metric__sub { margin-top: 8px; color: var(--muted-strong); font-size: 0.83rem; line-height: 1.55; }

        .wl-editor-card { overflow: hidden; }
        .wl-editor-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; padding: 22px 24px 16px; border-bottom: 1px solid var(--line); }
        .wl-editor-head__meta { display: flex; gap: 12px; min-width: 0; }
        .wl-doc-icon { width: 20px; height: 20px; color: #747b8d; flex: none; margin-top: 3px; }
        .wl-editor-head__title { font-size: 1.28rem; font-weight: 800; letter-spacing: -0.03em; color: var(--ink); line-height: 1.15; }
        .wl-editor-head__sub { margin-top: 6px; color: var(--muted); font-size: 0.83rem; }
        .wl-text-actions { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
        .wl-text-link { color: var(--muted-strong); font-size: 0.84rem; font-weight: 700; }
        .wl-text-link--active { color: var(--accent); }
        .wl-toolbar-wrap { padding: 16px 24px 10px; background: #fbfcff; border-bottom: 1px solid var(--line); }
        .wl-toolbar-note { margin-top: 10px; color: var(--muted); font-size: 0.78rem; }
        .wl-editor-body { padding: 18px 24px 24px; }
        .wl-status-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
        .wl-status-pill { display: inline-flex; align-items: center; min-height: 30px; padding: 0 12px; border-radius: 999px; background: var(--panel); border: 1px solid var(--line); color: var(--muted-strong); font-size: 0.76rem; font-weight: 700; }
        .wl-status-pill--accent { color: var(--accent); background: var(--accent-soft); border-color: transparent; }
        .wl-status-pill--danger { color: var(--danger); background: var(--danger-soft); border-color: transparent; }
        .wl-subtle { color: var(--muted); font-size: 0.8rem; line-height: 1.5; }

        .wl-preview-card, .wl-panel-card {
            background: rgba(255,255,255,.98);
            border: 1px solid rgba(228,231,239,.96);
            border-radius: 20px;
            box-shadow: var(--shadow-md);
            padding: 18px;
        }

        .wl-preview-card + .wl-preview-card, .wl-panel-card + .wl-panel-card { margin-top: 16px; }
        .wl-card-title { font-size: 1rem; font-weight: 800; color: var(--ink); letter-spacing: -0.02em; }
        .wl-card-sub { margin-top: 6px; color: var(--muted-strong); font-size: 0.83rem; line-height: 1.55; }
        .wl-preview-surface { margin-top: 16px; padding: 22px 24px 28px; background: #ffffff; border: 1px solid var(--line); border-radius: 18px; min-height: 260px; }
        .wl-divider { height: 1px; background: var(--line); margin: 14px 0; }
        .wl-tiny-list { color: var(--muted-strong); font-size: 0.8rem; line-height: 1.7; }

        .wl-comment-card, .wl-history-card {
            border: 1px solid var(--line);
            background: #fbfbfe;
            border-radius: 16px;
            padding: 14px;
        }

        .wl-comment-card + .wl-comment-card, .wl-history-card + .wl-history-card { margin-top: 12px; }
        .wl-comment-card__head, .wl-history-card__head { display: flex; justify-content: space-between; gap: 8px; align-items: flex-start; }
        .wl-comment-card__title, .wl-history-card__title { font-size: 0.9rem; font-weight: 800; color: #222837; }
        .wl-comment-card__meta, .wl-history-card__meta { margin-top: 4px; color: var(--muted); font-size: 0.76rem; }
        .wl-comment-card__body, .wl-history-card__body { margin-top: 10px; color: #2b3140; font-size: 0.85rem; line-height: 1.7; }
        .wl-avatar { width: 28px; height: 28px; border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 800; color: #ffffff; flex: none; }
        .wl-avatar--blue { background: #65a8ff; }
        .wl-avatar--violet { background: #8f7cff; }
        .wl-avatar--yellow { background: #f0b541; }
        .wl-thread-status { display: inline-flex; align-items: center; min-height: 24px; padding: 0 8px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-size: 0.72rem; font-weight: 800; }
        .wl-thread-status--resolved { background: #eef7f0; color: #3f9155; }

        .wl-banner {
            margin-top: 16px;
            border-radius: 16px;
            background: var(--blue-soft);
            border: 1px solid rgba(94,163,255,.22);
            padding: 12px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            color: #31558e;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        .wl-banner__cta {
            display: inline-flex;
            align-items: center;
            min-height: 32px;
            padding: 0 12px;
            border-radius: 999px;
            background: #ffffff;
            border: 1px solid rgba(94,163,255,.22);
            color: #31558e;
            font-weight: 700;
        }

        .doc-empty-state__title { font-size: 1.02rem; font-weight: 800; color: var(--ink); }
        .doc-empty-state__text { margin-top: 6px; color: var(--muted-strong); font-size: 0.9rem; }
        .doc-heading { margin: 1.3rem 0 0.75rem; font-size: 1.25rem; line-height: 1.25; color: #191d29; font-weight: 800; letter-spacing: -0.03em; }
        .doc-paragraph { margin: 0.85rem 0; font-size: 0.98rem; line-height: 1.82; color: #242b3a; }
        .doc-divider { height: 1px; background: rgba(20,23,28,0.08); margin: 1.15rem 0; }
        .doc-callout { margin: 1rem 0; padding: 0.9rem 1rem; border-radius: 16px; background: #f7f7fb; border: 1px solid rgba(20,23,28,0.08); color: #2e3443; line-height: 1.7; }
        .doc-formula-chip { display: inline-flex; align-items: center; gap: 0.5rem; min-height: 1.85rem; padding: 0 0.72rem; border-radius: 999px; background: var(--accent-soft); color: #5d48d2; font-size: 0.76rem; font-weight: 800; vertical-align: middle; }
        .doc-formula-chip__index { color: #ffffff; background: #8f7cff; border-radius: 999px; min-width: 1.25rem; height: 1.25rem; display: inline-flex; align-items: center; justify-content: center; font-size: 0.68rem; }
        .doc-formula-chip__value { color: #75809a; font-weight: 700; }

        @media (max-width: 1400px) {
            .wl-shell { grid-template-columns: 260px minmax(0, 1fr); }
        }

        @media (max-width: 1080px) {
            .wl-shell, .wl-metric-grid { grid-template-columns: 1fr; }
            .wl-rail { position: relative; min-height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

