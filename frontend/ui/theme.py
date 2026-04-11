from __future__ import annotations

import streamlit as st


def configure_page() -> None:
    st.set_page_config(
        page_title="WikiLive Editor",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"] {
            background: #ffffff !important;
            overflow: hidden !important;
            height: 100vh !important;
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
        """,
        unsafe_allow_html=True,
    )
