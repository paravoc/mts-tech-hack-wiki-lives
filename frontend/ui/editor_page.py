from __future__ import annotations

from textwrap import dedent

import streamlit.components.v1 as components

from ui.cursors import cursor_root_variables
from ui.loading_page import document_header_markup, loading_screen_markup


_EMPTY_HINT = "Начните вводить содержимое или нажмите / чтобы использовать команды"


def _toolbar_markup() -> str:
    return dedent(
        """
        <div class="editor-toolbar" id="toolbar">
          <div class="toolbar-group">
            <button class="toolbar-button toolbar-button--ghost" data-tip="Отменить" data-command="undo">&#8630;</button>
            <button class="toolbar-button toolbar-button--ghost" data-tip="Повторить" data-command="redo">&#8631;</button>
          </div>
          <div class="toolbar-sep"></div>
          <div class="toolbar-group">
            <button class="toolbar-button" data-tip="Жирный" data-command="bold">B</button>
            <button class="toolbar-button" data-tip="Курсив" data-command="italic"><em>T</em></button>
            <button class="toolbar-button" data-tip="Зачеркнутый" data-command="strikeThrough"><span class="strike-label">T</span></button>
            <button class="toolbar-button" data-tip="Подчеркнуть" data-command="underline"><span class="underline-label">U</span></button>
          </div>
          <div class="toolbar-sep"></div>
          <div class="toolbar-group">
            <button class="toolbar-button toolbar-button--compound" data-tip="Размер текста" data-menu="font-size" data-active-group="font-size">
              <span>A</span><span class="toolbar-caret">&#9662;</span>
            </button>
          </div>
          <div class="toolbar-sep"></div>
          <div class="toolbar-group">
            <button class="toolbar-button" data-tip="Обычный текст" data-block="p">T</button>
            <button class="toolbar-button" data-tip="Заголовок 1" data-block="h1">H<span class="subscript">1</span></button>
            <button class="toolbar-button" data-tip="Заголовок 2" data-block="h2">H<span class="subscript">2</span></button>
            <button class="toolbar-button" data-tip="Заголовок 3" data-block="h3">H<span class="subscript">3</span></button>
          </div>
          <div class="toolbar-sep"></div>
          <div class="toolbar-group">
            <button class="toolbar-button" data-tip="Выровнять влево" data-command="justifyLeft">&#9776;</button>
            <button class="toolbar-button" data-tip="Выровнять по центру" data-command="justifyCenter">&#8801;</button>
            <button class="toolbar-button" data-tip="Выровнять вправо" data-command="justifyRight">&#9783;</button>
          </div>
          <div class="toolbar-sep"></div>
          <div class="toolbar-group">
            <button class="toolbar-button" data-tip="Маркированный список" data-command="insertUnorderedList">&#8226;&#8801;</button>
            <button class="toolbar-button" data-tip="Нумерованный список" data-command="insertOrderedList">1&#8801;</button>
          </div>
          <div class="toolbar-sep"></div>
          <div class="toolbar-group">
            <button class="toolbar-button" data-tip="Вставить файл" data-upload="file">@</button>
            <button class="toolbar-button toolbar-button--compound" data-tip="Ссылка" data-menu="link" data-active-group="link">
              <span>L</span>
            </button>
            <button class="toolbar-button" data-tip="Ссылка">&lt;/&gt;</button>
            <button class="toolbar-button" data-tip="Цитата" data-block="blockquote">``</button>
            <button class="toolbar-button" data-tip="Изображение" data-upload="image">&#9633;</button>
          </div>
        </div>
        """
    ).strip()


def _selection_toolbar_markup() -> str:
    return dedent(
        """
        <div class="selection-toolbar-wrap">
          <div class="selection-toolbar" id="selectionToolbar">
            <div class="selection-toolbar__group">
              <button class="toolbar-button" data-tip="Жирный" data-command="bold">B</button>
              <button class="toolbar-button" data-tip="Курсив" data-command="italic"><em>T</em></button>
              <button class="toolbar-button" data-tip="Подчеркнуть" data-command="underline"><span class="underline-label">U</span></button>
              <button class="toolbar-button" data-tip="Зачеркнутый" data-command="strikeThrough"><span class="strike-label">T</span></button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button toolbar-button--compound" data-tip="Размер текста" data-menu="font-size" data-active-group="font-size">
                <span>A</span><span class="toolbar-caret">&#9662;</span>
              </button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button toolbar-button--compound" data-tip="Стиль текста" data-menu="text-style" data-active-group="text-style">
                <span>T</span><span class="toolbar-caret">&#9662;</span>
              </button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button toolbar-button--compound" data-tip="Выравнивание" data-menu="alignment" data-active-group="alignment">
                <span>&#8801;</span><span class="toolbar-caret">&#9662;</span>
              </button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button toolbar-button--compound" data-tip="Список" data-menu="list" data-active-group="list">
                <span>1&#8801;</span><span class="toolbar-caret">&#9662;</span>
              </button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button" data-tip="Вставить файл" data-upload="file">@</button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button toolbar-button--compound" data-tip="Ссылка" data-menu="link" data-active-group="link">
                <span>L</span>
              </button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button" data-tip="Ссылка">&lt;/&gt;</button>
            </div>
            <div class="selection-toolbar__group">
              <button class="toolbar-button" data-tip="Цитата" data-block="blockquote">``</button>
            </div>
          </div>

          <div class="floating-menu" id="floatingMenuTextStyle" data-menu-panel="text-style">
            <button class="floating-menu__item" data-tip="Обычный текст" data-block="p">Обычный текст</button>
            <button class="floating-menu__item" data-tip="Заголовок 1" data-block="h1">Заголовок 1</button>
            <button class="floating-menu__item" data-tip="Заголовок 2" data-block="h2">Заголовок 2</button>
            <button class="floating-menu__item" data-tip="Заголовок 3" data-block="h3">Заголовок 3</button>
          </div>

          <div class="floating-menu floating-menu--font-size" id="floatingMenuFontSize" data-menu-panel="font-size">
            <div class="font-size-control">
              <input class="font-size-control__range" id="fontSizeRange" type="range" min="12" max="72" step="1" value="14" />
              <div class="font-size-control__row">
                <input class="font-size-control__input" id="fontSizeInput" type="number" min="12" max="72" step="1" value="14" />
                <span class="font-size-control__suffix">px</span>
              </div>
            </div>
            <div class="font-size-presets">
              <button class="floating-menu__item" data-tip="12 px" data-font-size="12px">12</button>
              <button class="floating-menu__item" data-tip="14 px" data-font-size="14px">14</button>
              <button class="floating-menu__item" data-tip="16 px" data-font-size="16px">16</button>
              <button class="floating-menu__item" data-tip="18 px" data-font-size="18px">18</button>
              <button class="floating-menu__item" data-tip="24 px" data-font-size="24px">24</button>
              <button class="floating-menu__item" data-tip="32 px" data-font-size="32px">32</button>
            </div>
          </div>

          <div class="floating-menu" id="floatingMenuAlignment" data-menu-panel="alignment">
            <button class="floating-menu__item" data-tip="Выровнять влево" data-command="justifyLeft">По левому краю</button>
            <button class="floating-menu__item" data-tip="Выровнять по центру" data-command="justifyCenter">По центру</button>
            <button class="floating-menu__item" data-tip="Выровнять вправо" data-command="justifyRight">По правому краю</button>
          </div>

          <div class="floating-menu" id="floatingMenuList" data-menu-panel="list">
            <button class="floating-menu__item" data-tip="Маркированный список" data-command="insertUnorderedList">Маркированный список</button>
            <button class="floating-menu__item" data-tip="Нумерованный список" data-command="insertOrderedList">Нумерованный список</button>
          </div>

          <div class="floating-menu floating-menu--link" id="floatingMenuLink" data-menu-panel="link">
            <div class="link-menu">
              <div class="link-menu__field">
                <label class="link-menu__label" for="linkTextInput">Выделенный текст</label>
                <input class="link-menu__input" id="linkTextInput" type="text" placeholder="Введите текст ссылки" />
              </div>
              <div class="link-menu__field">
                <label class="link-menu__label" for="linkTargetInput">Ссылка или заголовок</label>
                <input class="link-menu__input" id="linkTargetInput" type="text" placeholder="https://site.ru или выберите заголовок" />
              </div>
              <label class="link-menu__checkbox">
                <input id="linkOpenInNewTab" type="checkbox" />
                <span>Открывать в новой вкладке</span>
              </label>
              <div class="link-menu__headings" id="linkHeadingList"></div>
              <div class="link-menu__actions">
                <button class="link-menu__button link-menu__button--primary" id="linkConfirmButton" type="button">Подтвердить</button>
                <button class="link-menu__button" id="linkCancelButton" type="button">Отменить</button>
              </div>
            </div>
          </div>
        </div>
        """
    ).strip()


def render_editor_page() -> None:
    html = dedent(
        """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <style>
            :root {
              --page: #ffffff;
              --line: #eceff3;
              --toolbar: #f4f7fb;
              --toolbar-border: #d8dde6;
              --text: #272b34;
              --muted: #a7adb8;
              --icon: #8f7cff;
              --shadow: 0 16px 36px rgba(17, 24, 39, 0.12);
              --shadow-soft: 0 12px 26px rgba(17, 24, 39, 0.12);
              --danger: #ff4f8b;
              --selection: #d4e5ff;
              --skeleton: #f0f1f4;
              --top-shell-height: 94px;
__CURSOR_ROOT_VARIABLES__
            }

            * {
              box-sizing: border-box;
            }

            html,
            body {
              margin: 0;
              min-height: 100%;
              background: #ffffff;
              color: var(--text);
              font-family: Inter, "Segoe UI", Arial, sans-serif;
            }

            body {
              overflow: hidden;
            }

            body,
            .app,
            .screen,
            .doc-head,
            .doc-body,
            .doc-shell,
            .editor-shell,
            .page-shell {
              cursor: var(--cursor-default);
            }

            button,
            input,
            textarea {
              font: inherit;
            }

            button,
            .toolbar-button,
            .slash-item,
            .menu-item,
            .menu-panel button,
            .selection-toolbar button,
            .upload-preview__retry,
            .upload-modal__action,
            .embedded-file-chip a,
            .body-editor a.is-ctrl-ready,
            .title-editor a.is-ctrl-ready,
            [role="button"] {
              cursor: var(--cursor-pointer);
            }

            input,
            textarea,
            [contenteditable="true"],
            .title-editor,
            .body-editor {
              cursor: var(--cursor-text);
            }

            .embedded-image-block,
            .embedded-image-frame,
            .block-handle {
              cursor: var(--cursor-grab);
            }

            body[data-cursor-state="grabbing"],
            body[data-cursor-state="grabbing"] * {
              cursor: var(--cursor-grabbing) !important;
            }

            body[data-cursor-state="resize-ew"],
            body[data-cursor-state="resize-ew"] * {
              cursor: var(--cursor-ew) !important;
            }

            body[data-cursor-state="resize-ns"],
            body[data-cursor-state="resize-ns"] * {
              cursor: var(--cursor-ns) !important;
            }

            body[data-cursor-state="resize-nwse"],
            body[data-cursor-state="resize-nwse"] * {
              cursor: var(--cursor-nwse) !important;
            }

            body[data-cursor-state="resize-nesw"],
            body[data-cursor-state="resize-nesw"] * {
              cursor: var(--cursor-nesw) !important;
            }

            .app {
              position: relative;
              min-height: 100vh;
              background: #ffffff;
            }

            .screen {
              position: absolute;
              inset: 0;
              display: flex;
              flex-direction: column;
              background: #ffffff;
              transition: opacity .22s ease, visibility .22s ease;
            }

            .screen.is-hidden {
              opacity: 0;
              visibility: hidden;
              pointer-events: none;
            }

            .doc-head {
              padding: 15px 28px 11px;
              border-bottom: 1px solid var(--line);
              background: #ffffff;
              flex: none;
            }

            .doc-head__meta {
              display: flex;
              gap: 8px;
              align-items: flex-start;
            }

            .doc-icon {
              width: 15px;
              height: 15px;
              flex: none;
              margin-top: 2px;
              color: var(--icon);
            }

            .doc-title {
              font-size: 15px;
              line-height: 1.2;
              font-weight: 700;
              letter-spacing: -0.01em;
              color: #262a33;
            }

            .doc-subtitle {
              margin-top: 4px;
              font-size: 13px;
              line-height: 1.2;
              color: var(--muted);
              font-weight: 500;
            }

            .loading-body {
              min-height: calc(100vh - 58px);
              display: flex;
              align-items: center;
              justify-content: center;
              padding: 24px;
            }

            .loading-skeleton {
              width: 552px;
              max-width: 100%;
              transform: translateY(-22px);
            }

            .loading-skeleton__bar {
              position: relative;
              overflow: hidden;
              height: 20px;
              border-radius: 4px;
              background: var(--skeleton);
            }

            .loading-skeleton__bar::after {
              content: "";
              position: absolute;
              inset: 0;
              transform: translateX(-100%);
              background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0) 0%,
                rgba(255, 255, 255, 0.85) 50%,
                rgba(255, 255, 255, 0) 100%
              );
              animation: shimmer 1.45s ease-in-out infinite;
            }

            .loading-skeleton__bar--short {
              width: 248px;
              margin-bottom: 18px;
            }

            .loading-skeleton__bar--line-1 {
              width: 495px;
              margin-bottom: 18px;
            }

            .loading-skeleton__bar--line-2 {
              width: 552px;
              margin-bottom: 18px;
            }

            .loading-skeleton__bar--line-3 {
              width: 522px;
              margin-bottom: 18px;
            }

            .loading-skeleton__bar--line-4 {
              width: 336px;
            }

            .editor-toolbar {
              display: flex;
              align-items: center;
              gap: 4px;
              min-height: 34px;
              padding: 5px 8px;
              background: var(--toolbar);
              border-bottom: 1px solid var(--line);
              overflow-x: auto;
              flex: none;
            }

            .editor-toolbar,
            .editor-toolbar *,
            .selection-toolbar,
            .selection-toolbar * {
              cursor: var(--cursor-pointer) !important;
            }

            .editor-toolbar::-webkit-scrollbar {
              height: 0;
            }

            .toolbar-group {
              display: flex;
              align-items: center;
              gap: 4px;
              flex: none;
            }

            .toolbar-sep {
              width: 8px;
              flex: none;
            }

            .toolbar-button {
              appearance: none;
              border: 1px solid var(--toolbar-border);
              outline: none;
              min-width: 24px;
              height: 24px;
              padding: 0 7px;
              border-radius: 6px;
              background: linear-gradient(180deg, #ffffff 0%, #f8f9fb 100%);
              color: #6f7685;
              font-size: 12px;
              font-weight: 700;
              display: inline-flex;
              align-items: center;
              justify-content: center;
              gap: 4px;
              white-space: nowrap;
              cursor: pointer;
              transition: border-color .16s ease, color .16s ease, background .16s ease;
            }

            .toolbar-button:hover {
              background: #ffffff;
              color: #596070;
            }

            .toolbar-button:focus-visible {
              border-color: var(--danger);
            }

            .toolbar-button.is-active {
              border-color: var(--danger);
              color: var(--danger);
              background: #ffffff;
            }

            .toolbar-button--ghost {
              min-width: 20px;
              padding: 0 4px;
              border-color: transparent;
              background: transparent;
            }

            .toolbar-button--compound {
              min-width: 30px;
              padding: 0 6px 0 7px;
              gap: 3px;
            }

            .toolbar-caret {
              font-size: 9px;
              line-height: 1;
              position: relative;
              top: 1px;
            }

            .subscript {
              font-size: 9px;
              line-height: 1;
              position: relative;
              top: 2px;
            }

            .strike-label {
              text-decoration: line-through;
            }

            .underline-label {
              text-decoration: underline;
              text-underline-offset: 2px;
            }

            .editor-canvas {
              position: absolute;
              top: var(--top-shell-height);
              left: 0;
              right: 0;
              bottom: 0;
              overflow: auto;
              background: #ffffff;
              scrollbar-width: none;
              -ms-overflow-style: none;
            }

            .editor-canvas::-webkit-scrollbar {
              width: 0;
              height: 0;
            }

            .editor-shell {
              width: 644px;
              max-width: calc(100vw - 80px);
              margin: 0 auto;
              padding: 54px 0 180px;
            }

            .outline-sidebar {
              position: fixed;
              top: 50%;
              left: max(34px, calc(50vw - 470px));
              transform: translateY(-50%);
              display: flex;
              align-items: flex-start;
              gap: 10px;
              z-index: 31;
            }

            .editor-top-shell {
              position: fixed;
              top: 0;
              left: 0;
              right: 0;
              z-index: 30;
              background: #ffffff;
            }

            .outline-sidebar__rail {
              width: 28px;
              height: 44px;
              border-radius: 14px;
              border: 1px solid #e3e8ef;
              background: #ffffff;
              color: var(--danger);
              box-shadow: 0 8px 22px rgba(17, 24, 39, 0.08);
              display: inline-flex;
              align-items: center;
              justify-content: center;
              flex: none;
            }

            .outline-sidebar__rail svg {
              width: 13px;
              height: 13px;
              display: block;
            }

            .outline-sidebar__panel {
              width: 0;
              opacity: 0;
              overflow: hidden;
              pointer-events: none;
              transform: translateX(-4px);
              transition: width .18s ease, opacity .18s ease, transform .18s ease;
            }

            .outline-sidebar:hover .outline-sidebar__panel,
            .outline-sidebar:focus-within .outline-sidebar__panel {
              width: 232px;
              opacity: 1;
              transform: translateX(0);
              pointer-events: auto;
            }

            .outline-sidebar__card {
              width: 232px;
              max-height: min(56vh, 520px);
              overflow: auto;
              padding: 10px 8px;
              border-radius: 16px;
              background: rgba(255, 255, 255, 0.96);
              border: 1px solid #eef1f5;
              box-shadow: 0 16px 36px rgba(17, 24, 39, 0.10);
              scrollbar-width: none;
            }

            .outline-sidebar__card::-webkit-scrollbar {
              width: 0;
              height: 0;
            }

            .outline-sidebar__title {
              padding: 0 8px 8px;
              font-size: 11px;
              font-weight: 700;
              letter-spacing: 0.04em;
              text-transform: uppercase;
              color: #9aa3b2;
            }

            .outline-sidebar__list {
              display: flex;
              flex-direction: column;
              gap: 2px;
            }

            .outline-sidebar__item {
              width: 100%;
              min-height: 30px;
              padding: 0 10px;
              border: 0;
              border-radius: 10px;
              background: transparent;
              color: #38404d;
              font-size: 13px;
              font-weight: 500;
              text-align: left;
              cursor: pointer;
              display: flex;
              align-items: center;
              gap: 8px;
            }

            .outline-sidebar__item:hover {
              background: #f5f7fb;
            }

            .outline-sidebar__item-badge {
              flex: none;
              min-width: 24px;
              height: 18px;
              padding: 0 5px;
              border-radius: 999px;
              border: 1px solid #dde3eb;
              background: #ffffff;
              color: #8c96a7;
              font-size: 10px;
              font-weight: 700;
              display: inline-flex;
              align-items: center;
              justify-content: center;
            }

            .outline-sidebar__item-text {
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .outline-sidebar__item--depth-1 {
              padding-left: 20px;
            }

            .outline-sidebar__item--depth-2 {
              padding-left: 30px;
            }

            .outline-sidebar__empty {
              padding: 0 10px;
              color: #a1a9b7;
              font-size: 12px;
              line-height: 1.5;
            }

            .title-editor {
              margin: 0;
              font-size: 55px;
              line-height: 1.05;
              font-weight: 800;
              letter-spacing: -0.05em;
              text-align: center;
              color: #242933;
              outline: none;
              caret-color: #242933;
            }

            .title-editor:empty::before {
              content: "Новая страница";
              color: #242933;
            }

            .body-editor {
              margin-top: 24px;
              min-height: 320px;
              outline: none;
              color: #2b3140;
              font-size: 14px;
              line-height: 1.75;
              caret-color: #2b3140;
              position: relative;
            }

            .body-editor p,
            .body-editor h1,
            .body-editor h2,
            .body-editor h3,
            .body-editor ul,
            .body-editor ol,
            .body-editor blockquote,
            .body-editor pre {
              margin: 0 0 14px;
            }

            .body-editor p:last-child,
            .body-editor h1:last-child,
            .body-editor h2:last-child,
            .body-editor h3:last-child,
            .body-editor ul:last-child,
            .body-editor ol:last-child,
            .body-editor blockquote:last-child,
            .body-editor pre:last-child {
              margin-bottom: 0;
            }

            .body-editor p {
              min-height: 26px;
            }

            .body-editor h1,
            .body-editor h2,
            .body-editor h3 {
              font-weight: 700;
              color: #242933;
            }

            .body-editor a,
            .title-editor a {
              color: var(--danger);
              text-decoration: none;
            }

            .body-editor a.is-ctrl-ready,
            .title-editor a.is-ctrl-ready {
              color: var(--danger);
              cursor: pointer;
            }

            .body-editor b,
            .body-editor strong,
            .title-editor b,
            .title-editor strong {
              font-weight: 700;
            }

            .body-editor i,
            .body-editor em,
            .title-editor i,
            .title-editor em {
              font-style: italic;
            }

            .body-editor u,
            .title-editor u {
              text-decoration: underline;
              text-underline-offset: 2px;
            }

            .body-editor strike,
            .body-editor s,
            .title-editor strike,
            .title-editor s {
              text-decoration: line-through;
            }

            .body-editor h1 {
              font-size: 32px;
              line-height: 1.15;
            }

            .body-editor h2 {
              font-size: 22px;
              line-height: 1.25;
            }

            .body-editor h3 {
              font-size: 18px;
              line-height: 1.35;
            }

            .body-editor ul,
            .body-editor ol {
              padding-left: 24px;
            }

            .body-editor ul[style*="text-align: center"],
            .body-editor ol[style*="text-align: center"],
            .body-editor ul[align="center"],
            .body-editor ol[align="center"],
            .body-editor li[style*="text-align: center"],
            .body-editor li[align="center"] {
              padding-left: 0;
              padding-inline-start: 0;
              list-style-position: inside;
              text-align: center;
            }

            .body-editor ul[style*="text-align: right"],
            .body-editor ol[style*="text-align: right"],
            .body-editor ul[align="right"],
            .body-editor ol[align="right"],
            .body-editor li[style*="text-align: right"],
            .body-editor li[align="right"] {
              padding-left: 0;
              padding-inline-start: 0;
              list-style-position: inside;
              text-align: right;
            }

            .body-editor blockquote {
              padding-left: 14px;
              border-left: 3px solid #dfe5ee;
              color: #535b6a;
            }

            .body-editor pre {
              padding: 12px 14px;
              border-radius: 10px;
              background: #f6f8fb;
              border: 1px solid #eef1f5;
              white-space: pre-wrap;
            }

            .body-placeholder {
              color: var(--muted);
              text-align: center;
            }

            .slash-menu {
              position: absolute;
              top: 0;
              left: 0;
              width: 190px;
              display: none;
              padding: 10px;
              border-radius: 14px;
              background: #ffffff;
              border: 1px solid #eef1f5;
              box-shadow: var(--shadow-soft);
              z-index: 11;
            }

            .slash-menu.is-visible {
              display: block;
            }

            .slash-item {
              display: flex;
              align-items: center;
              gap: 10px;
              height: 30px;
              padding: 0 8px;
              border-radius: 8px;
              color: #363c49;
              font-size: 13px;
              cursor: pointer;
            }

            .slash-item:hover {
              background: #f6f8fb;
            }

            .slash-item__icon {
              width: 20px;
              height: 20px;
              flex: none;
              border-radius: 8px;
              border: 1px solid #d8dde6;
              background: linear-gradient(180deg, #ffffff 0%, #f7f8fa 100%);
              display: inline-flex;
              align-items: center;
              justify-content: center;
              color: #7b8394;
              font-size: 11px;
              font-weight: 700;
            }

            .selection-toolbar-wrap {
              position: absolute;
              top: 0;
              left: 0;
              display: none;
              z-index: 12;
            }

            .selection-toolbar-wrap.is-visible,
            .selection-toolbar-wrap.has-open-menu {
              display: block;
            }

            .selection-toolbar {
              position: absolute;
              top: 0;
              left: 0;
              align-items: center;
              gap: 4px;
              padding: 6px;
              border-radius: 12px;
              background: #ffffff;
              box-shadow: var(--shadow);
              max-width: min(1000px, calc(100vw - 32px));
              overflow-x: auto;
              white-space: nowrap;
            }

            .selection-toolbar {
              display: none;
            }

            .selection-toolbar-wrap.is-visible .selection-toolbar {
              display: inline-flex;
            }

            .selection-toolbar .toolbar-button {
              height: 22px;
              min-width: 22px;
              font-size: 11px;
            }

            .selection-toolbar .toolbar-button--compound {
              min-width: 30px;
              padding-inline: 6px;
            }

            .selection-toolbar__group {
              display: inline-flex;
              align-items: center;
              gap: 4px;
              flex: none;
            }

            .floating-menu {
              position: fixed;
              top: 0;
              left: 0;
              display: none;
              min-width: 170px;
              padding: 8px;
              border-radius: 12px;
              background: #ffffff;
              border: 1px solid #eef1f5;
              box-shadow: var(--shadow-soft);
              z-index: 13;
            }

            .floating-menu.is-visible {
              display: block;
            }

            .floating-menu__item {
              display: flex;
              align-items: center;
              width: 100%;
              min-height: 30px;
              padding: 0 9px;
              border: 0;
              border-radius: 8px;
              background: transparent;
              color: #363c49;
              font-size: 13px;
              text-align: left;
              cursor: pointer;
            }

            .floating-menu__item:hover {
              background: #f6f8fb;
            }

            .floating-menu--font-size {
              width: 220px;
            }

            .floating-menu--link {
              width: 360px;
              padding: 14px;
            }

            .font-size-control {
              display: flex;
              flex-direction: column;
              gap: 10px;
              padding: 6px 6px 10px;
            }

            .font-size-control__range {
              width: 100%;
              margin: 0;
              accent-color: var(--danger);
            }

            .font-size-control__row {
              display: flex;
              align-items: center;
              gap: 8px;
            }

            .font-size-control__input {
              width: 68px;
              height: 30px;
              padding: 0 10px;
              border-radius: 8px;
              border: 1px solid #d8dde6;
              outline: none;
              color: #363c49;
              background: #ffffff;
            }

            .font-size-control__input:focus {
              border-color: var(--danger);
            }

            .font-size-control__suffix {
              font-size: 12px;
              color: #7b8394;
              font-weight: 600;
            }

            .font-size-presets {
              display: grid;
              grid-template-columns: repeat(3, 1fr);
              gap: 4px;
            }

            .font-size-presets .floating-menu__item {
              justify-content: center;
              min-height: 28px;
              padding: 0;
            }

            .link-menu {
              display: flex;
              flex-direction: column;
              gap: 12px;
            }

            .link-menu__field {
              display: flex;
              flex-direction: column;
              gap: 6px;
            }

            .link-menu__label {
              font-size: 12px;
              line-height: 1.2;
              color: #8f96a4;
            }

            .link-menu__input {
              width: 100%;
              height: 30px;
              padding: 0 10px;
              border-radius: 8px;
              border: 1px solid #d8dde6;
              outline: none;
              color: #363c49;
              background: #ffffff;
            }

            .link-menu__input:focus {
              border-color: var(--danger);
            }

            .link-menu__checkbox {
              display: inline-flex;
              align-items: center;
              gap: 8px;
              font-size: 12px;
              color: #4b5261;
              cursor: pointer;
            }

            .link-menu__checkbox input {
              margin: 0;
              accent-color: var(--danger);
            }

            .link-menu__headings {
              display: flex;
              flex-direction: column;
              gap: 6px;
              max-height: 132px;
              overflow: auto;
            }

            .link-menu__heading {
              display: flex;
              align-items: center;
              gap: 8px;
              min-height: 32px;
              padding: 0 10px;
              border: 0;
              border-radius: 9px;
              background: #f7f8fb;
              color: #363c49;
              font-size: 12px;
              text-align: left;
              cursor: pointer;
            }

            .link-menu__heading:hover {
              background: #f1f3f8;
            }

            .link-menu__heading-badge {
              flex: none;
              min-width: 26px;
              height: 20px;
              padding: 0 6px;
              border-radius: 999px;
              background: #ffffff;
              border: 1px solid #d8dde6;
              color: #7b8394;
              font-size: 10px;
              font-weight: 700;
              display: inline-flex;
              align-items: center;
              justify-content: center;
            }

            .link-menu__empty {
              min-height: 32px;
              padding: 8px 10px;
              border-radius: 9px;
              background: #f7f8fb;
              color: #8f96a4;
              font-size: 12px;
            }

            .link-menu__actions {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 8px;
            }

            .link-menu__button {
              appearance: none;
              border: 0;
              height: 30px;
              border-radius: 8px;
              background: #eceff4;
              color: #2d3340;
              font-size: 13px;
              font-weight: 600;
              cursor: pointer;
            }

            .link-menu__button:disabled {
              opacity: 0.45;
              cursor: default;
            }

            .link-menu__button--primary {
              background: var(--danger);
              color: #ffffff;
            }

            .upload-modal {
              position: fixed;
              inset: 0;
              display: none;
              align-items: center;
              justify-content: center;
              padding: 24px;
              z-index: 40;
            }

            .upload-modal.is-visible {
              display: flex;
            }

            .upload-modal__backdrop {
              position: absolute;
              inset: 0;
              background: rgba(21, 28, 38, 0.16);
            }

            .upload-modal__dialog {
              position: relative;
              width: min(660px, calc(100vw - 32px));
              padding: 22px 22px 18px;
              border-radius: 18px;
              background: #ffffff;
              box-shadow: 0 24px 54px rgba(17, 24, 39, 0.16);
              border: 1px solid #edf1f5;
            }

            .upload-modal__close {
              position: absolute;
              top: 16px;
              right: 16px;
              width: 30px;
              height: 30px;
              border: 0;
              border-radius: 10px;
              background: #f5f7fb;
              color: #39414e;
              font-size: 22px;
              line-height: 1;
              cursor: pointer;
            }

            .upload-modal__title {
              margin: 0 36px 22px 0;
              font-size: 18px;
              line-height: 1.2;
              font-weight: 700;
              color: #2a303a;
            }

            .upload-modal__alert {
              display: none;
              margin-bottom: 18px;
              min-height: 34px;
              padding: 0 16px;
              border-radius: 10px;
              background: rgba(255, 108, 69, 0.12);
              color: #ff6c45;
              font-size: 14px;
              font-weight: 500;
              align-items: center;
              justify-content: center;
              text-align: center;
            }

            .upload-modal__alert.is-visible {
              display: flex;
            }

            .upload-modal__field {
              display: flex;
              flex-direction: column;
              gap: 10px;
            }

            .upload-modal__label {
              font-size: 13px;
              color: #7f8796;
            }

            .upload-dropzone {
              position: relative;
              min-height: 84px;
              padding: 0 18px;
              border-radius: 12px;
              border: 2px dashed #dde5f0;
              background: #ffffff;
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 6px;
              text-align: center;
            }

            .upload-dropzone.is-dragover {
              border-color: #8f7cff;
              background: #faf9ff;
            }

            .upload-dropzone__input {
              position: absolute;
              inset: 0;
              opacity: 0;
              pointer-events: none;
            }

            .upload-dropzone__button {
              border: 0;
              background: transparent;
              color: #3279ff;
              font-size: 14px;
              font-weight: 500;
              cursor: pointer;
            }

            .upload-dropzone__text {
              font-size: 14px;
              color: #3e4654;
            }

            .upload-modal__hint {
              font-size: 12px;
              color: #9aa2b0;
            }

            .upload-preview {
              display: none;
              margin-top: 16px;
            }

            .upload-preview.is-visible {
              display: block;
            }

            .upload-preview__card {
              position: relative;
              width: 128px;
            }

            .upload-preview__thumb {
              width: 128px;
              height: 82px;
              border-radius: 8px;
              background: #f3f5f9 center / cover no-repeat;
              border: 1px solid #eef1f5;
              overflow: hidden;
              display: flex;
              align-items: center;
              justify-content: center;
              color: #8e97a6;
              font-size: 28px;
            }

            .upload-preview__thumb img {
              width: 100%;
              height: 100%;
              object-fit: cover;
              display: block;
            }

            .upload-preview__remove {
              position: absolute;
              top: -6px;
              right: -6px;
              width: 18px;
              height: 18px;
              border: 0;
              border-radius: 999px;
              background: #ffffff;
              box-shadow: 0 4px 12px rgba(17, 24, 39, 0.12);
              color: #ff7b53;
              font-size: 14px;
              line-height: 1;
              cursor: pointer;
            }

            .upload-preview__name-row {
              display: flex;
              justify-content: space-between;
              gap: 10px;
              margin-top: 8px;
              font-size: 13px;
              color: #535c6c;
            }

            .upload-preview__size {
              color: #7f8796;
              white-space: nowrap;
            }

            .upload-preview__error {
              position: absolute;
              inset: 0;
              border-radius: 8px;
              background: rgba(255, 255, 255, 0.84);
              display: none;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              gap: 6px;
              text-align: center;
              padding: 12px;
            }

            .upload-preview__error.is-visible {
              display: flex;
            }

            .upload-preview__error-title {
              font-size: 14px;
              font-weight: 600;
              color: #505968;
            }

            .upload-preview__retry {
              border: 0;
              background: transparent;
              color: #3279ff;
              font-size: 14px;
              cursor: pointer;
            }

            .upload-modal__actions {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 8px;
              margin-top: 18px;
            }

            .upload-modal__action {
              appearance: none;
              border: 0;
              height: 30px;
              border-radius: 8px;
              background: #eef1f5;
              color: #2e3542;
              font-size: 13px;
              font-weight: 600;
              cursor: pointer;
            }

            .upload-modal__action--primary {
              background: var(--danger);
              color: #ffffff;
            }

            .upload-modal__action:disabled {
              opacity: 0.45;
              cursor: default;
            }

            .embedded-image-block {
              position: relative;
              display: inline-block;
              width: min(100%, 610px);
              margin: 8px 10px 10px 0;
              vertical-align: top;
              user-select: none;
            }

            .embedded-image-block.is-align-inline {
              float: none;
              display: inline-block;
              margin: 8px 10px 10px 0;
            }

            .embedded-image-block.is-align-left {
              float: left;
              display: block;
              margin: 8px 18px 12px 0;
            }

            .embedded-image-block.is-align-center {
              float: none;
              display: block;
              margin: 18px auto;
            }

            .embedded-image-block.is-align-right {
              float: right;
              display: block;
              margin: 8px 0 12px 18px;
            }

            .embedded-image-frame {
              position: relative;
              width: 100%;
              border: 2px solid transparent;
              background: #ffffff;
              cursor: var(--cursor-grab);
            }

            .embedded-image-block:hover .embedded-image-frame,
            .embedded-image-block.is-selected .embedded-image-frame {
              border-color: var(--danger);
            }

            .embedded-image-frame img {
              display: block;
              width: 100%;
              height: auto;
              border-radius: 0;
              pointer-events: none;
              -webkit-user-drag: none;
            }

            .embedded-image-handle {
              position: absolute;
              width: 10px;
              height: 10px;
              padding: 0;
              border: 1px solid var(--danger);
              background: var(--danger);
              display: none;
              z-index: 9;
            }

            .embedded-image-block:hover .embedded-image-handle,
            .embedded-image-block.is-selected .embedded-image-handle {
              display: block;
            }

            .embedded-image-handle--nw {
              top: -6px;
              left: -6px;
              cursor: var(--cursor-nwse);
            }

            .embedded-image-handle--ne {
              top: -6px;
              right: -6px;
              cursor: var(--cursor-nesw);
            }

            .embedded-image-handle--sw {
              bottom: -6px;
              left: -6px;
              cursor: var(--cursor-nesw);
            }

            .embedded-image-handle--se {
              bottom: -6px;
              right: -6px;
              cursor: var(--cursor-nwse);
            }

            .embedded-image-handle--w,
            .embedded-image-handle--e,
            .embedded-image-handle--n,
            .embedded-image-handle--s {
              border: 0;
              background: transparent;
            }

            .embedded-image-handle--w,
            .embedded-image-handle--e {
              top: 8px;
              bottom: 8px;
              width: 14px;
              height: auto;
            }

            .embedded-image-handle--w {
              left: -8px;
              cursor: var(--cursor-ew);
            }

            .embedded-image-handle--e {
              right: -8px;
              cursor: var(--cursor-ew);
            }

            .embedded-image-handle--n,
            .embedded-image-handle--s {
              left: 8px;
              right: 8px;
              width: auto;
              height: 14px;
            }

            .embedded-image-handle--n {
              top: -8px;
              cursor: var(--cursor-ns);
            }

            .embedded-image-handle--s {
              bottom: -8px;
              cursor: var(--cursor-ns);
            }

            .image-drop-indicator {
              position: absolute;
              display: none;
              width: 2px;
              background: var(--danger);
              box-shadow: 0 0 0 1px rgba(255, 79, 139, 0.06);
              z-index: 9;
            }

            .image-drop-indicator::before {
              content: "";
              position: absolute;
              left: -3px;
              top: -2px;
              width: 8px;
              height: 8px;
              border-radius: 999px;
              background: var(--danger);
            }

            .image-ghost {
              position: fixed;
              display: none;
              pointer-events: none;
              opacity: 0.36;
              border: 2px solid rgba(255, 79, 139, 0.55);
              background: rgba(255, 255, 255, 0.1);
              box-shadow: 0 18px 36px rgba(17, 24, 39, 0.12);
              z-index: 60;
              overflow: hidden;
            }

            .image-ghost img {
              width: 100%;
              height: 100%;
              display: block;
              object-fit: cover;
            }

            .embedded-file-chip {
              display: inline-flex;
              align-items: center;
              gap: 10px;
              margin: 8px 0;
              padding: 10px 12px;
              border-radius: 14px;
              background: #f7f9fc;
              border: 1px solid #e8edf3;
              color: #343b49;
            }

            .embedded-file-chip a {
              color: #343b49;
              text-decoration: none;
            }

            .embedded-file-chip__ext {
              min-width: 34px;
              height: 22px;
              padding: 0 8px;
              border-radius: 999px;
              background: #ffffff;
              border: 1px solid #dbe2ec;
              color: #8a93a3;
              font-size: 11px;
              font-weight: 700;
              display: inline-flex;
              align-items: center;
              justify-content: center;
            }

            .block-handle {
              position: absolute;
              display: none;
              align-items: center;
              justify-content: center;
              width: 18px;
              height: 22px;
              border: 0;
              background: transparent;
              color: #8f96a4;
              padding: 0;
              z-index: 10;
              pointer-events: auto;
              cursor: pointer;
            }

            .block-handle.is-visible {
              display: inline-flex;
            }

            .block-handle svg {
              width: 12px;
              height: 16px;
              display: block;
            }

            .tooltip {
              position: fixed;
              left: 50%;
              bottom: 18px;
              transform: translateX(-50%);
              display: none;
              align-items: center;
              justify-content: center;
              min-height: 28px;
              padding: 0 12px;
              border-radius: 8px;
              background: #1f232d;
              color: #ffffff;
              font-size: 12px;
              box-shadow: 0 10px 24px rgba(0, 0, 0, 0.2);
              z-index: 20;
            }

            .tooltip.is-visible {
              display: inline-flex;
            }

            ::selection {
              background: var(--selection);
            }

            @keyframes shimmer {
              100% {
                transform: translateX(100%);
              }
            }

            @media (max-width: 900px) {
              .doc-head {
                padding: 14px 18px 11px;
              }

              .outline-sidebar {
                display: none;
              }

              .editor-shell {
                max-width: calc(100vw - 36px);
                padding-top: 42px;
              }

              .title-editor {
                font-size: 42px;
              }

              .loading-skeleton {
                width: 100%;
                transform: none;
              }

              .loading-skeleton__bar--short,
              .loading-skeleton__bar--line-1,
              .loading-skeleton__bar--line-2,
              .loading-skeleton__bar--line-3,
              .loading-skeleton__bar--line-4 {
                width: 100%;
              }
            }
          </style>
        </head>
        <body>
          <div class="app">
            __LOADING_SCREEN__

            <section class="screen is-hidden" id="editorScreen">
              <div class="editor-top-shell">
                __DOCUMENT_HEADER__
                __TOOLBAR__
              </div>
              <div class="editor-canvas" id="editorCanvas">
                <aside class="outline-sidebar" id="outlineSidebar">
                  <div class="outline-sidebar__rail" aria-hidden="true">
                    <svg viewBox="0 0 16 16" fill="currentColor">
                      <rect x="3" y="4" width="10" height="1.5" rx="0.75"></rect>
                      <rect x="3" y="7.25" width="10" height="1.5" rx="0.75"></rect>
                      <rect x="3" y="10.5" width="7" height="1.5" rx="0.75"></rect>
                    </svg>
                  </div>
                  <div class="outline-sidebar__panel">
                    <div class="outline-sidebar__card">
                      <div class="outline-sidebar__title">Навигация</div>
                      <div class="outline-sidebar__list" id="outlineList"></div>
                    </div>
                  </div>
                </aside>
                <div class="editor-shell">
                  <h1 class="title-editor" id="titleEditor" contenteditable="true" spellcheck="false">Новая страница</h1>
                  <div class="body-editor" id="bodyEditor" contenteditable="true" spellcheck="false">
                    <p class="body-placeholder">__EMPTY_HINT__</p>
                  </div>
                </div>

                __SELECTION_TOOLBAR__
                <button class="block-handle" id="blockHandle" aria-hidden="true">
                  <svg viewBox="0 0 12 16" fill="currentColor" aria-hidden="true">
                    <circle cx="3" cy="3" r="1.1"></circle>
                    <circle cx="9" cy="3" r="1.1"></circle>
                    <circle cx="3" cy="8" r="1.1"></circle>
                    <circle cx="9" cy="8" r="1.1"></circle>
                    <circle cx="3" cy="13" r="1.1"></circle>
                    <circle cx="9" cy="13" r="1.1"></circle>
                  </svg>
                </button>
                <div class="slash-menu" id="slashMenu"></div>
              </div>
            </section>

            <div class="tooltip" id="tooltip">Tooltip Text</div>

            <div class="upload-modal" id="uploadModal" aria-hidden="true">
              <div class="upload-modal__backdrop" data-upload-close="1"></div>
              <div class="upload-modal__dialog" role="dialog" aria-modal="true" aria-labelledby="uploadModalTitle">
                <button class="upload-modal__close" id="uploadModalClose" type="button" aria-label="Закрыть">&times;</button>
                <h2 class="upload-modal__title" id="uploadModalTitle">Вставить изображение</h2>
                <div class="upload-modal__alert" id="uploadModalAlert"></div>
                <div class="upload-modal__field">
                  <label class="upload-modal__label" id="uploadModalLabel" for="uploadModalInput">Файл изображения</label>
                  <div class="upload-dropzone" id="uploadDropzone">
                    <input class="upload-dropzone__input" id="uploadModalInput" type="file" />
                    <button class="upload-dropzone__button" id="uploadBrowseButton" type="button">Выберите файл</button>
                    <span class="upload-dropzone__text" id="uploadDropzoneText">или переместите его сюда</span>
                  </div>
                  <div class="upload-modal__hint" id="uploadModalHint">Формат файла: JPG, PNG, GIF. Не более 5 МБ</div>
                </div>
                <div class="upload-preview" id="uploadPreview"></div>
                <div class="upload-modal__actions">
                  <button class="upload-modal__action" id="uploadCancelButton" type="button">Отменить</button>
                  <button class="upload-modal__action upload-modal__action--primary" id="uploadConfirmButton" type="button" disabled>Подтвердить</button>
                </div>
              </div>
            </div>
          </div>

          <script>
            const loadingScreen = document.getElementById("loadingScreen");
            const editorScreen = document.getElementById("editorScreen");
            const editorCanvas = document.getElementById("editorCanvas");
            const editorShell = document.querySelector(".editor-shell");
            const bodyEditor = document.getElementById("bodyEditor");
            const titleEditor = document.getElementById("titleEditor");
            const slashMenu = document.getElementById("slashMenu");
            const tooltip = document.getElementById("tooltip");
            const selectionToolbar = document.getElementById("selectionToolbar");
            const selectionToolbarWrap = document.querySelector(".selection-toolbar-wrap");
            const blockHandle = document.getElementById("blockHandle");
            const outlineList = document.getElementById("outlineList");
            const toolbarButtons = Array.from(document.querySelectorAll(".toolbar-button"));
            const floatingMenuItems = Array.from(document.querySelectorAll(".floating-menu__item"));
            const fontSizeRange = document.getElementById("fontSizeRange");
            const fontSizeInput = document.getElementById("fontSizeInput");
            const linkTextInput = document.getElementById("linkTextInput");
            const linkTargetInput = document.getElementById("linkTargetInput");
            const linkOpenInNewTab = document.getElementById("linkOpenInNewTab");
            const linkHeadingList = document.getElementById("linkHeadingList");
            const linkConfirmButton = document.getElementById("linkConfirmButton");
            const linkCancelButton = document.getElementById("linkCancelButton");
            const uploadModal = document.getElementById("uploadModal");
            const uploadModalClose = document.getElementById("uploadModalClose");
            const uploadModalTitle = document.getElementById("uploadModalTitle");
            const uploadModalAlert = document.getElementById("uploadModalAlert");
            const uploadModalLabel = document.getElementById("uploadModalLabel");
            const uploadModalInput = document.getElementById("uploadModalInput");
            const uploadModalHint = document.getElementById("uploadModalHint");
            const uploadDropzone = document.getElementById("uploadDropzone");
            const uploadDropzoneText = document.getElementById("uploadDropzoneText");
            const uploadBrowseButton = document.getElementById("uploadBrowseButton");
            const uploadPreview = document.getElementById("uploadPreview");
            const uploadCancelButton = document.getElementById("uploadCancelButton");
            const uploadConfirmButton = document.getElementById("uploadConfirmButton");
            const floatingMenus = {
              "font-size": document.getElementById("floatingMenuFontSize"),
              "text-style": document.getElementById("floatingMenuTextStyle"),
              "alignment": document.getElementById("floatingMenuAlignment"),
              "list": document.getElementById("floatingMenuList"),
              "link": document.getElementById("floatingMenuLink")
            };
            const emptyHint = "__EMPTY_HINT__";
            let savedRange = null;
            let tooltipTimer = null;
            let hoveredBlock = null;
            let isHandleHovered = false;
            let activeMenuKey = null;
            let pendingFontSize = "14px";
            let pendingLinkTarget = "";
            let hoveredLink = null;
            let ctrlPressed = false;
            let uploadMode = "image";
            let uploadState = null;
            let selectedImageBlock = null;
            let imageInteraction = null;

            function setCursorState(state) {
              if (!state) {
                document.body.removeAttribute("data-cursor-state");
                return;
              }
              document.body.setAttribute("data-cursor-state", state);
            }

            function clearCursorState() {
              document.body.removeAttribute("data-cursor-state");
            }

            function getResizeCursorState(handle) {
              if (handle === "e" || handle === "w") {
                return "resize-ew";
              }
              if (handle === "n" || handle === "s") {
                return "resize-ns";
              }
              if (handle === "nw" || handle === "se") {
                return "resize-nwse";
              }
              return "resize-nesw";
            }

            const imageGhost = document.createElement("div");
            imageGhost.className = "image-ghost";
            imageGhost.innerHTML = '<img alt="" />';
            editorCanvas.appendChild(imageGhost);
            const imageGhostImage = imageGhost.querySelector("img");

            const imageDropIndicator = document.createElement("div");
            imageDropIndicator.className = "image-drop-indicator";
            editorCanvas.appendChild(imageDropIndicator);

            const slashItems = [
              { icon: "T", label: "Обычный текст", queries: ["текст", "text"], kind: "block", value: "p" },
              { icon: "H1", label: "Заголовок 1", queries: ["загол", "заголовок", "h1"], kind: "block", value: "h1" },
              { icon: "H2", label: "Заголовок 2", queries: ["загол", "заголовок", "h2"], kind: "block", value: "h2" },
              { icon: "H3", label: "Заголовок 3", queries: ["загол", "заголовок", "h3"], kind: "block", value: "h3" },
              { icon: "•", label: "Маркированный список", queries: ["список", "марк"], kind: "list", value: "ul" },
              { icon: "1", label: "Нумерованный список", queries: ["список", "номер"], kind: "list", value: "ol" },
              { icon: "✓", label: "Чеклист", queries: ["чек", "todo"], kind: "list", value: "ul" },
              { icon: "</>", label: "Код", queries: ["код"], kind: "block", value: "pre" },
              { icon: "``", label: "Цитата", queries: ["цитата"], kind: "block", value: "blockquote" },
              { icon: "▣", label: "Изображение", queries: ["изображение", "фото"], kind: "stub", value: "image" }
            ];

            function setLoadingState() {
              loadingScreen.classList.remove("is-hidden");
              editorScreen.classList.add("is-hidden");
            }

            function showEditorState() {
              loadingScreen.classList.add("is-hidden");
              editorScreen.classList.remove("is-hidden");
            }

            function pinComponentFrame() {
              try {
                const frame = window.frameElement;
                if (frame) {
                  frame.style.position = "fixed";
                  frame.style.inset = "0";
                  frame.style.width = "100vw";
                  frame.style.height = "100vh";
                  frame.style.border = "0";
                  frame.style.margin = "0";
                  frame.style.padding = "0";
                  frame.style.zIndex = "1";
                  frame.style.background = "#ffffff";
                }

                const parentDocument = window.parent && window.parent.document;
                if (parentDocument) {
                  const html = parentDocument.documentElement;
                  const body = parentDocument.body;
                  if (html) {
                    html.style.overflow = "hidden";
                    html.style.height = "100vh";
                    html.style.background = "#ffffff";
                  }
                  if (body) {
                    body.style.overflow = "hidden";
                    body.style.height = "100vh";
                    body.style.background = "#ffffff";
                  }

                  const appRoot = parentDocument.querySelector(".stApp");
                  const view = parentDocument.querySelector('[data-testid="stAppViewContainer"]');
                  const block = parentDocument.querySelector('[data-testid="stAppViewBlockContainer"]');
                  const mainBlock = parentDocument.querySelector(".stMainBlockContainer");
                  [appRoot, view, block, mainBlock].forEach((node) => {
                    if (!node) {
                      return;
                    }
                    node.style.overflow = "hidden";
                    node.style.height = "100vh";
                    node.style.maxHeight = "100vh";
                    node.style.padding = "0";
                    node.style.margin = "0";
                    node.style.background = "#ffffff";
                  });
                }
              } catch (error) {
                // Keep the editor usable even if parent iframe styling is unavailable.
              }
            }

            function placeCaretAtEnd(node) {
              if (!node) {
                return;
              }
              const selection = window.getSelection();
              const range = document.createRange();
              range.selectNodeContents(node);
              range.collapse(false);
              selection.removeAllRanges();
              selection.addRange(range);
              saveCurrentRange();
            }

            function resetBodyPlaceholder() {
              bodyEditor.innerHTML = '<p class="body-placeholder">' + emptyHint + "</p>";
            }

            function hasPlaceholder() {
              return Boolean(bodyEditor.querySelector(".body-placeholder"));
            }

            function clearPlaceholderIfNeeded() {
              if (!hasPlaceholder()) {
                return;
              }
              bodyEditor.innerHTML = "<p><br></p>";
              placeCaretAtEnd(bodyEditor.firstElementChild);
            }

            function isEditorEmpty() {
              const hasEmbeddedContent = bodyEditor.querySelector(
                ".embedded-image-block, .embedded-file-chip, img, video, table, iframe"
              );
              if (hasEmbeddedContent) {
                return false;
              }
              const text = bodyEditor.textContent.replace(/\\u200B/g, "").replace(/\\n/g, " ").trim();
              return !text;
            }

            function restorePlaceholderIfEmpty() {
              if (document.activeElement === bodyEditor) {
                return;
              }
              if (isEditorEmpty()) {
                resetBodyPlaceholder();
              }
            }

            function saveCurrentRange() {
              const selection = window.getSelection();
              if (!selection.rangeCount) {
                return;
              }
              const range = selection.getRangeAt(0);
              if (bodyEditor.contains(range.commonAncestorContainer)) {
                savedRange = range.cloneRange();
              }
            }

            function restoreSavedRange() {
              if (!savedRange) {
                return;
              }
              const selection = window.getSelection();
              selection.removeAllRanges();
              selection.addRange(savedRange);
            }

            function getActiveEditableRoot() {
              const sourceNode = savedRange ? savedRange.commonAncestorContainer : window.getSelection().anchorNode;
              if (sourceNode && titleEditor.contains(sourceNode)) {
                return titleEditor;
              }
              return bodyEditor;
            }

            function safeQueryCommandState(command) {
              try {
                return document.queryCommandState(command);
              } catch (error) {
                return false;
              }
            }

            function getCurrentBlockTag() {
              const selection = window.getSelection();
              const sourceNode = savedRange ? savedRange.commonAncestorContainer : selection.anchorNode;
              if (sourceNode && titleEditor.contains(sourceNode)) {
                return "h1";
              }

              const block = findEditableBlock(sourceNode);
              if (!block) {
                return "p";
              }
              return block.tagName.toLowerCase();
            }

            function updateActiveToolbarButtons() {
              if (selectedImageBlock) {
                const align = selectedImageBlock.dataset.align || "inline";
                toolbarButtons.forEach((button) => {
                  button.classList.remove("is-active");
                  if (button.classList.contains("toolbar-button--ghost")) {
                    return;
                  }
                  const command = button.dataset.command;
                  if (command === "justifyLeft" && align === "left") {
                    button.classList.add("is-active");
                  }
                  if (command === "justifyCenter" && align === "center") {
                    button.classList.add("is-active");
                  }
                  if (command === "justifyRight" && align === "right") {
                    button.classList.add("is-active");
                  }
                });
                return;
              }

              const currentBlockTag = getCurrentBlockTag();
              toolbarButtons.forEach((button) => {
                const isOpen = button.classList.contains("is-open");
                button.classList.remove("is-active");

                if (button.classList.contains("toolbar-button--ghost")) {
                  return;
                }

                const command = button.dataset.command;
                const block = button.dataset.block;
                const activeGroup = button.dataset.activeGroup;

                if (activeGroup === "text-style" && ["p", "h1", "h2", "h3", "blockquote"].includes(currentBlockTag)) {
                  button.classList.add("is-active");
                }

                if (activeGroup === "font-size") {
                  const currentFontSize = getCurrentFontSize();
                  if (currentFontSize) {
                    button.classList.add("is-active");
                  }
                }

                if (activeGroup === "list" && (safeQueryCommandState("insertOrderedList") || safeQueryCommandState("insertUnorderedList"))) {
                  button.classList.add("is-active");
                }

                if (activeGroup === "link" && getSelectionLink()) {
                  button.classList.add("is-active");
                }

                if (command && safeQueryCommandState(command)) {
                  button.classList.add("is-active");
                }

                if (block && currentBlockTag === block.toLowerCase()) {
                  button.classList.add("is-active");
                }

                if (isOpen) {
                  button.classList.add("is-active", "is-open");
                }
              });
            }

            function getSelectionContainer() {
              const selection = window.getSelection();
              if (!selection.rangeCount) {
                return null;
              }
              return savedRange ? savedRange.commonAncestorContainer : selection.anchorNode;
            }

            function getClosestLink(node) {
              if (!node) {
                return null;
              }
              const element = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
              return element ? element.closest("a") : null;
            }

            function getSelectionLink() {
              const selection = window.getSelection();
              const sourceNode = savedRange ? savedRange.commonAncestorContainer : selection.anchorNode;
              return getClosestLink(sourceNode);
            }

            function clearHoveredLink() {
              if (hoveredLink) {
                hoveredLink.classList.remove("is-ctrl-ready");
              }
              hoveredLink = null;
            }

            function setHoveredLink(link) {
              if (hoveredLink === link) {
                if (hoveredLink && ctrlPressed) {
                  hoveredLink.classList.add("is-ctrl-ready");
                }
                return;
              }
              clearHoveredLink();
              hoveredLink = link;
              if (hoveredLink && ctrlPressed) {
                hoveredLink.classList.add("is-ctrl-ready");
              }
            }

            function navigateToLink(link) {
              if (!link) {
                return;
              }
              const href = (link.getAttribute("href") || "").trim();
              if (!href) {
                return;
              }

              if (href.startsWith("#")) {
                const target = document.querySelector(href);
                if (target) {
                  target.scrollIntoView({ behavior: "smooth", block: "center" });
                  showTooltip("Переход к заголовку");
                }
                return;
              }

              if (link.getAttribute("target") === "_blank") {
                window.open(href, "_blank", "noopener,noreferrer");
                return;
              }

              window.location.href = href;
            }

            function getSavedSelectionText() {
              if (savedRange) {
                return savedRange.cloneContents().textContent.replace(/\\u200B/g, "").trim();
              }
              const selection = window.getSelection();
              return selection ? selection.toString().trim() : "";
            }

            function ensureHeadingAnchors() {
              const headings = Array.from(bodyEditor.querySelectorAll("h1, h2, h3"));
              headings.forEach((heading, index) => {
                if (!heading.id) {
                  heading.id = "heading-" + (index + 1);
                }
              });
              return headings
                .map((heading, index) => ({
                  id: heading.id || "heading-" + (index + 1),
                  label: heading.textContent.replace(/\\u200B/g, "").trim(),
                  level: heading.tagName.toUpperCase()
                }))
                .filter((item) => item.label);
            }

            function getOutlineItems() {
              const items = [];
              const titleText = titleEditor.textContent.replace(/\\u200B/g, "").trim();
              if (titleText) {
                items.push({
                  id: "titleEditor",
                  label: titleText,
                  level: "H1",
                  depth: 0
                });
              }

              const headings = ensureHeadingAnchors();
              headings.forEach((item) => {
                items.push({
                  id: item.id,
                  label: item.label,
                  level: item.level,
                  depth: item.level === "H1" ? 0 : item.level === "H2" ? 1 : 2
                });
              });

              return items;
            }

            function renderOutline() {
              if (!outlineList) {
                return;
              }

              const items = getOutlineItems();
              if (!items.length) {
                outlineList.innerHTML = '<div class="outline-sidebar__empty">Пока нет заголовков для навигации</div>';
                return;
              }

              outlineList.innerHTML = items.map((item) => `
                <button
                  class="outline-sidebar__item outline-sidebar__item--depth-${item.depth}"
                  type="button"
                  data-outline-target="${item.id}"
                >
                  <span class="outline-sidebar__item-badge">${item.level}</span>
                  <span class="outline-sidebar__item-text">${item.label}</span>
                </button>
              `).join("");
            }

            function normalizeLinkTarget(value) {
              const trimmed = String(value || "").trim();
              if (!trimmed) {
                return "";
              }
              if (trimmed.startsWith("#") || /^[a-z][a-z0-9+.-]*:/i.test(trimmed)) {
                return trimmed;
              }
              if (trimmed.startsWith("www.")) {
                return "https://" + trimmed;
              }
              if (trimmed.includes(".") && !trimmed.includes(" ")) {
                return "https://" + trimmed;
              }
              return trimmed;
            }

            function updateLinkConfirmState() {
              if (!linkConfirmButton) {
                return;
              }
              const hasText = Boolean(linkTextInput && linkTextInput.value.trim());
              const hasTarget = Boolean(normalizeLinkTarget(linkTargetInput ? linkTargetInput.value : ""));
              linkConfirmButton.disabled = !(hasText && hasTarget);
            }

            function renderLinkHeadingList() {
              if (!linkHeadingList) {
                return;
              }
              const headings = ensureHeadingAnchors();
              if (!headings.length) {
                linkHeadingList.innerHTML = '<div class="link-menu__empty">Нет заголовков в текущем тексте</div>';
                return;
              }
              linkHeadingList.innerHTML = headings.map((item) => `
                <button class="link-menu__heading" type="button" data-heading-target="#${item.id}">
                  <span class="link-menu__heading-badge">${item.level}</span>
                  <span>${item.label}</span>
                </button>
              `).join("");
            }

            function populateLinkMenu() {
              const selectedText = getSavedSelectionText();
              const activeLink = getSelectionLink();
              const existingTarget = activeLink ? activeLink.getAttribute("href") || "" : "";
              const existingText = activeLink ? activeLink.textContent.trim() : "";

              if (linkTextInput) {
                linkTextInput.value = selectedText || existingText || "";
              }
              if (linkTargetInput) {
                linkTargetInput.value = pendingLinkTarget || existingTarget;
              }
              if (linkOpenInNewTab) {
                linkOpenInNewTab.checked = Boolean(
                  activeLink &&
                  activeLink.getAttribute("target") === "_blank"
                );
              }

              renderLinkHeadingList();
              updateLinkConfirmState();
            }

            function applyLink() {
              const rawText = linkTextInput ? linkTextInput.value.trim() : "";
              const href = normalizeLinkTarget(linkTargetInput ? linkTargetInput.value : "");

              if (!rawText || !href) {
                updateLinkConfirmState();
                return;
              }

              pendingLinkTarget = href;
              const activeRoot = getActiveEditableRoot();
              activeRoot.focus();
              restoreSavedRange();

              const selection = window.getSelection();
              if (!selection.rangeCount) {
                return;
              }

              const range = selection.getRangeAt(0);
              const activeLink = getSelectionLink();

              if (range.collapsed) {
                const anchor = activeLink || document.createElement("a");
                anchor.href = href;
                anchor.textContent = rawText;
                if (linkOpenInNewTab && linkOpenInNewTab.checked && !href.startsWith("#")) {
                  anchor.target = "_blank";
                  anchor.rel = "noopener noreferrer";
                } else {
                  anchor.removeAttribute("target");
                  anchor.removeAttribute("rel");
                }
                if (!activeLink) {
                  range.insertNode(anchor);
                }
                const nextRange = document.createRange();
                nextRange.setStartAfter(anchor);
                nextRange.collapse(true);
                selection.removeAllRanges();
                selection.addRange(nextRange);
                savedRange = nextRange.cloneRange();
              } else {
                document.execCommand("createLink", false, href);
                const linkNode = getClosestLink(selection.anchorNode) || getClosestLink(selection.focusNode) || activeLink;
                if (linkNode) {
                  linkNode.setAttribute("href", href);
                  linkNode.textContent = rawText;
                  if (linkOpenInNewTab && linkOpenInNewTab.checked && !href.startsWith("#")) {
                    linkNode.setAttribute("target", "_blank");
                    linkNode.setAttribute("rel", "noopener noreferrer");
                  } else {
                    linkNode.removeAttribute("target");
                    linkNode.removeAttribute("rel");
                  }
                }
                saveCurrentRange();
              }

              hideFloatingMenus();
              updateActiveToolbarButtons();
              updateSelectionToolbar();
              showTooltip("Ссылка");
            }

            function getUploadConfig(mode) {
              if (mode === "file") {
                return {
                  mode: "file",
                  title: "Вставить файл",
                  label: "Файл",
                  browse: "Выберите файлы",
                  trail: "или переместите их сюда",
                  hint: "Формат файла: TXT, CSV, XLS, XLSX. Не более 2 МБ",
                  maxBytes: 2 * 1024 * 1024,
                  accept: ".txt,.csv,.xls,.xlsx,text/plain,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                  formats: ["txt", "csv", "xls", "xlsx"]
                };
              }

              return {
                mode: "image",
                title: "Вставить изображение",
                label: "Файл изображения",
                browse: "Выберите файл",
                trail: "или переместите его сюда",
                hint: "Формат файла: JPG, PNG, GIF. Не более 5 МБ",
                maxBytes: 5 * 1024 * 1024,
                accept: ".jpg,.jpeg,.png,.gif,image/jpeg,image/png,image/gif",
                formats: ["jpg", "jpeg", "png", "gif"]
              };
            }

            function formatFileSize(bytes) {
              if (!bytes) {
                return "0 Б";
              }
              if (bytes >= 1024 * 1024) {
                return (bytes / (1024 * 1024)).toFixed(1).replace(".0", "") + " МБ";
              }
              if (bytes >= 1024) {
                return Math.round(bytes / 1024) + " КБ";
              }
              return bytes + " Б";
            }

            function resetUploadState() {
              if (uploadState && uploadState.objectUrl) {
                URL.revokeObjectURL(uploadState.objectUrl);
              }
              uploadState = null;
              if (uploadModalInput) {
                uploadModalInput.value = "";
              }
            }

            function setUploadAlert(message) {
              if (!uploadModalAlert) {
                return;
              }
              uploadModalAlert.textContent = message || "";
              uploadModalAlert.classList.toggle("is-visible", Boolean(message));
            }

            function buildUploadPreviewCard() {
              if (!uploadState) {
                return "";
              }

              const name = uploadState.file.name || "file";
              const size = formatFileSize(uploadState.file.size || 0);
              const ext = name.includes(".") ? name.split(".").pop().toUpperCase() : "FILE";
              const thumbContent = uploadMode === "image" && uploadState.objectUrl
                ? `<img src="${uploadState.objectUrl}" alt="${name}" />`
                : `<span>${ext}</span>`;
              const errorHtml = uploadState.error === "load"
                ? `
                    <div class="upload-preview__error is-visible">
                      <div class="upload-preview__error-title">Ошибка загрузки</div>
                      <button class="upload-preview__retry" id="uploadRetryButton" type="button">Повторить</button>
                    </div>
                  `
                : "";

              return `
                <div class="upload-preview__card">
                  <div class="upload-preview__thumb">
                    ${thumbContent}
                    ${errorHtml}
                  </div>
                  <button class="upload-preview__remove" id="uploadRemoveButton" type="button" aria-label="Удалить">&times;</button>
                  <div class="upload-preview__name-row">
                    <span>${name}</span>
                    <span class="upload-preview__size">${size}</span>
                  </div>
                </div>
              `;
            }

            function renderUploadModal() {
              const config = getUploadConfig(uploadMode);

              if (uploadModalTitle) {
                uploadModalTitle.textContent = config.title;
              }
              if (uploadModalLabel) {
                uploadModalLabel.textContent = config.label;
              }
              if (uploadModalHint) {
                uploadModalHint.textContent = config.hint;
              }
              if (uploadBrowseButton) {
                uploadBrowseButton.textContent = config.browse;
              }
              if (uploadDropzoneText) {
                uploadDropzoneText.textContent = config.trail;
              }
              if (uploadModalInput) {
                uploadModalInput.accept = config.accept;
              }

              let alertMessage = "";
              if (uploadState && uploadState.error === "format") {
                alertMessage = uploadMode === "image"
                  ? "Для загрузки доступны файлы в форматах JPG, PNG, GIF"
                  : "Для загрузки доступны файлы в форматах TXT, CSV, XLS, XLSX";
              } else if (uploadState && uploadState.error === "size") {
                alertMessage = uploadMode === "image"
                  ? "Для загрузки доступны файлы не более 5 МБ"
                  : "Для загрузки доступны файлы не более 2 МБ";
              }
              setUploadAlert(alertMessage);

              const showPreview = Boolean(
                uploadState &&
                (!uploadState.error || uploadState.error === "load")
              );

              if (uploadPreview) {
                uploadPreview.innerHTML = showPreview ? buildUploadPreviewCard() : "";
                uploadPreview.classList.toggle("is-visible", showPreview);
              }

              if (uploadConfirmButton) {
                uploadConfirmButton.disabled = !uploadState || Boolean(uploadState.error);
              }
            }

            function closeUploadModal() {
              if (!uploadModal) {
                return;
              }
              uploadModal.classList.remove("is-visible");
              uploadModal.setAttribute("aria-hidden", "true");
              uploadDropzone.classList.remove("is-dragover");
              resetUploadState();
              renderUploadModal();
            }

            function openUploadModal(mode) {
              uploadMode = mode === "file" ? "file" : "image";
              hideFloatingMenus();
              resetUploadState();
              renderUploadModal();
              if (!uploadModal) {
                return;
              }
              uploadModal.classList.add("is-visible");
              uploadModal.setAttribute("aria-hidden", "false");
            }

            function readFileAsDataUrl(file) {
              return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(String(reader.result || ""));
                reader.onerror = () => reject(new Error("read"));
                reader.readAsDataURL(file);
              });
            }

            function createImageState(file) {
              return new Promise((resolve) => {
                const objectUrl = URL.createObjectURL(file);
                const image = new Image();
                image.onload = () => resolve({ file, objectUrl, error: null });
                image.onerror = () => resolve({ file, objectUrl, error: "load" });
                image.src = objectUrl;
              });
            }

            async function handleUploadFile(file) {
              const config = getUploadConfig(uploadMode);
              if (!file) {
                return;
              }

              const extension = file.name.includes(".") ? file.name.split(".").pop().toLowerCase() : "";
              if (!config.formats.includes(extension)) {
                resetUploadState();
                uploadState = { file, error: "format" };
                renderUploadModal();
                return;
              }

              if (file.size > config.maxBytes) {
                resetUploadState();
                uploadState = { file, error: "size" };
                renderUploadModal();
                return;
              }

              resetUploadState();
              if (uploadMode === "image") {
                uploadState = await createImageState(file);
              } else {
                uploadState = { file, error: null };
              }
              renderUploadModal();
            }

            async function insertImageFile(file) {
              if (!file) {
                return;
              }

              const imageConfig = getUploadConfig("image");
              const type = String(file.type || "").toLowerCase();
              const extension = file.name && file.name.includes(".")
                ? file.name.split(".").pop().toLowerCase()
                : "";

              if (
                !type.startsWith("image/") &&
                (!extension || !imageConfig.formats.includes(extension))
              ) {
                showTooltip("Только JPG, PNG, GIF");
                return;
              }

              if (file.size > imageConfig.maxBytes) {
                showTooltip("Не более 5 МБ");
                return;
              }

              const safeName = file.name || "clipboard-image.png";
              const normalizedFile = file.name
                ? file
                : new File([file], safeName, { type: file.type || "image/png" });

              const dataUrl = await readFileAsDataUrl(normalizedFile);
              const block = createImageBlock(dataUrl, safeName);
              insertInlineNode(block);
              selectImageBlock(block);
              saveCurrentRange();
              updateActiveToolbarButtons();
              updateSelectionToolbar();
              updateBlockHandleFromSelection();
              showTooltip("Изображение");
            }

            function insertNodeWithTrailingParagraph(node) {
              if (hasPlaceholder()) {
                clearPlaceholderIfNeeded();
              }

              bodyEditor.focus();
              restoreSavedRange();

              const selection = window.getSelection();
              if (!selection.rangeCount) {
                bodyEditor.appendChild(node);
                const paragraph = document.createElement("p");
                paragraph.innerHTML = "<br>";
                bodyEditor.appendChild(paragraph);
                placeCaretAtEnd(paragraph);
                return;
              }

              const range = selection.getRangeAt(0);
              range.deleteContents();
              range.insertNode(node);

              const paragraph = document.createElement("p");
              paragraph.innerHTML = "<br>";
              node.parentNode.insertBefore(paragraph, node.nextSibling);
              placeCaretAtEnd(paragraph);
            }

            function insertInlineNode(node) {
              if (hasPlaceholder()) {
                clearPlaceholderIfNeeded();
              }

              bodyEditor.focus();
              restoreSavedRange();

              const selection = window.getSelection();
              if (!selection.rangeCount) {
                const paragraph = createEmptyParagraph();
                paragraph.innerHTML = "";
                const spacer = document.createTextNode("\u00A0");
                paragraph.appendChild(node);
                paragraph.appendChild(spacer);
                bodyEditor.appendChild(paragraph);
                const range = document.createRange();
                range.setStartAfter(spacer);
                range.collapse(true);
                selection.removeAllRanges();
                selection.addRange(range);
                savedRange = range.cloneRange();
                return;
              }

              const range = selection.getRangeAt(0);
              range.deleteContents();
              range.insertNode(node);

              const spacer = document.createTextNode("\u00A0");
              if (node.parentNode) {
                node.parentNode.insertBefore(spacer, node.nextSibling);
              }

              const nextRange = document.createRange();
              nextRange.setStartAfter(spacer);
              nextRange.collapse(true);
              selection.removeAllRanges();
              selection.addRange(nextRange);
              savedRange = nextRange.cloneRange();
            }

            function createEmptyParagraph() {
              const paragraph = document.createElement("p");
              paragraph.innerHTML = "<br>";
              return paragraph;
            }

            function ensureTrailingParagraphAfter(node) {
              if (!node || !node.parentNode) {
                return;
              }
              const next = node.nextElementSibling;
              if (next && isEditableBlock(next)) {
                return;
              }
              node.parentNode.insertBefore(createEmptyParagraph(), node.nextSibling);
            }

            function getImageMaxWidth() {
              const shellWidth = editorShell ? editorShell.clientWidth : 640;
              const bodyWidth = bodyEditor ? bodyEditor.clientWidth : shellWidth;
              return Math.max(260, Math.min(shellWidth, bodyWidth));
            }

            function getImageMaxHeight() {
              return Math.max(200, Math.min(window.innerHeight - 160, 900));
            }

            function setImageBlockDimensions(block, width, height) {
              if (!block) {
                return;
              }
              const maxWidth = getImageMaxWidth();
              const nextWidth = Math.max(220, Math.min(maxWidth, Math.round(width || maxWidth)));
              block.style.width = nextWidth + "px";
              block.dataset.width = String(nextWidth);

              const frame = block.querySelector(".embedded-image-frame");
              const image = block.querySelector("img");
              const hasExplicitHeight = Number.isFinite(height) && height !== null;

              if (frame && image) {
                if (hasExplicitHeight) {
                  const nextHeight = Math.max(120, Math.min(getImageMaxHeight(), Math.round(height)));
                  frame.style.height = nextHeight + "px";
                  image.style.height = "100%";
                  image.style.objectFit = "fill";
                  block.dataset.height = String(nextHeight);
                } else {
                  frame.style.height = "";
                  image.style.height = "auto";
                  image.style.objectFit = "";
                  delete block.dataset.height;
                }
              }
            }

            function setImageAlignment(block, align) {
              if (!block) {
                return;
              }
              const nextAlign = ["left", "center", "right", "inline"].includes(align) ? align : "inline";
              block.dataset.align = nextAlign;
              block.classList.remove("is-align-inline", "is-align-left", "is-align-center", "is-align-right");
              block.classList.add("is-align-" + nextAlign);
            }

            function setImageBlockWidth(block, width) {
              if (!block) {
                return;
              }
              const explicitHeight = block.dataset.height ? Number(block.dataset.height) : null;
              setImageBlockDimensions(block, width, explicitHeight);
            }

            function setImageBlockHeight(block, height) {
              if (!block) {
                return;
              }
              const currentWidth = Number(block.dataset.width) || Math.round(block.getBoundingClientRect().width || getImageMaxWidth());
              setImageBlockDimensions(block, currentWidth, height);
            }

            function hideImageGhost() {
              imageGhost.style.display = "none";
              imageGhostImage.removeAttribute("src");
            }

            function showImageGhost(rect, src) {
              if (!rect || !src) {
                hideImageGhost();
                return;
              }
              imageGhostImage.src = src;
              imageGhost.style.display = "block";
              imageGhost.style.left = rect.left + "px";
              imageGhost.style.top = rect.top + "px";
              imageGhost.style.width = rect.width + "px";
              imageGhost.style.height = rect.height + "px";
            }

            function hideImageDropIndicator() {
              imageDropIndicator.style.display = "none";
            }

            function showImageDropIndicator(target) {
              if (!target) {
                hideImageDropIndicator();
                return;
              }
              const canvasRect = editorCanvas.getBoundingClientRect();
              const rect = target.rect;
              imageDropIndicator.style.display = "block";
              imageDropIndicator.style.left = rect.left - canvasRect.left + editorCanvas.scrollLeft + "px";
              imageDropIndicator.style.top = rect.top - canvasRect.top + editorCanvas.scrollTop + "px";
              imageDropIndicator.style.height = Math.max(24, rect.height || 24) + "px";
            }

            function clearSelectedImageBlock() {
              if (selectedImageBlock) {
                selectedImageBlock.classList.remove("is-selected");
              }
              selectedImageBlock = null;
              hideImageGhost();
              hideImageDropIndicator();
            }

            function selectImageBlock(block) {
              if (!block) {
                clearSelectedImageBlock();
                return;
              }
              if (selectedImageBlock && selectedImageBlock !== block) {
                selectedImageBlock.classList.remove("is-selected");
              }
              selectedImageBlock = block;
              selectedImageBlock.classList.add("is-selected");
              hideFloatingMenus();
              selectionToolbarWrap.classList.remove("is-visible");
              hideBlockHandle();
            }

            function createImageBlock(dataUrl, name) {
              const block = document.createElement("span");
              block.className = "embedded-image-block";
              block.contentEditable = "false";
              block.dataset.kind = "image";

              const frame = document.createElement("div");
              frame.className = "embedded-image-frame";
              const image = document.createElement("img");
              image.src = dataUrl;
              image.alt = name;
              image.draggable = false;
              frame.appendChild(image);

              ["nw", "ne", "sw", "se", "w", "e", "n", "s"].forEach((handle) => {
                const node = document.createElement("button");
                node.type = "button";
                node.className = "embedded-image-handle embedded-image-handle--" + handle;
                node.dataset.imageResize = handle;
                frame.appendChild(node);
              });

              block.appendChild(frame);
              setImageBlockWidth(block, Math.min(getImageMaxWidth(), 610));
              setImageAlignment(block, "inline");
              return block;
            }

            function removeSelectedImageBlock(block) {
              const target = block || selectedImageBlock;
              if (!target || !target.parentNode) {
                return;
              }
              const nextFocus = target.nextElementSibling && isEditableBlock(target.nextElementSibling)
                ? target.nextElementSibling
                : target.previousElementSibling && isEditableBlock(target.previousElementSibling)
                  ? target.previousElementSibling
                  : null;
              target.remove();
              clearSelectedImageBlock();
              if (!bodyEditor.children.length) {
                resetBodyPlaceholder();
              } else if (nextFocus) {
                bodyEditor.focus();
                placeCaretAtEnd(nextFocus);
              }
            }

            function getCaretRangeFromPoint(clientX, clientY) {
              if (document.caretRangeFromPoint) {
                return document.caretRangeFromPoint(clientX, clientY);
              }
              if (document.caretPositionFromPoint) {
                const position = document.caretPositionFromPoint(clientX, clientY);
                if (!position) {
                  return null;
                }
                const range = document.createRange();
                range.setStart(position.offsetNode, position.offset);
                range.collapse(true);
                return range;
              }
              return null;
            }

            function getImageDropTarget(clientX, clientY, draggedBlock) {
              const range = getCaretRangeFromPoint(clientX, clientY);
              if (!range) {
                return null;
              }
              if (!bodyEditor.contains(range.commonAncestorContainer)) {
                return null;
              }

              const owner = range.startContainer.nodeType === Node.ELEMENT_NODE ? range.startContainer : range.startContainer.parentElement;
              const ownerImage = owner ? owner.closest(".embedded-image-block") : null;
              if (ownerImage && ownerImage === draggedBlock) {
                const rect = draggedBlock.getBoundingClientRect();
                return {
                  range: null,
                  rect: {
                    left: rect.right,
                    top: rect.top,
                    height: rect.height
                  }
                };
              }

              let rect = null;
              const rects = Array.from(range.getClientRects()).filter((item) => item.width || item.height);
              if (rects.length) {
                rect = rects[0];
              } else {
                const block = findEditableBlock(range.startContainer);
                if (block) {
                  const blockRect = block.getBoundingClientRect();
                  rect = {
                    left: blockRect.left,
                    top: blockRect.top,
                    height: blockRect.height
                  };
                }
              }

              return {
                range: range.cloneRange(),
                rect: rect || { left: bodyEditor.getBoundingClientRect().left, top: bodyEditor.getBoundingClientRect().top, height: 26 }
              };
            }

            function commitImageMove(block, clientX, clientY) {
              if (!block || !block.parentNode) {
                return;
              }
              const target = getImageDropTarget(clientX, clientY, block);
              if (!target || !target.range) {
                return;
              }

              const range = target.range;
              const selection = window.getSelection();
              block.remove();
              range.insertNode(block);

              const spacer = document.createTextNode("\u00A0");
              if (block.parentNode) {
                block.parentNode.insertBefore(spacer, block.nextSibling);
              }

              if (selection) {
                const nextRange = document.createRange();
                nextRange.setStartAfter(spacer);
                nextRange.collapse(true);
                selection.removeAllRanges();
                selection.addRange(nextRange);
                savedRange = nextRange.cloneRange();
              }
            }

            function finishImageInteraction(event) {
              if (!imageInteraction) {
                return;
              }

              const interaction = imageInteraction;
              imageInteraction = null;
              clearCursorState();
              document.removeEventListener("pointermove", handleImageInteractionMove);
              document.removeEventListener("pointerup", finishImageInteraction);
              document.removeEventListener("pointercancel", finishImageInteraction);

              if (interaction.type === "resize" && interaction.previewRect) {
                if (interaction.handle === "e" || interaction.handle === "w") {
                  setImageBlockWidth(interaction.block, interaction.previewRect.width);
                } else if (interaction.handle === "n" || interaction.handle === "s") {
                  setImageBlockHeight(interaction.block, interaction.previewRect.height);
                } else {
                  setImageBlockDimensions(interaction.block, interaction.previewRect.width, interaction.previewRect.height);
                }
              }

              if (interaction.type === "move" && interaction.hasMoved) {
                commitImageMove(interaction.block, event.clientX, event.clientY);
              }

              hideImageGhost();
              hideImageDropIndicator();
              selectImageBlock(interaction.block);
              updateBlockHandleFromSelection();
            }

            function handleImageInteractionMove(event) {
              if (!imageInteraction) {
                return;
              }
              event.preventDefault();

              if (imageInteraction.type === "resize") {
                const dx = event.clientX - imageInteraction.startX;
                const dy = event.clientY - imageInteraction.startY;
                const startRect = imageInteraction.startRect;
                let width = startRect.width;
                let height = startRect.height;
                let left = startRect.left;
                let top = startRect.top;
                const ratio = imageInteraction.aspectRatio || 1;
                const handle = imageInteraction.handle;

                if (handle === "e" || handle === "w") {
                  if (handle === "e") {
                    width = startRect.width + dx;
                  } else {
                    width = startRect.width - dx;
                  }
                  width = Math.max(220, Math.min(getImageMaxWidth(), width));
                  height = startRect.height;
                  if (handle === "w") {
                    left = startRect.right - width;
                  }
                } else if (handle === "n" || handle === "s") {
                  if (handle === "s") {
                    height = startRect.height + dy;
                  } else {
                    height = startRect.height - dy;
                  }
                  height = Math.max(120, Math.min(getImageMaxHeight(), height));
                  width = startRect.width;
                  if (handle === "n") {
                    top = startRect.bottom - height;
                  }
                } else {
                  if (handle.includes("e")) {
                    width = startRect.width + dx;
                  }
                  if (handle.includes("w")) {
                    width = startRect.width - dx;
                  }

                  width = Math.max(220, Math.min(getImageMaxWidth(), width));
                  height = Math.max(120, Math.min(getImageMaxHeight(), width / ratio));

                  if (handle.includes("w")) {
                    left = startRect.right - width;
                  }
                  if (handle.includes("n")) {
                    top = startRect.bottom - height;
                  }
                }

                imageInteraction.previewRect = { left, top, width, height };
                showImageGhost(imageInteraction.previewRect, imageInteraction.src);
                return;
              }

              const moveX = Math.abs(event.clientX - imageInteraction.startX);
              const moveY = Math.abs(event.clientY - imageInteraction.startY);
              if (!imageInteraction.hasMoved && moveX + moveY < 6) {
                return;
              }

              imageInteraction.hasMoved = true;
              const rect = {
                left: event.clientX - imageInteraction.offsetX,
                top: event.clientY - imageInteraction.offsetY,
                width: imageInteraction.startRect.width,
                height: imageInteraction.startRect.height
              };
              showImageGhost(rect, imageInteraction.src);
              const target = getImageDropTarget(event.clientX, event.clientY, imageInteraction.block);
              imageInteraction.dropTarget = target;
              showImageDropIndicator(target);
            }

            function startImageResize(block, handle, event) {
              if (!block) {
                return;
              }
              event.preventDefault();
              event.stopPropagation();
              selectImageBlock(block);
              setCursorState(getResizeCursorState(handle));
              const rect = block.getBoundingClientRect();
              const image = block.querySelector("img");
              imageInteraction = {
                type: "resize",
                block,
                handle,
                startX: event.clientX,
                startY: event.clientY,
                startRect: rect,
                aspectRatio: rect.width / Math.max(rect.height, 1),
                src: image ? image.src : "",
                previewRect: { left: rect.left, top: rect.top, width: rect.width, height: rect.height }
              };
              showImageGhost(imageInteraction.previewRect, imageInteraction.src);
              document.addEventListener("pointermove", handleImageInteractionMove);
              document.addEventListener("pointerup", finishImageInteraction);
              document.addEventListener("pointercancel", finishImageInteraction);
            }

            function startImageMove(block, event) {
              if (!block || event.button !== 0) {
                return;
              }
              event.preventDefault();
              selectImageBlock(block);
              setCursorState("grabbing");
              const rect = block.getBoundingClientRect();
              const image = block.querySelector("img");
              imageInteraction = {
                type: "move",
                block,
                startX: event.clientX,
                startY: event.clientY,
                startRect: rect,
                offsetX: event.clientX - rect.left,
                offsetY: event.clientY - rect.top,
                src: image ? image.src : "",
                hasMoved: false,
                dropTarget: null
              };
              document.addEventListener("pointermove", handleImageInteractionMove);
              document.addEventListener("pointerup", finishImageInteraction);
              document.addEventListener("pointercancel", finishImageInteraction);
            }

            async function confirmUpload() {
              if (!uploadState || uploadState.error) {
                return;
              }

              try {
                if (uploadMode === "image") {
                  await insertImageFile(uploadState.file);
                } else {
                  const dataUrl = await readFileAsDataUrl(uploadState.file);
                  const block = document.createElement("div");
                  block.className = "embedded-file-chip";
                  block.contentEditable = "false";
                  const ext = uploadState.file.name.includes(".")
                    ? uploadState.file.name.split(".").pop().toUpperCase()
                    : "FILE";
                  const badge = document.createElement("span");
                  badge.className = "embedded-file-chip__ext";
                  badge.textContent = ext;
                  const anchor = document.createElement("a");
                  anchor.href = dataUrl;
                  anchor.download = uploadState.file.name;
                  anchor.textContent = uploadState.file.name;
                  block.appendChild(badge);
                  block.appendChild(anchor);
                  insertNodeWithTrailingParagraph(block);
                }

                closeUploadModal();
                saveCurrentRange();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
                updateBlockHandleFromSelection();
                showTooltip(uploadMode === "image" ? "Изображение" : "Файл");
              } catch (error) {
                if (uploadState) {
                  uploadState.error = "load";
                }
                renderUploadModal();
              }
            }

            function getCurrentFontSize() {
              const sourceNode = getSelectionContainer();
              if (!sourceNode) {
                return pendingFontSize;
              }
              const element = sourceNode.nodeType === Node.ELEMENT_NODE ? sourceNode : sourceNode.parentElement;
              if (!element) {
                return pendingFontSize;
              }
              return window.getComputedStyle(element).fontSize;
            }

            function normalizeFontSizeValue(value) {
              const parsed = parseInt(String(value || "").replace("px", "").trim(), 10);
              if (Number.isNaN(parsed)) {
                return 14;
              }
              return Math.max(12, Math.min(72, parsed));
            }

            function syncFontSizeControls(value) {
              const normalized = normalizeFontSizeValue(value);
              if (fontSizeRange) {
                fontSizeRange.value = String(normalized);
              }
              if (fontSizeInput) {
                fontSizeInput.value = String(normalized);
              }
              pendingFontSize = normalized + "px";
            }

            function applyBlockFormat(block) {
              const currentBlockTag = getCurrentBlockTag();
              const nextBlock = currentBlockTag === block.toLowerCase() ? "p" : block;
              document.execCommand("formatBlock", false, nextBlock);
            }

            function applyFontSize(fontSize) {
              const normalized = normalizeFontSizeValue(fontSize) + "px";
              pendingFontSize = normalized;
              const selection = window.getSelection();
              if (!selection.rangeCount) {
                syncFontSizeControls(normalized);
                return;
              }

              const range = selection.getRangeAt(0);
              if (selection.isCollapsed) {
                const root = getActiveEditableRoot();
                if (root === titleEditor) {
                  titleEditor.style.fontSize = normalized;
                }
                syncFontSizeControls(normalized);
                return;
              }

              const startElement = range.startContainer.nodeType === Node.ELEMENT_NODE ? range.startContainer : range.startContainer.parentElement;
              const endElement = range.endContainer.nodeType === Node.ELEMENT_NODE ? range.endContainer : range.endContainer.parentElement;
              const startWrapper = startElement ? startElement.closest('[data-inline-font-size="1"]') : null;
              const endWrapper = endElement ? endElement.closest('[data-inline-font-size="1"]') : null;

              if (startWrapper && startWrapper === endWrapper) {
                startWrapper.style.fontSize = normalized;
                startWrapper.style.lineHeight = "inherit";
                startWrapper.style.verticalAlign = "baseline";
                syncFontSizeControls(normalized);
                return;
              }

              try {
                const span = document.createElement("span");
                span.style.fontSize = normalized;
                span.style.lineHeight = "inherit";
                span.style.verticalAlign = "baseline";
                span.dataset.inlineFontSize = "1";
                range.surroundContents(span);
                const newRange = document.createRange();
                newRange.selectNodeContents(span);
                selection.removeAllRanges();
                selection.addRange(newRange);
                savedRange = newRange.cloneRange();
              } catch (error) {
                document.execCommand("styleWithCSS", false, true);
                document.execCommand("fontSize", false, "7");
                const fonts = (getActiveEditableRoot() || bodyEditor).querySelectorAll('font[size="7"]');
                fonts.forEach((node) => {
                  node.removeAttribute("size");
                  node.style.fontSize = normalized;
                  node.style.lineHeight = "inherit";
                  node.style.verticalAlign = "baseline";
                  node.dataset.inlineFontSize = "1";
                });
              }
              syncFontSizeControls(normalized);
            }

            function getInlineFontWrapper(node) {
              if (!node) {
                return null;
              }
              const element = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
              return element ? element.closest('[data-inline-font-size="1"]') : null;
            }

            function insertPendingSizedText(text) {
              const selection = window.getSelection();
              if (!selection.rangeCount || !text) {
                return false;
              }

              const range = selection.getRangeAt(0);
              if (!range.collapsed) {
                return false;
              }

              const root = getActiveEditableRoot();
              if (root !== bodyEditor) {
                return false;
              }

              const currentFontSize = normalizeFontSizeValue(getCurrentFontSize()) + "px";
              if (!pendingFontSize || currentFontSize === pendingFontSize) {
                return false;
              }

              const wrapper = getInlineFontWrapper(range.startContainer);
              if (wrapper && wrapper.style.fontSize === pendingFontSize) {
                return false;
              }

              range.deleteContents();
              const span = document.createElement("span");
              span.style.fontSize = pendingFontSize;
              span.style.lineHeight = "inherit";
              span.style.verticalAlign = "baseline";
              span.dataset.inlineFontSize = "1";
              span.textContent = text;
              range.insertNode(span);

              const nextRange = document.createRange();
              nextRange.setStartAfter(span);
              nextRange.collapse(true);
              selection.removeAllRanges();
              selection.addRange(nextRange);
              savedRange = nextRange.cloneRange();
              return true;
            }

            function hideFloatingMenus() {
              Object.values(floatingMenus).forEach((menu) => {
                menu.classList.remove("is-visible");
              });
              toolbarButtons.forEach((button) => {
                button.classList.remove("is-open");
              });
              selectionToolbarWrap.classList.remove("has-open-menu");
              activeMenuKey = null;
            }

            function toggleFloatingMenu(button) {
              const menuKey = button.dataset.menu;
              const menu = floatingMenus[menuKey];
              if (!menu) {
                return;
              }

              const alreadyVisible = menu.classList.contains("is-visible");
              hideFloatingMenus();

              if (alreadyVisible) {
                updateActiveToolbarButtons();
                return;
              }

              const buttonRect = button.getBoundingClientRect();
              menu.style.left = Math.max(12, buttonRect.left) + "px";
              menu.style.top = buttonRect.bottom + 8 + "px";
              menu.classList.add("is-visible");
              button.classList.add("is-open", "is-active");
              selectionToolbarWrap.classList.add("has-open-menu");
              activeMenuKey = menuKey;

              if (menuKey === "font-size") {
                syncFontSizeControls(getCurrentFontSize());
              }

              if (menuKey === "link") {
                populateLinkMenu();
              }
            }

            function showTooltip(text) {
              tooltip.textContent = text || "Tooltip Text";
              tooltip.classList.add("is-visible");
              window.clearTimeout(tooltipTimer);
              tooltipTimer = window.setTimeout(() => {
                tooltip.classList.remove("is-visible");
              }, 1100);
            }

            function hideTooltip() {
              window.clearTimeout(tooltipTimer);
              tooltip.classList.remove("is-visible");
            }

            function getCurrentBlock() {
              const selection = window.getSelection();
              if (!selection.rangeCount) {
                return null;
              }
              let node = selection.anchorNode;
              while (node && node !== bodyEditor) {
                if (node.nodeType === Node.ELEMENT_NODE && /^(P|H1|H2|H3|LI|BLOCKQUOTE|PRE)$/i.test(node.tagName)) {
                  return node;
                }
                node = node.parentNode;
              }
              return null;
            }

            function getBlockText(block) {
              return block ? block.textContent.replace(/\\u200B/g, "").trim() : "";
            }

            function isEditableBlock(node) {
              return Boolean(
                node &&
                node.nodeType === Node.ELEMENT_NODE &&
                /^(P|H1|H2|H3|LI|BLOCKQUOTE|PRE)$/i.test(node.tagName) &&
                !node.classList.contains("body-placeholder")
              );
            }

            function findEditableBlock(startNode) {
              let node = startNode;
              while (node && node !== bodyEditor) {
                if (isEditableBlock(node)) {
                  return node;
                }
                node = node.parentNode;
              }
              return null;
            }

            function hideBlockHandle() {
              if (isHandleHovered) {
                return;
              }
              hoveredBlock = null;
              blockHandle.classList.remove("is-visible");
            }

            function showBlockHandle(block) {
              if (!block || !bodyEditor.contains(block)) {
                hideBlockHandle();
                return;
              }
              hoveredBlock = block;
              const blockRect = block.getBoundingClientRect();
              const canvasRect = editorCanvas.getBoundingClientRect();
              blockHandle.style.left = blockRect.left - canvasRect.left + editorCanvas.scrollLeft - 22 + "px";
              blockHandle.style.top = blockRect.top - canvasRect.top + editorCanvas.scrollTop + 2 + "px";
              blockHandle.classList.add("is-visible");
            }

            function getSelectionBlock() {
              const selection = window.getSelection();
              if (!selection.rangeCount) {
                return null;
              }
              const range = selection.getRangeAt(0);
              if (!bodyEditor.contains(range.commonAncestorContainer)) {
                return null;
              }
              return findEditableBlock(selection.anchorNode || range.commonAncestorContainer);
            }

            function updateBlockHandleFromSelection() {
              const block = getSelectionBlock();
              if (block) {
                showBlockHandle(block);
              } else if (!isHandleHovered) {
                hideBlockHandle();
              }
            }

            function selectWholeBlock(block) {
              if (!block) {
                return;
              }
              const selection = window.getSelection();
              const range = document.createRange();
              range.selectNodeContents(block);
              selection.removeAllRanges();
              selection.addRange(range);
              saveCurrentRange();
              updateActiveToolbarButtons();
              updateSelectionToolbar();
            }

            function replaceBlockWithTag(block, tagName) {
              if (!block || !block.parentNode) {
                return null;
              }

              const nextBlock = document.createElement(tagName);
              nextBlock.innerHTML = "<br>";
              block.parentNode.replaceChild(nextBlock, block);
              return nextBlock;
            }

            function replaceBlockWithList(block, listTag) {
              if (!block || !block.parentNode) {
                return null;
              }

              const list = document.createElement(listTag);
              const item = document.createElement("li");
              item.innerHTML = "<br>";
              list.appendChild(item);
              block.parentNode.replaceChild(list, block);
              return item;
            }

            function applySlashItem(item) {
              const block = getCurrentBlock();
              if (!block) {
                hideSlashMenu();
                return;
              }

              if (item.kind === "stub") {
                hideSlashMenu();
                showTooltip(item.label);
                return;
              }

              let targetNode = block;

              if (item.kind === "block") {
                targetNode = replaceBlockWithTag(block, item.value);
              } else if (item.kind === "list") {
                targetNode = replaceBlockWithList(block, item.value);
              }

              if (!targetNode) {
                hideSlashMenu();
                return;
              }

              if (pendingFontSize) {
                targetNode.style.fontSize = pendingFontSize;
              }

              hideSlashMenu();
              placeCaretAtEnd(targetNode);
              saveCurrentRange();
              renderOutline();
              updateActiveToolbarButtons();
              updateSelectionToolbar();
              showTooltip(item.label);
            }

            function renderSlashMenu(items) {
              slashMenu.innerHTML = items.map((item, index) => `
                <div class="slash-item" data-index="${index}">
                  <span class="slash-item__icon">${item.icon}</span>
                  <span>${item.label}</span>
                </div>
              `).join("");
              slashMenu.dataset.items = JSON.stringify(items);
            }

            function hideSlashMenu() {
              slashMenu.classList.remove("is-visible");
            }

            function updateSlashMenu() {
              const block = getCurrentBlock();
              if (!block || !bodyEditor.contains(block)) {
                hideSlashMenu();
                return;
              }

              const text = getBlockText(block);
              if (!text.startsWith("/")) {
                hideSlashMenu();
                return;
              }

              const query = text.slice(1).toLowerCase();
              const filtered = slashItems.filter((item) => {
                if (!query) {
                  return true;
                }
                return item.label.toLowerCase().includes(query) || item.queries.some((value) => value.includes(query));
              });

              if (!filtered.length) {
                hideSlashMenu();
                return;
              }

              renderSlashMenu(filtered);

              const blockRect = block.getBoundingClientRect();
              const canvasRect = editorCanvas.getBoundingClientRect();
              slashMenu.style.left = Math.max(20, blockRect.left - canvasRect.left + editorCanvas.scrollLeft) + "px";
              slashMenu.style.top = blockRect.bottom - canvasRect.top + editorCanvas.scrollTop + 10 + "px";
              slashMenu.classList.add("is-visible");
            }

            function updateSelectionToolbar() {
              if (selectedImageBlock) {
                selectionToolbarWrap.classList.remove("is-visible");
                return;
              }
              const selection = window.getSelection();
              if (!selection.rangeCount || selection.isCollapsed) {
                selectionToolbarWrap.classList.remove("is-visible");
                return;
              }

              const range = selection.getRangeAt(0);
              if (!bodyEditor.contains(range.commonAncestorContainer)) {
                selectionToolbarWrap.classList.remove("is-visible");
                return;
              }

              const selectedText = selection.toString().trim();
              if (!selectedText) {
                selectionToolbarWrap.classList.remove("is-visible");
                return;
              }

              const rects = Array.from(range.getClientRects()).filter((rect) => rect.width || rect.height);
              const targetRect = rects[0] || range.getBoundingClientRect();
              if (!targetRect) {
                selectionToolbarWrap.classList.remove("is-visible");
                return;
              }

              selectionToolbarWrap.classList.add("is-visible");
              const canvasRect = editorCanvas.getBoundingClientRect();
              const left = targetRect.left - canvasRect.left + editorCanvas.scrollLeft + targetRect.width / 2;
              const top = targetRect.top - canvasRect.top + editorCanvas.scrollTop - 48;
              const width = selectionToolbar.offsetWidth || 184;

              selectionToolbarWrap.style.left = Math.max(16, left - width / 2) + "px";
              selectionToolbarWrap.style.top = Math.max(16, top) + "px";
            }

            function execFormatting(button) {
              const command = button.dataset.command;
              const block = button.dataset.block;
              const menu = button.dataset.menu;
              const upload = button.dataset.upload;

              if (menu) {
                toggleFloatingMenu(button);
                return;
              }

              if (upload) {
                openUploadModal(upload);
                return;
              }

              if (selectedImageBlock) {
                if (command === "justifyLeft") {
                  setImageAlignment(selectedImageBlock, "left");
                  updateActiveToolbarButtons();
                  showTooltip(button.dataset.tip);
                } else if (command === "justifyCenter") {
                  setImageAlignment(selectedImageBlock, "center");
                  updateActiveToolbarButtons();
                  showTooltip(button.dataset.tip);
                } else if (command === "justifyRight") {
                  setImageAlignment(selectedImageBlock, "right");
                  updateActiveToolbarButtons();
                  showTooltip(button.dataset.tip);
                }
                return;
              }

              if (!command && !block) {
                showTooltip(button.dataset.tip);
                return;
              }

              const activeRoot = getActiveEditableRoot();
              activeRoot.focus();
              restoreSavedRange();

              if (command) {
                document.execCommand(command, false);
              } else if (block) {
                applyBlockFormat(block);
              }

              saveCurrentRange();
              updateActiveToolbarButtons();
              updateSelectionToolbar();
              updateSlashMenu();
              hideFloatingMenus();
              showTooltip(button.dataset.tip);
            }

            toolbarButtons.forEach((button) => {
              button.addEventListener("mouseenter", () => {
                if (button.dataset.tip) {
                  showTooltip(button.dataset.tip);
                }
              });

              button.addEventListener("mouseleave", hideTooltip);
              button.addEventListener("mousedown", (event) => {
                event.preventDefault();
                event.stopPropagation();
                saveCurrentRange();
                if (button.dataset.menu) {
                  toggleFloatingMenu(button);
                }
              });
              button.addEventListener("click", (event) => {
                if (button.dataset.menu) {
                  event.preventDefault();
                  event.stopPropagation();
                  return;
                }
                execFormatting(button);
              });
            });

            floatingMenuItems.forEach((item) => {
              item.addEventListener("mousedown", (event) => event.preventDefault());
              item.addEventListener("click", () => {
                const activeRoot = getActiveEditableRoot();
                activeRoot.focus();
                restoreSavedRange();

                if (item.dataset.command) {
                  document.execCommand(item.dataset.command, false);
                } else if (item.dataset.fontSize) {
                  applyFontSize(item.dataset.fontSize);
                } else if (item.dataset.block) {
                  applyBlockFormat(item.dataset.block);
                }

                saveCurrentRange();
                hideFloatingMenus();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
                showTooltip(item.dataset.tip);
              });
            });

            Object.values(floatingMenus).forEach((menu) => {
              if (!menu) {
                return;
              }
              menu.addEventListener("mousedown", (event) => event.stopPropagation());
              menu.addEventListener("click", (event) => event.stopPropagation());
            });

            if (fontSizeRange) {
              fontSizeRange.addEventListener("mousedown", (event) => event.stopPropagation());
              fontSizeRange.addEventListener("click", (event) => event.stopPropagation());
              fontSizeRange.addEventListener("input", () => {
                syncFontSizeControls(fontSizeRange.value);
                const activeRoot = getActiveEditableRoot();
                activeRoot.focus();
                restoreSavedRange();
                applyFontSize(fontSizeRange.value);
                saveCurrentRange();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
              });

              fontSizeRange.addEventListener("change", () => {
                const activeRoot = getActiveEditableRoot();
                activeRoot.focus();
                restoreSavedRange();
                applyFontSize(fontSizeRange.value);
                saveCurrentRange();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
              });
            }

            if (fontSizeInput) {
              fontSizeInput.addEventListener("mousedown", (event) => event.stopPropagation());
              fontSizeInput.addEventListener("click", (event) => event.stopPropagation());
              fontSizeInput.addEventListener("input", () => {
                syncFontSizeControls(fontSizeInput.value);
              });

              fontSizeInput.addEventListener("change", () => {
                const activeRoot = getActiveEditableRoot();
                activeRoot.focus();
                restoreSavedRange();
                applyFontSize(fontSizeInput.value);
                saveCurrentRange();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
              });
            }

            if (linkTextInput) {
              linkTextInput.addEventListener("mousedown", (event) => event.stopPropagation());
              linkTextInput.addEventListener("click", (event) => event.stopPropagation());
              linkTextInput.addEventListener("input", updateLinkConfirmState);
            }

            if (linkTargetInput) {
              linkTargetInput.addEventListener("mousedown", (event) => event.stopPropagation());
              linkTargetInput.addEventListener("click", (event) => event.stopPropagation());
              linkTargetInput.addEventListener("input", () => {
                pendingLinkTarget = linkTargetInput.value;
                updateLinkConfirmState();
              });
            }

            if (linkOpenInNewTab) {
              linkOpenInNewTab.addEventListener("mousedown", (event) => event.stopPropagation());
              linkOpenInNewTab.addEventListener("click", (event) => event.stopPropagation());
            }

            if (linkHeadingList) {
              linkHeadingList.addEventListener("mousedown", (event) => event.stopPropagation());
              linkHeadingList.addEventListener("click", (event) => {
                event.stopPropagation();
                const option = event.target.closest("[data-heading-target]");
                if (!option || !linkTargetInput) {
                  return;
                }
                const target = option.dataset.headingTarget || "";
                linkTargetInput.value = target;
                pendingLinkTarget = target;
                updateLinkConfirmState();
              });
            }

            if (linkConfirmButton) {
              linkConfirmButton.addEventListener("mousedown", (event) => event.stopPropagation());
              linkConfirmButton.addEventListener("click", (event) => {
                event.stopPropagation();
                applyLink();
              });
            }

            if (linkCancelButton) {
              linkCancelButton.addEventListener("mousedown", (event) => event.stopPropagation());
              linkCancelButton.addEventListener("click", (event) => {
                event.stopPropagation();
                hideFloatingMenus();
                updateActiveToolbarButtons();
              });
            }

            if (outlineList) {
              outlineList.addEventListener("click", (event) => {
                const item = event.target.closest("[data-outline-target]");
                if (!item) {
                  return;
                }
                const target = document.getElementById(item.dataset.outlineTarget || "");
                if (!target) {
                  return;
                }
                target.scrollIntoView({ behavior: "smooth", block: "center" });
                if (target === titleEditor) {
                  titleEditor.focus();
                } else {
                  bodyEditor.focus();
                }
              });
            }

            if (uploadBrowseButton && uploadModalInput) {
              uploadBrowseButton.addEventListener("click", (event) => {
                event.preventDefault();
                uploadModalInput.click();
              });
            }

            if (uploadModalInput) {
              uploadModalInput.addEventListener("change", () => {
                const [file] = Array.from(uploadModalInput.files || []);
                handleUploadFile(file);
              });
            }

            if (uploadDropzone) {
              uploadDropzone.addEventListener("dragover", (event) => {
                event.preventDefault();
                uploadDropzone.classList.add("is-dragover");
              });
              uploadDropzone.addEventListener("dragleave", () => {
                uploadDropzone.classList.remove("is-dragover");
              });
              uploadDropzone.addEventListener("drop", (event) => {
                event.preventDefault();
                uploadDropzone.classList.remove("is-dragover");
                const [file] = Array.from(event.dataTransfer?.files || []);
                handleUploadFile(file);
              });
            }

            if (uploadPreview) {
              uploadPreview.addEventListener("click", (event) => {
                const removeButton = event.target.closest("#uploadRemoveButton");
                if (removeButton) {
                  resetUploadState();
                  renderUploadModal();
                  return;
                }
                const retryButton = event.target.closest("#uploadRetryButton");
                if (retryButton && uploadState && uploadState.file) {
                  handleUploadFile(uploadState.file);
                }
              });
            }

            if (uploadCancelButton) {
              uploadCancelButton.addEventListener("click", closeUploadModal);
            }

            if (uploadModalClose) {
              uploadModalClose.addEventListener("click", closeUploadModal);
            }

            if (uploadModal) {
              uploadModal.addEventListener("click", (event) => {
                if (event.target.closest("[data-upload-close='1']")) {
                  closeUploadModal();
                }
              });
            }

            if (uploadConfirmButton) {
              uploadConfirmButton.addEventListener("click", () => {
                confirmUpload();
              });
            }

            bodyEditor.addEventListener("focus", clearPlaceholderIfNeeded);
            bodyEditor.addEventListener("paste", async (event) => {
              const clipboard = event.clipboardData;
              if (!clipboard) {
                return;
              }

              const imageItem = Array.from(clipboard.items || []).find((item) => {
                return item.kind === "file" && String(item.type || "").toLowerCase().startsWith("image/");
              });

              if (!imageItem) {
                return;
              }

              const file = imageItem.getAsFile();
              if (!file) {
                return;
              }

              event.preventDefault();
              try {
                await insertImageFile(file);
              } catch (error) {
                showTooltip("Ошибка вставки");
              }
            });
            bodyEditor.addEventListener("dragstart", (event) => {
              if (event.target.closest(".embedded-image-block")) {
                event.preventDefault();
              }
            });
            bodyEditor.addEventListener("pointerdown", (event) => {
              const resizeHandle = event.target.closest("[data-image-resize]");
              if (resizeHandle) {
                startImageResize(resizeHandle.closest(".embedded-image-block"), resizeHandle.dataset.imageResize || "", event);
                return;
              }

              const imageBlock = event.target.closest(".embedded-image-block");
              if (imageBlock) {
                startImageMove(imageBlock, event);
                return;
              }

              if (selectedImageBlock) {
                clearSelectedImageBlock();
              }
            });
            bodyEditor.addEventListener("click", (event) => {
              const imageBlock = event.target.closest(".embedded-image-block");
              if (imageBlock) {
                event.preventDefault();
                event.stopPropagation();
                selectImageBlock(imageBlock);
              }
            });
            bodyEditor.addEventListener("beforeinput", (event) => {
              if (
                event.inputType === "insertText" &&
                event.data &&
                insertPendingSizedText(event.data)
              ) {
                event.preventDefault();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
              }
            });
            bodyEditor.addEventListener("blur", () => {
              window.setTimeout(() => {
                restorePlaceholderIfEmpty();
                hideSlashMenu();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
              }, 0);
            });

            bodyEditor.addEventListener("keydown", (event) => {
              if (uploadModal && uploadModal.classList.contains("is-visible") && event.key === "Escape") {
                event.preventDefault();
                closeUploadModal();
                return;
              }

              if (selectedImageBlock && (event.key === "Backspace" || event.key === "Delete")) {
                event.preventDefault();
                removeSelectedImageBlock();
                return;
              }

              if (hasPlaceholder() && event.key.length === 1) {
                clearPlaceholderIfNeeded();
              }

              if (event.key === "Enter") {
                event.preventDefault();
                document.execCommand("insertParagraph", false);
                window.requestAnimationFrame(() => {
                  updateActiveToolbarButtons();
                  updateSlashMenu();
                  updateSelectionToolbar();
                });
              }

              if (event.key === "Escape") {
                hideSlashMenu();
                selectionToolbarWrap.classList.remove("is-visible");
                hideFloatingMenus();
              }
            });

            bodyEditor.addEventListener("input", () => {
              renderOutline();
              updateActiveToolbarButtons();
              updateSlashMenu();
              updateSelectionToolbar();
              updateBlockHandleFromSelection();
            });

            bodyEditor.addEventListener("keyup", () => {
              saveCurrentRange();
              updateActiveToolbarButtons();
              updateSlashMenu();
              updateSelectionToolbar();
              updateBlockHandleFromSelection();
            });

            editorCanvas.addEventListener("scroll", () => {
              updateActiveToolbarButtons();
              updateSelectionToolbar();
              updateSlashMenu();
              if (hoveredBlock) {
                showBlockHandle(hoveredBlock);
              }
            });

            document.addEventListener("selectionchange", () => {
              saveCurrentRange();
              const selection = window.getSelection();
              if (selectedImageBlock && selection && selection.rangeCount && !selection.isCollapsed) {
                clearSelectedImageBlock();
              }
              if (activeMenuKey === "font-size") {
                syncFontSizeControls(getCurrentFontSize());
              }
              if (activeMenuKey === "link") {
                populateLinkMenu();
              }
              updateActiveToolbarButtons();
              updateSelectionToolbar();
              updateBlockHandleFromSelection();
            });

            document.addEventListener("keydown", (event) => {
              if (uploadModal && uploadModal.classList.contains("is-visible") && event.key === "Escape") {
                event.preventDefault();
                closeUploadModal();
                return;
              }

              if (selectedImageBlock && (event.key === "Backspace" || event.key === "Delete")) {
                event.preventDefault();
                removeSelectedImageBlock();
                return;
              }

              if (event.key !== "Control") {
                return;
              }
              ctrlPressed = true;
              if (hoveredLink) {
                hoveredLink.classList.add("is-ctrl-ready");
              }
              if (!event.repeat && hoveredLink) {
                navigateToLink(hoveredLink);
              }
            });

            document.addEventListener("keyup", (event) => {
              if (event.key !== "Control") {
                return;
              }
              ctrlPressed = false;
              if (hoveredLink) {
                hoveredLink.classList.remove("is-ctrl-ready");
              }
            });

            document.addEventListener("click", (event) => {
              if (!slashMenu.contains(event.target) && event.target !== bodyEditor) {
                const block = getCurrentBlock();
                if (!block || !getBlockText(block).startsWith("/")) {
                  hideSlashMenu();
                }
              }

              const clickedMenuTrigger = event.target.closest('[data-menu]');
              const clickedFloatingMenu = event.target.closest('.floating-menu');
              if (!clickedMenuTrigger && !clickedFloatingMenu && !selectionToolbarWrap.contains(event.target)) {
                hideFloatingMenus();
                updateActiveToolbarButtons();
              }

              if (
                selectedImageBlock &&
                !event.target.closest(".embedded-image-block")
              ) {
                clearSelectedImageBlock();
              }
            });

            function handleCtrlLinkClick(event) {
              const link = event.target.closest("a");
              if (!link) {
                return;
              }
              if (!(event.ctrlKey || ctrlPressed)) {
                return;
              }
              event.preventDefault();
              event.stopPropagation();
              navigateToLink(link);
            }

            bodyEditor.addEventListener("click", handleCtrlLinkClick);
            titleEditor.addEventListener("click", handleCtrlLinkClick);

            bodyEditor.addEventListener("mousemove", (event) => {
              setHoveredLink(event.target.closest("a"));
              const imageBlock = event.target.closest(".embedded-image-block");
              if (imageBlock) {
                hideBlockHandle();
                return;
              }
              const block = findEditableBlock(event.target);
              if (block) {
                showBlockHandle(block);
              } else if (!isHandleHovered) {
                hideBlockHandle();
              }
            });

            bodyEditor.addEventListener("mouseleave", (event) => {
              if (!event.relatedTarget || !bodyEditor.contains(event.relatedTarget)) {
                clearHoveredLink();
              }
              if (event.relatedTarget === blockHandle || blockHandle.contains(event.relatedTarget)) {
                return;
              }
              updateBlockHandleFromSelection();
            });

            titleEditor.addEventListener("mousemove", (event) => {
              setHoveredLink(event.target.closest("a"));
            });

            titleEditor.addEventListener("mouseleave", () => {
              clearHoveredLink();
            });

            blockHandle.addEventListener("mouseenter", () => {
              isHandleHovered = true;
              if (hoveredBlock) {
                showBlockHandle(hoveredBlock);
              }
            });

            blockHandle.addEventListener("mouseleave", () => {
              isHandleHovered = false;
              updateBlockHandleFromSelection();
            });

            blockHandle.addEventListener("mousedown", (event) => {
              event.preventDefault();
              if (hoveredBlock) {
                bodyEditor.focus();
                selectWholeBlock(hoveredBlock);
              }
            });

            titleEditor.addEventListener("focus", updateActiveToolbarButtons);
            titleEditor.addEventListener("keyup", () => {
              saveCurrentRange();
              if (pendingFontSize) {
                titleEditor.style.fontSize = pendingFontSize;
              }
              renderOutline();
              updateActiveToolbarButtons();
              updateSelectionToolbar();
            });
            titleEditor.addEventListener("input", () => {
              renderOutline();
              updateActiveToolbarButtons();
            });

            slashMenu.addEventListener("mousedown", (event) => event.preventDefault());
            slashMenu.addEventListener("click", (event) => {
              const item = event.target.closest(".slash-item");
              if (!item) {
                return;
              }
              const items = JSON.parse(slashMenu.dataset.items || "[]");
              const selectedItem = items[Number(item.dataset.index)];
              if (!selectedItem) {
                hideSlashMenu();
                return;
              }
              applySlashItem(selectedItem);
            });

            setLoadingState();
            pinComponentFrame();
            window.addEventListener("resize", pinComponentFrame);
            window.addEventListener("blur", clearCursorState);
            window.setTimeout(() => {
              pinComponentFrame();
              showEditorState();
              window.setTimeout(() => {
                pinComponentFrame();
                renderOutline();
                titleEditor.focus();
                placeCaretAtEnd(titleEditor);
                updateActiveToolbarButtons();
              }, 120);
            }, 900);
          </script>
        </body>
        </html>
        """
    ).strip()

    html = html.replace("__LOADING_SCREEN__", loading_screen_markup())
    html = html.replace("__DOCUMENT_HEADER__", document_header_markup())
    html = html.replace("__TOOLBAR__", _toolbar_markup())
    html = html.replace("__SELECTION_TOOLBAR__", _selection_toolbar_markup())
    html = html.replace("__EMPTY_HINT__", _EMPTY_HINT)
    html = html.replace("__CURSOR_ROOT_VARIABLES__", cursor_root_variables("              "))

    components.html(html, height=780, scrolling=False)
