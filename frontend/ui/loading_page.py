from __future__ import annotations

from textwrap import dedent


def file_icon_svg(css_class: str = "doc-icon") -> str:
    return (
        f"<svg class='{css_class}' viewBox='0 0 24 24' fill='none' "
        "stroke='currentColor' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M6 3.5h7l4 4V18a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5.5a2 2 0 0 1 2-2Z'></path>"
        "<path d='M13 3.5V8h4'></path>"
        "</svg>"
    )


def document_header_markup(
    title: str = "Новая страница",
    subtitle: str = "Добавить описание",
) -> str:
    return dedent(
        f"""
        <header class="doc-head">
          <div class="doc-head__meta">
            {file_icon_svg()}
            <div>
              <div class="doc-title">{title}</div>
              <div class="doc-subtitle">{subtitle}</div>
            </div>
          </div>
        </header>
        """
    ).strip()


def loading_screen_markup() -> str:
    return dedent(
        f"""
        <section class="screen" id="loadingScreen">
          {document_header_markup()}
          <div class="loading-body">
            <div class="loading-skeleton" aria-hidden="true">
              <div class="loading-skeleton__bar loading-skeleton__bar--short"></div>
              <div class="loading-skeleton__bar loading-skeleton__bar--line-1"></div>
              <div class="loading-skeleton__bar loading-skeleton__bar--line-2"></div>
              <div class="loading-skeleton__bar loading-skeleton__bar--line-3"></div>
              <div class="loading-skeleton__bar loading-skeleton__bar--line-4"></div>
            </div>
          </div>
        </section>
        """
    ).strip()
