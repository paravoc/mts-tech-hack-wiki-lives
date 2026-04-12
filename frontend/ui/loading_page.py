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


def _account_switcher_markup() -> str:
    return dedent(
        """
        <div class="account-switcher" id="accountSwitcher">
          <button class="account-switcher__trigger" id="accountTrigger" type="button" aria-label="Сменить аккаунт">
            <span class="account-switcher__avatar" id="accountAvatar">И</span>
          </button>
          <div class="account-switcher__menu" id="accountMenu">
            <button class="account-switcher__item" data-account-user="ivan" type="button">
              <span class="account-switcher__item-avatar" style="background:#59c4ff">И</span>
              <span class="account-switcher__item-text">
                <strong>Иван Иванов</strong>
                <span>@ivan</span>
              </span>
            </button>
            <button class="account-switcher__item" data-account-user="sergei" type="button">
              <span class="account-switcher__item-avatar" style="background:#7b68ee">С</span>
              <span class="account-switcher__item-text">
                <strong>Сергей Иванов</strong>
                <span>@sergei</span>
              </span>
            </button>
            <button class="account-switcher__item" data-account-user="anna" type="button">
              <span class="account-switcher__item-avatar" style="background:#4f83ff">А</span>
              <span class="account-switcher__item-text">
                <strong>Анна Ивлева</strong>
                <span>@anna</span>
              </span>
            </button>
            <div class="account-switcher__sep"></div>
            <button class="account-switcher__item is-muted" data-account-action="logout" type="button">
              <span class="account-switcher__item-text">
                <strong>Выйти</strong>
                <span>Перейти в гостя</span>
              </span>
            </button>
          </div>
        </div>
        """
    ).strip()


def _pages_switcher_markup() -> str:
    return dedent(
        """
        <div class="pages-switcher" id="pagesSwitcher">
          <button class="pages-switcher__trigger" id="pagesTrigger" type="button">
            <span>Мои страницы</span>
            <span class="pages-switcher__count" id="pagesCount">0</span>
          </button>
          <div class="pages-switcher__menu" id="pagesMenu">
            <div class="pages-switcher__menu-head">
              <div class="pages-switcher__menu-title">Мои страницы</div>
              <button class="pages-switcher__create" id="pagesCreateButton" type="button">+ Новая</button>
            </div>
            <div class="pages-switcher__list" id="pagesList"></div>
          </div>
        </div>
        """
    ).strip()


def _presence_markup() -> str:
    return dedent(
        """
        <div class="page-presence is-empty" id="pagePresence">
          <div class="page-presence__avatars" id="pagePresenceAvatars"></div>
          <div class="page-presence__count" id="pagePresenceCount">0</div>
        </div>
        """
    ).strip()


def document_header_markup(
    title: str = "Новая страница",
    subtitle: str = "Добавить описание",
) -> str:
    return dedent(
        f"""
        <header class="doc-head">
          <div class="doc-head__meta">
            <div class="doc-head__title-wrap">
              {file_icon_svg()}
              <div class="doc-head__title-block">
                <div class="doc-head__title-row">
                  <div class="doc-title" id="docHeaderTitle">{title}</div>
                  <div class="doc-head__inline-tools">
                    {_account_switcher_markup()}
                    {_pages_switcher_markup()}
                    {_presence_markup()}
                  </div>
                </div>
                <div class="doc-subtitle" id="docHeaderSubtitle">{subtitle}</div>
              </div>
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
