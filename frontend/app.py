from __future__ import annotations

from pathlib import Path
import sys

FRONTEND_ROOT = Path(__file__).resolve().parent
if str(FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(FRONTEND_ROOT))

from ui.editor_page import render_editor_page
from ui.theme import configure_page, inject_global_styles


configure_page()


def main() -> None:
    inject_global_styles()
    render_editor_page()


if __name__ == "__main__":
    main()
