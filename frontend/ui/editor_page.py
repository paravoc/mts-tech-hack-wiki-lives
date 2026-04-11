from __future__ import annotations

from textwrap import dedent

import streamlit.components.v1 as components

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
            <button class="toolbar-button" data-tip="Вставить объект">@</button>
            <button class="toolbar-button" data-tip="Ссылка">&lt;/&gt;</button>
            <button class="toolbar-button" data-tip="Цитата" data-block="blockquote">``</button>
            <button class="toolbar-button" data-tip="Изображение">&#9633;</button>
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
              <button class="toolbar-button" data-tip="Вставить объект">@</button>
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

          <div class="floating-menu" id="floatingMenuAlignment" data-menu-panel="alignment">
            <button class="floating-menu__item" data-tip="Выровнять влево" data-command="justifyLeft">По левому краю</button>
            <button class="floating-menu__item" data-tip="Выровнять по центру" data-command="justifyCenter">По центру</button>
            <button class="floating-menu__item" data-tip="Выровнять вправо" data-command="justifyRight">По правому краю</button>
          </div>

          <div class="floating-menu" id="floatingMenuList" data-menu-panel="list">
            <button class="floating-menu__item" data-tip="Маркированный список" data-command="insertUnorderedList">Маркированный список</button>
            <button class="floating-menu__item" data-tip="Нумерованный список" data-command="insertOrderedList">Нумерованный список</button>
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

            button,
            input,
            textarea {
              font: inherit;
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
              position: relative;
              flex: 1;
              overflow: auto;
              background: #ffffff;
            }

            .editor-shell {
              width: 644px;
              max-width: calc(100vw - 80px);
              margin: 0 auto;
              padding: 54px 0 180px;
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

            .selection-toolbar-wrap.is-visible {
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
              position: absolute;
              top: 34px;
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
              __DOCUMENT_HEADER__
              __TOOLBAR__
              <div class="editor-canvas" id="editorCanvas">
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
          </div>

          <script>
            const loadingScreen = document.getElementById("loadingScreen");
            const editorScreen = document.getElementById("editorScreen");
            const editorCanvas = document.getElementById("editorCanvas");
            const bodyEditor = document.getElementById("bodyEditor");
            const titleEditor = document.getElementById("titleEditor");
            const slashMenu = document.getElementById("slashMenu");
            const tooltip = document.getElementById("tooltip");
            const selectionToolbar = document.getElementById("selectionToolbar");
            const selectionToolbarWrap = document.querySelector(".selection-toolbar-wrap");
            const blockHandle = document.getElementById("blockHandle");
            const toolbarButtons = Array.from(document.querySelectorAll(".toolbar-button"));
            const floatingMenuItems = Array.from(document.querySelectorAll(".floating-menu__item"));
            const floatingMenus = {
              "text-style": document.getElementById("floatingMenuTextStyle"),
              "alignment": document.getElementById("floatingMenuAlignment"),
              "list": document.getElementById("floatingMenuList")
            };
            const emptyHint = "__EMPTY_HINT__";
            let savedRange = null;
            let tooltipTimer = null;
            let hoveredBlock = null;
            let isHandleHovered = false;

            const slashItems = [
              { icon: "T", label: "Обычный текст", queries: ["текст", "text"] },
              { icon: "H1", label: "Заголовок 1", queries: ["загол", "заголовок", "h1"] },
              { icon: "H2", label: "Заголовок 2", queries: ["загол", "заголовок", "h2"] },
              { icon: "H3", label: "Заголовок 3", queries: ["загол", "заголовок", "h3"] },
              { icon: "•", label: "Маркированный список", queries: ["список", "марк"] },
              { icon: "1", label: "Нумерованный список", queries: ["список", "номер"] },
              { icon: "✓", label: "Чеклист", queries: ["чек", "todo"] },
              { icon: "</>", label: "Код", queries: ["код"] },
              { icon: "``", label: "Цитата", queries: ["цитата"] },
              { icon: "▣", label: "Изображение", queries: ["изображение", "фото"] }
            ];

            function setLoadingState() {
              loadingScreen.classList.remove("is-hidden");
              editorScreen.classList.add("is-hidden");
            }

            function showEditorState() {
              loadingScreen.classList.add("is-hidden");
              editorScreen.classList.remove("is-hidden");
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

                if (activeGroup === "list" && (safeQueryCommandState("insertOrderedList") || safeQueryCommandState("insertUnorderedList"))) {
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

            function applyBlockFormat(block) {
              const currentBlockTag = getCurrentBlockTag();
              const nextBlock = currentBlockTag === block.toLowerCase() ? "p" : block;
              document.execCommand("formatBlock", false, nextBlock);
            }

            function hideFloatingMenus() {
              Object.values(floatingMenus).forEach((menu) => {
                menu.classList.remove("is-visible");
              });
              toolbarButtons.forEach((button) => {
                button.classList.remove("is-open");
              });
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

              const wrapRect = selectionToolbarWrap.getBoundingClientRect();
              const buttonRect = button.getBoundingClientRect();
              menu.style.left = buttonRect.left - wrapRect.left + "px";
              menu.style.top = selectionToolbar.offsetHeight + 8 + "px";
              menu.classList.add("is-visible");
              button.classList.add("is-open", "is-active");
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

            function renderSlashMenu(items) {
              slashMenu.innerHTML = items.map((item) => `
                <div class="slash-item" data-label="${item.label}">
                  <span class="slash-item__icon">${item.icon}</span>
                  <span>${item.label}</span>
                </div>
              `).join("");
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
              const selection = window.getSelection();
              if (!selection.rangeCount || selection.isCollapsed) {
                selectionToolbarWrap.classList.remove("is-visible");
                hideFloatingMenus();
                return;
              }

              const range = selection.getRangeAt(0);
              if (!bodyEditor.contains(range.commonAncestorContainer)) {
                selectionToolbarWrap.classList.remove("is-visible");
                hideFloatingMenus();
                return;
              }

              const selectedText = selection.toString().trim();
              if (!selectedText) {
                selectionToolbarWrap.classList.remove("is-visible");
                hideFloatingMenus();
                return;
              }

              const rects = Array.from(range.getClientRects()).filter((rect) => rect.width || rect.height);
              const targetRect = rects[0] || range.getBoundingClientRect();
              if (!targetRect) {
                selectionToolbarWrap.classList.remove("is-visible");
                hideFloatingMenus();
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

              if (menu) {
                toggleFloatingMenu(button);
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
              button.addEventListener("mousedown", (event) => event.preventDefault());
              button.addEventListener("click", () => execFormatting(button));
            });

            floatingMenuItems.forEach((item) => {
              item.addEventListener("mousedown", (event) => event.preventDefault());
              item.addEventListener("click", () => {
                const activeRoot = getActiveEditableRoot();
                activeRoot.focus();
                restoreSavedRange();

                if (item.dataset.command) {
                  document.execCommand(item.dataset.command, false);
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

            bodyEditor.addEventListener("focus", clearPlaceholderIfNeeded);
            bodyEditor.addEventListener("blur", () => {
              window.setTimeout(() => {
                restorePlaceholderIfEmpty();
                hideSlashMenu();
                updateActiveToolbarButtons();
                updateSelectionToolbar();
              }, 0);
            });

            bodyEditor.addEventListener("keydown", (event) => {
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
              updateActiveToolbarButtons();
              updateSelectionToolbar();
              updateBlockHandleFromSelection();
            });

            document.addEventListener("click", (event) => {
              if (!slashMenu.contains(event.target) && event.target !== bodyEditor) {
                const block = getCurrentBlock();
                if (!block || !getBlockText(block).startsWith("/")) {
                  hideSlashMenu();
                }
              }

              if (!selectionToolbarWrap.contains(event.target)) {
                hideFloatingMenus();
                updateActiveToolbarButtons();
              }
            });

            bodyEditor.addEventListener("mousemove", (event) => {
              const block = findEditableBlock(event.target);
              if (block) {
                showBlockHandle(block);
              } else if (!isHandleHovered) {
                hideBlockHandle();
              }
            });

            bodyEditor.addEventListener("mouseleave", (event) => {
              if (event.relatedTarget === blockHandle || blockHandle.contains(event.relatedTarget)) {
                return;
              }
              updateBlockHandleFromSelection();
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
              updateActiveToolbarButtons();
              updateSelectionToolbar();
            });
            titleEditor.addEventListener("input", updateActiveToolbarButtons);

            slashMenu.addEventListener("mousedown", (event) => event.preventDefault());
            slashMenu.addEventListener("click", (event) => {
              const item = event.target.closest(".slash-item");
              if (!item) {
                return;
              }
              const label = item.dataset.label;
              hideSlashMenu();
              showTooltip(label);
            });

            setLoadingState();
            window.setTimeout(() => {
              showEditorState();
              window.setTimeout(() => {
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

    components.html(html, height=920, scrolling=False)
