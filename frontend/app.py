from __future__ import annotations

import streamlit as st

from utils.prototype_renderer import render_prototype


st.set_page_config(
    page_title="WikiLive Editor Prototype",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            color-scheme: light;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #424245;
            color: #141418;
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

        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_base_styles()
    render_prototype()


if __name__ == "__main__":
    main()
