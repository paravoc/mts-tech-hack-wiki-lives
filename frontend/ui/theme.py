from __future__ import annotations

import streamlit as st

from ui.cursors import cursor_root_variables


def configure_page() -> None:
    st.set_page_config(
        page_title="WikiLive Editor",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_global_styles() -> None:
    styles = """
        <style>
        :root {
__CURSOR_ROOT_VARIABLES__
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }

       html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: #ffffff !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100vh !important;
    cursor: var(--cursor-default) !important;
}

        a,
        button,
        [role="button"],
        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-primary"] {
            cursor: var(--cursor-pointer) !important;
        }

        input,
        textarea,
        [contenteditable="true"] {
            cursor: var(--cursor-text) !important;
        }

        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stSidebar"],
        [data-testid="stStatusWidget"],
        [data-testid="stSpinner"],
        .stSpinner,
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
        }

        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after,
        .stApp::before,
        .stApp::after {
            background: #ffffff !important;
        }

        .block-container {
            max-width: none !important;
            padding: 0 !important;
        }

        .stMainBlockContainer {
            padding: 0 !important;
        }

        iframe {
            width: 100% !important;
            border: 0 !important;
        }

        [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }
        </style>
        """
    styles = styles.replace("__CURSOR_ROOT_VARIABLES__", cursor_root_variables("            "))
    st.markdown(
        styles,
        unsafe_allow_html=True,
    )
