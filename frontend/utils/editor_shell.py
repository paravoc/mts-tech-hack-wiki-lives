from __future__ import annotations

import json
from typing import Any

import streamlit.components.v1 as components


PAGE_BREAK_MARKER = "[[WL_PAGE_BREAK]]"


def render_editor_shell(
    insert_lookup: dict[str, dict[str, Any]],
    draft_key: str,
    active_snippet: str,
    active_hint: str,
    page_id: str | None,
    backend_url: str,
) -> None:
    html = r"""
        <style>
        html, body { margin: 0; padding: 0; background: transparent; color: #111827; font-family: 'Manrope', sans-serif; }
        .wikilive-rich-root { position: relative; min-height: 82vh; padding: 0.2rem 0 2rem; }
        .wl-workbench {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 320px;
            gap: 1rem;
            align-items: start;
        }
        .wl-toolbar {
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 0.55rem;
            padding: 0.2rem 0 0.95rem;
            background: linear-gradient(180deg, rgba(246,247,249,.98), rgba(246,247,249,.92), rgba(246,247,249,0));
            backdrop-filter: blur(10px);
        }
        .wl-toolbar__group { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem; }
        .wl-toolbar__sep { width: 1px; height: 1.85rem; background: rgba(17,24,39,.10); margin: 0 0.1rem; }
        .wl-toolbar button, .wl-toolbar select, .wl-toolbar input[type="range"] {
            position: relative;
            min-height: 2.2rem;
            border-radius: 12px;
            border: 1px solid rgba(227,6,19,.18);
            background: rgba(255,255,255,.98);
            color: #111827;
            box-shadow: 0 1px 2px rgba(17,24,39,.04);
            transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
        }
        .wl-toolbar button, .wl-toolbar select {
            padding: 0.46rem 0.72rem;
            font: 700 .84rem/1.1 Manrope, sans-serif;
        }
        .wl-toolbar button:hover, .wl-toolbar select:hover {
            transform: translateY(-1px);
            border-color: rgba(227,6,19,.42);
            box-shadow: 0 10px 20px rgba(17,24,39,.06);
        }
        .wl-toolbar button.is-active {
            background: rgba(227,6,19,.08);
            color: #bf0812;
            border-color: rgba(227,6,19,.48);
        }
        .wl-toolbar button:disabled {
            opacity: .42;
            cursor: default;
            box-shadow: none;
            transform: none;
        }
        .wl-toolbar__icon { width: 2.45rem; padding: 0; justify-content: center; }
        .wl-toolbar__symbol { min-width: 2.75rem; font-weight: 800; }
        .wl-toolbar [data-tip]:hover::after {
            content: attr(data-tip);
            position: absolute;
            left: 50%;
            top: calc(100% + 9px);
            transform: translateX(-50%);
            min-width: 8rem;
            padding: 0.5rem 0.65rem;
            border-radius: 12px;
            background: rgba(17,24,39,.94);
            color: #f9fafb;
            white-space: pre-line;
            text-align: center;
            font: 600 .74rem/1.35 Manrope, sans-serif;
            box-shadow: 0 12px 28px rgba(17,24,39,.18);
            pointer-events: none;
            z-index: 200;
        }
        #wl-image-width, #wl-image-opacity {
            width: 8rem;
            display: none;
            accent-color: #e30613;
        }
        .wl-canvas {
            max-width: 920px;
            margin: 0 auto;
            padding: 0 1.2rem 4rem;
        }
        .wl-editor {
            min-height: 78vh;
            outline: none;
            color: #111827;
            caret-color: #e30613;
            font: 500 17px/1.9 Manrope, sans-serif;
            word-break: break-word;
        }
        .wl-editor:empty::before {
            content: attr(data-placeholder);
            color: #9ca3af;
        }
        .wl-line,
        .wl-table-block,
        .wl-code-block {
            position: relative;
            border-radius: 18px;
        }
        .wl-line {
            min-height: 1.92em;
            white-space: pre-wrap;
            padding: 0.08rem 0.8rem 0.12rem 0.9rem;
            margin: 0.08rem -0.25rem;
            transition: background .16s ease, box-shadow .16s ease;
        }
        .wl-line:hover {
            background: rgba(255,255,255,.72);
            box-shadow: 0 10px 22px rgba(17,24,39,.04);
        }
        .wl-line__body { min-height: 1.92em; }
        .wl-line.is-comment-target {
            background: rgba(227,6,19,.07);
            box-shadow: 0 14px 24px rgba(227,6,19,.08);
        }
        .wl-line[data-kind="heading1"] {
            font: 800 2rem/1.22 'Onest', sans-serif;
            letter-spacing: -0.03em;
            margin: 0.22rem 0 0.34rem;
        }
        .wl-line[data-kind="heading2"] {
            font: 800 1.46rem/1.34 'Onest', sans-serif;
            letter-spacing: -0.02em;
            margin: 0.18rem 0 0.24rem;
        }
        .wl-line[data-kind="heading3"] {
            font: 700 1.12rem/1.55 'Onest', sans-serif;
            letter-spacing: -0.01em;
            margin: 0.12rem 0 0.12rem;
        }
        .wl-line[data-kind="callout"] {
            padding: 0.38rem 0.85rem;
            margin: 0.2rem 0;
            border-left: 3px solid #e30613;
            border-radius: 0 14px 14px 0;
            background: rgba(227,6,19,.05);
        }
        .wl-block-handle,
        .wl-block-comment {
            position: absolute;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            border: 1px solid rgba(17,24,39,.08);
            background: rgba(255,255,255,.96);
            color: #6b7280;
            box-shadow: 0 10px 24px rgba(17,24,39,.08);
            cursor: pointer;
            opacity: 0;
            transform: translateY(4px);
            transition: opacity .16s ease, transform .16s ease, border-color .16s ease, color .16s ease;
            z-index: 3;
        }
        .wl-block-handle:hover,
        .wl-block-comment:hover {
            color: #bf0812;
            border-color: rgba(227,6,19,.28);
        }
        .wl-line:hover .wl-block-handle,
        .wl-line:hover .wl-block-comment,
        .wl-line.has-comments .wl-block-comment,
        .wl-line.is-comment-target .wl-block-handle,
        .wl-line.is-comment-target .wl-block-comment {
            opacity: 1;
            transform: translateY(0);
        }
        .wl-block-handle {
            left: -2.15rem;
            top: 0.25rem;
            width: 1.7rem;
            height: 1.7rem;
            font: 800 .84rem/1 Manrope, sans-serif;
        }
        .wl-block-comment {
            right: -2.45rem;
            bottom: 0.18rem;
            min-width: 1.9rem;
            height: 1.9rem;
            padding: 0 0.45rem;
            gap: 0.28rem;
            font: 800 .76rem/1 Manrope, sans-serif;
        }
        .wl-block-comment__icon { font-size: .84rem; }
        .wl-block-comment__count { color: inherit; }
        .wl-inline-mark--underline { text-decoration: underline; }
        .wl-inline-mark--strike { text-decoration: line-through; color: #6b7280; }
        .wl-object, .wl-attachment {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            margin: 0 0.14rem;
            border: 1px solid rgba(17,24,39,.10);
            background: rgba(255,255,255,.98);
            box-shadow: 0 8px 20px rgba(17,24,39,.06);
            cursor: pointer;
            transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
            vertical-align: middle;
        }
        .wl-object:hover, .wl-object.is-selected, .wl-attachment:hover, .wl-attachment.is-selected {
            transform: translateY(-1px);
            border-color: rgba(227,6,19,.42);
            box-shadow: 0 14px 30px rgba(227,6,19,.10);
        }
        .wl-object { padding: 0.22rem 0.55rem; border-radius: 999px; }
        .wl-object__field { color: #bf0812; font-size: .74rem; font-weight: 800; }
        .wl-object__value { color: #4b5563; font-size: .8rem; max-width: 14rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .wl-attachment { border-radius: 18px; }
        .wl-attachment--image {
            flex-direction: column;
            align-items: stretch;
            padding: 0.46rem;
            width: fit-content;
            max-width: 520px;
        }
        .wl-attachment--image img {
            display: block;
            width: 100%;
            max-height: 360px;
            object-fit: cover;
            border-radius: 14px;
            background: #f3f4f6;
        }
        .wl-attachment__caption, .wl-attachment__meta {
            display: flex;
            align-items: center;
            gap: 0.48rem;
            flex-wrap: wrap;
            padding: 0 0.1rem;
        }
        .wl-attachment__name { color: #111827; font-size: .82rem; font-weight: 700; }
        .wl-attachment__type { color: #6b7280; font-size: .74rem; font-weight: 700; }
        .wl-attachment--file { padding: 0.45rem 0.7rem; border-radius: 999px; }
        .wl-attachment__dot { width: .5rem; height: .5rem; border-radius: 999px; background: #e30613; flex: none; }
        .wl-table-block {
            margin: 0.55rem 0 0.85rem;
            overflow: auto;
            border-radius: 18px;
            border: 1px solid rgba(17,24,39,.08);
            background: #ffffff;
        }
        .wl-table { width: 100%; border-collapse: collapse; font-size: .93rem; }
        .wl-table th, .wl-table td {
            padding: 0.68rem 0.76rem;
            border-bottom: 1px solid rgba(17,24,39,.06);
            text-align: left;
            vertical-align: top;
        }
        .wl-table th { background: rgba(243,244,246,.92); font-weight: 800; color: #374151; }
        .wl-table .wl-attachment--image { max-width: 220px; }
        .wl-code-block {
            margin: 0.55rem 0 0.85rem;
            padding: 0.85rem 0.95rem;
            border-radius: 18px;
            border: 1px solid rgba(17,24,39,.08);
            background: #111827;
            color: #f3f4f6;
            font: 500 .86rem/1.65 Consolas, 'Courier New', monospace;
            white-space: pre-wrap;
        }
        .wl-context-menu, .wl-slash-menu {
            position: fixed;
            z-index: 99999;
            display: none;
            min-width: 220px;
            padding: 8px;
            border-radius: 16px;
            border: 1px solid rgba(17,24,39,.08);
            background: rgba(255,255,255,.98);
            box-shadow: 0 18px 40px rgba(17,24,39,.14);
        }
        .wl-context-menu button, .wl-slash-menu button {
            width: 100%;
            border: 1px solid rgba(227,6,19,.22);
            background: #ffffff;
            color: #111827;
            border-radius: 12px;
            padding: 0.74rem 0.85rem;
            text-align: left;
            font: 800 .84rem/1.2 Manrope, sans-serif;
            cursor: pointer;
        }
        .wl-context-menu button + button, .wl-slash-menu button + button { margin-top: 0.35rem; }
        .wl-context-menu__hint {
            margin-top: 0.45rem;
            padding: 0 0.18rem;
            color: #6b7280;
            font: 600 .74rem/1.45 Manrope, sans-serif;
        }
        .wl-slash-menu__meta {
            display: block;
            margin-top: 0.16rem;
            color: #6b7280;
            font-size: .72rem;
            font-weight: 700;
        }
        .wl-outline {
            position: fixed;
            left: 0.5rem;
            top: 5.4rem;
            z-index: 45;
            width: 2.8rem;
            max-height: calc(100vh - 6rem);
            overflow: hidden;
            border-radius: 18px;
            border: 1px solid rgba(17,24,39,.08);
            background: rgba(255,255,255,.92);
            box-shadow: 0 16px 36px rgba(17,24,39,.08);
            transition: width .22s ease, box-shadow .22s ease;
            backdrop-filter: blur(10px);
        }
        .wl-outline:hover {
            width: 16rem;
            box-shadow: 0 22px 44px rgba(17,24,39,.12);
        }
        .wl-outline__handle {
            width: 2.8rem;
            height: 2.8rem;
            border: none;
            border-bottom: 1px solid rgba(17,24,39,.06);
            background: transparent;
            color: #e30613;
            font: 900 1rem/1 Manrope, sans-serif;
            cursor: pointer;
        }
        .wl-outline__panel {
            opacity: 0;
            pointer-events: none;
            max-height: calc(100vh - 8.8rem);
            overflow: auto;
            transition: opacity .16s ease;
        }
        .wl-outline:hover .wl-outline__panel {
            opacity: 1;
            pointer-events: auto;
        }
        .wl-outline__list {
            display: flex;
            flex-direction: column;
            gap: 0.18rem;
            padding: 0.55rem;
        }
        .wl-outline__item {
            width: 100%;
            padding: 0.52rem 0.62rem;
            border-radius: 12px;
            border: 1px solid transparent;
            background: transparent;
            color: #374151;
            text-align: left;
            font: 700 .79rem/1.35 Manrope, sans-serif;
            cursor: pointer;
            transition: background .16s ease, border-color .16s ease, transform .16s ease;
        }
        .wl-outline__item:hover {
            transform: translateY(-1px);
            background: rgba(227,6,19,.06);
            border-color: rgba(227,6,19,.10);
            color: #bf0812;
        }
        .wl-outline__item.level-2 { padding-left: 1.1rem; }
        .wl-outline__item.level-3 { padding-left: 1.5rem; }
        .wl-outline__empty {
            padding: 0.55rem;
            color: #9ca3af;
            font: 700 .76rem/1.45 Manrope, sans-serif;
        }
        .wl-comments {
            position: sticky;
            top: 4.6rem;
            max-height: calc(100vh - 5.4rem);
            overflow: auto;
            border-radius: 24px;
            border: 1px solid rgba(17,24,39,.08);
            background: rgba(255,255,255,.92);
            box-shadow: 0 18px 40px rgba(17,24,39,.08);
            backdrop-filter: blur(12px);
        }
        .wl-comments__head {
            position: sticky;
            top: 0;
            z-index: 2;
            padding: 0.9rem 0.95rem 0.7rem;
            background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(255,255,255,.92));
            border-bottom: 1px solid rgba(17,24,39,.06);
        }
        .wl-comments__title {
            color: #111827;
            font: 800 .92rem/1.2 Manrope, sans-serif;
        }
        .wl-comments__subtitle {
            margin-top: 0.2rem;
            color: #6b7280;
            font: 600 .74rem/1.45 Manrope, sans-serif;
        }
        .wl-comments__context {
            margin-top: 0.7rem;
            padding: 0.72rem 0.78rem;
            border-radius: 16px;
            background: rgba(227,6,19,.05);
            color: #374151;
            font: 700 .77rem/1.45 Manrope, sans-serif;
            white-space: pre-wrap;
        }
        .wl-comments__context.is-muted {
            background: rgba(243,244,246,.88);
            color: #6b7280;
        }
        .wl-comments__composer {
            display: grid;
            gap: 0.55rem;
            margin-top: 0.7rem;
        }
        .wl-comments__composer textarea,
        .wl-thread__reply textarea {
            width: 100%;
            min-height: 78px;
            resize: vertical;
            border-radius: 16px;
            border: 1px solid rgba(17,24,39,.08);
            background: #ffffff;
            padding: 0.78rem 0.82rem;
            color: #111827;
            font: 600 .8rem/1.55 Manrope, sans-serif;
            box-sizing: border-box;
        }
        .wl-comments__composer textarea:focus,
        .wl-thread__reply textarea:focus {
            outline: none;
            border-color: rgba(227,6,19,.22);
            box-shadow: 0 0 0 3px rgba(227,6,19,.06);
        }
        .wl-comments__submit,
        .wl-thread__reply-send {
            border: 1px solid rgba(227,6,19,.24);
            background: #ffffff;
            color: #bf0812;
            border-radius: 14px;
            padding: 0.64rem 0.8rem;
            font: 800 .78rem/1 Manrope, sans-serif;
            cursor: pointer;
            transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
        }
        .wl-comments__submit:hover,
        .wl-thread__reply-send:hover {
            transform: translateY(-1px);
            border-color: rgba(227,6,19,.44);
            box-shadow: 0 10px 22px rgba(227,6,19,.08);
        }
        .wl-comments__submit:disabled,
        .wl-thread__reply-send:disabled {
            opacity: .42;
            box-shadow: none;
            transform: none;
            cursor: default;
        }
        .wl-comments__list {
            display: grid;
            gap: 0.75rem;
            padding: 0.9rem 0.95rem 1rem;
        }
        .wl-comments__empty {
            padding: 0.85rem;
            border-radius: 16px;
            background: rgba(243,244,246,.86);
            color: #6b7280;
            font: 700 .76rem/1.5 Manrope, sans-serif;
        }
        .wl-thread {
            padding: 0.8rem;
            border-radius: 18px;
            border: 1px solid rgba(17,24,39,.06);
            background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(249,250,251,.96));
            box-shadow: 0 12px 28px rgba(17,24,39,.05);
        }
        .wl-thread.is-focused {
            border-color: rgba(227,6,19,.20);
            box-shadow: 0 18px 34px rgba(227,6,19,.08);
        }
        .wl-thread.is-resolved { opacity: .74; }
        .wl-thread__row {
            display: grid;
            grid-template-columns: 2rem minmax(0, 1fr);
            gap: 0.62rem;
            align-items: start;
        }
        .wl-thread__avatar {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background: rgba(227,6,19,.10);
            color: #bf0812;
            font: 800 .78rem/1 Manrope, sans-serif;
        }
        .wl-thread__bubble {
            border-radius: 16px;
            background: #ffffff;
            padding: 0.72rem 0.8rem;
            border: 1px solid rgba(17,24,39,.06);
        }
        .wl-thread__author {
            color: #111827;
            font: 800 .78rem/1.2 Manrope, sans-serif;
        }
        .wl-thread__meta {
            margin-top: 0.16rem;
            color: #9ca3af;
            font: 700 .7rem/1.2 Manrope, sans-serif;
        }
        .wl-thread__body {
            margin-top: 0.38rem;
            color: #1f2937;
            font: 600 .8rem/1.55 Manrope, sans-serif;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .wl-thread__selection {
            margin-top: 0.46rem;
            color: #6b7280;
            font: 700 .72rem/1.45 Manrope, sans-serif;
        }
        .wl-thread__replies {
            display: grid;
            gap: 0.48rem;
            margin-top: 0.62rem;
        }
        .wl-thread__reply-row {
            display: grid;
            grid-template-columns: 1.65rem minmax(0, 1fr);
            gap: 0.48rem;
            align-items: start;
        }
        .wl-thread__reply-avatar {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.65rem;
            height: 1.65rem;
            border-radius: 999px;
            background: rgba(243,244,246,.9);
            color: #6b7280;
            font: 800 .7rem/1 Manrope, sans-serif;
        }
        .wl-thread__reply-bubble {
            border-radius: 14px;
            background: rgba(249,250,251,.95);
            padding: 0.56rem 0.64rem;
            border: 1px solid rgba(17,24,39,.05);
        }
        .wl-thread__actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.42rem;
            margin-top: 0.65rem;
        }
        .wl-thread__actions button {
            border: 1px solid rgba(17,24,39,.08);
            background: #ffffff;
            color: #4b5563;
            border-radius: 999px;
            padding: 0.38rem 0.62rem;
            font: 800 .72rem/1 Manrope, sans-serif;
            cursor: pointer;
        }
        .wl-thread__reply {
            display: grid;
            gap: 0.42rem;
            margin-top: 0.65rem;
        }
        .wl-thread__reply textarea {
            min-height: 60px;
        }
        .wl-selection-bubble {
            position: fixed;
            z-index: 99998;
            display: none;
            align-items: center;
            gap: 0.32rem;
            padding: 0.3rem;
            border-radius: 14px;
            border: 1px solid rgba(17,24,39,.08);
            background: rgba(255,255,255,.98);
            box-shadow: 0 16px 32px rgba(17,24,39,.14);
        }
        .wl-selection-bubble button {
            min-width: 2rem;
            height: 2rem;
            border-radius: 10px;
            border: 1px solid rgba(227,6,19,.16);
            background: #ffffff;
            color: #111827;
            font: 800 .76rem/1 Manrope, sans-serif;
            cursor: pointer;
        }
        @media (max-width: 980px) {
            .wl-outline { display: none; }
            .wl-workbench { grid-template-columns: 1fr; }
            .wl-canvas { padding: 0 0.2rem 3rem; max-width: none; }
            .wl-comments {
                position: static;
                max-height: none;
                margin: 0 0.2rem;
            }
            .wl-editor { min-height: 64vh; font-size: 16px; }
            .wl-block-handle { left: -0.1rem; }
            .wl-block-comment { right: 0.1rem; }
        }
        </style>
        <div class="wikilive-rich-root">
            <aside class="wl-outline">
                <button id="wl-outline-handle" class="wl-outline__handle" type="button" data-tip="Оглавление">#</button>
                <div class="wl-outline__panel">
                    <div id="wl-outline-list" class="wl-outline__list"></div>
                </div>
            </aside>
            <div class="wl-toolbar">
                <div class="wl-toolbar__group">
                    <button id="wl-undo" class="wl-toolbar__icon" type="button" data-tip="Отменить&#10;Ctrl+Z">&#8630;</button>
                    <button id="wl-redo" class="wl-toolbar__icon" type="button" data-tip="Повторить&#10;Ctrl+Shift+Z / Ctrl+Y">&#8631;</button>
                    <span class="wl-toolbar__sep"></span>
                    <select id="wl-block-style" data-tip="Стиль текста&#10;Alt+1 / Alt+2 / Alt+3">
                        <option value="line">Текст</option>
                        <option value="heading1">H1</option>
                        <option value="heading2">H2</option>
                        <option value="heading3">H3</option>
                        <option value="callout">Цитата</option>
                    </select>
                    <button id="wl-bold" class="wl-toolbar__icon" type="button" data-tip="Жирный&#10;Ctrl+B">B</button>
                    <button id="wl-italic" class="wl-toolbar__icon" type="button" data-tip="Курсив&#10;Ctrl+I">I</button>
                    <button id="wl-underline" class="wl-toolbar__icon" type="button" data-tip="Подчеркнутый&#10;Ctrl+U">U</button>
                    <button id="wl-strike" class="wl-toolbar__icon" type="button" data-tip="Зачеркнутый&#10;Alt+Shift+5">S</button>
                    <span class="wl-toolbar__sep"></span>
                    <button id="wl-align-left" class="wl-toolbar__icon" type="button" data-tip="Слева&#10;Alt+Shift+L">L</button>
                    <button id="wl-align-center" class="wl-toolbar__icon" type="button" data-tip="По центру&#10;Alt+Shift+C">C</button>
                    <button id="wl-align-right" class="wl-toolbar__icon" type="button" data-tip="Справа&#10;Alt+Shift+R">R</button>
                </div>
                <div class="wl-toolbar__group">
                    <button id="wl-insert-object" class="wl-toolbar__icon wl-toolbar__symbol" type="button" data-tip="Объект из таблицы&#10;@">@</button>
                    <button id="wl-insert-code" class="wl-toolbar__symbol" type="button" data-tip="Блок кода&#10;/code">&lt;/&gt;</button>
                    <button id="wl-insert-quote" class="wl-toolbar__symbol" type="button" data-tip="Цитата&#10;/quote">``</button>
                    <button id="wl-insert-photo" class="wl-toolbar__icon wl-toolbar__symbol" type="button" data-tip="Фото&#10;/photo">&#128444;</button>
                    <input id="wl-image-width" type="range" min="180" max="720" step="10" />
                    <input id="wl-image-opacity" type="range" min="20" max="100" step="5" />
                </div>
            </div>
            <input id="wl-file-input" type="file" multiple hidden />
            <div class="wl-workbench">
                <div class="wl-canvas">
                    <div id="wikilive-editor" class="wl-editor" contenteditable="true" spellcheck="true" data-placeholder="Пиши здесь"></div>
                </div>
                <aside class="wl-comments">
                    <div class="wl-comments__head">
                        <div class="wl-comments__title">Обсуждение</div>
                        <div class="wl-comments__subtitle">Комментарии прямо по абзацам</div>
                        <div id="wl-comment-context" class="wl-comments__context is-muted">Выбери абзац или выдели текст</div>
                        <div class="wl-comments__composer">
                            <textarea id="wl-comment-input" placeholder="Напиши комментарий"></textarea>
                            <button id="wl-comment-submit" class="wl-comments__submit" type="button">Отправить</button>
                        </div>
                    </div>
                    <div id="wl-comments-list" class="wl-comments__list"></div>
                </aside>
            </div>
        </div>
        <div id="wikilive-context-menu" class="wl-context-menu">
            <button id="wikilive-context-open" type="button">Выбрать из таблицы</button>
            <button id="wikilive-context-insert" type="button">Вставить значение</button>
            <div id="wikilive-context-hint" class="wl-context-menu__hint"></div>
        </div>
        <div id="wikilive-slash-menu" class="wl-slash-menu"></div>
        <div id="wikilive-selection-bubble" class="wl-selection-bubble">
            <button id="wl-bubble-bold" type="button" title="Жирный">B</button>
            <button id="wl-bubble-italic" type="button" title="Курсив">I</button>
            <button id="wl-bubble-quote" type="button" title="Цитата">``</button>
            <button id="wl-bubble-comment" type="button" title="Комментарий">&#128172;</button>
        </div>
        <script>
        const parentWindow = window.parent;
        const parentDoc = parentWindow.document;
        const lookup = __WIKILIVE_LOOKUP__;
        const draftKey = __WIKILIVE_DRAFT_KEY__;
        const pageBreakMarker = __WIKILIVE_PAGE_BREAK_MARKER__;
        const pageId = __WIKILIVE_PAGE_ID__;
        const backendUrl = (__WIKILIVE_BACKEND_URL__ || "").replace(/\/$/, "");
        let activeSnippet = __WIKILIVE_ACTIVE_SNIPPET__;
        let activeHint = __WIKILIVE_ACTIVE_HINT__;
        const storageKey = `wikilive:draft:${draftKey}`;
        const selectedKey = `wikilive:selected:${draftKey}`;
        const snippetKey = `wikilive:active-snippet:${draftKey}`;
        const hintKey = `wikilive:active-hint:${draftKey}`;
        const blockMapKey = `wikilive:block-map:${draftKey}`;
        const tokenRegex = /(\{\{([^:}\n]+):([^:}\n]+):([^}\n]+)\}\}|\[\[WL_ATTACHMENT:([^\]]+)\]\])/g;
        const tableSeparatorRegex = /^:?-{3,}:?$/;
        const inlineStyleRegex = /(\*\*[^*][^*]*\*\*|__[^_][^_]*__|~~[^~][^~]*~~|\*[^*][^*]*\*)/g;
        const editor = document.getElementById("wikilive-editor");
        const contextMenu = document.getElementById("wikilive-context-menu");
        const contextOpenButton = document.getElementById("wikilive-context-open");
        const contextInsertButton = document.getElementById("wikilive-context-insert");
        const contextHintNode = document.getElementById("wikilive-context-hint");
        const slashMenu = document.getElementById("wikilive-slash-menu");
        const selectionBubble = document.getElementById("wikilive-selection-bubble");
        const outlineList = document.getElementById("wl-outline-list");
        const blockStyleSelect = document.getElementById("wl-block-style");
        const fileInput = document.getElementById("wl-file-input");
        const imageWidthInput = document.getElementById("wl-image-width");
        const imageOpacityInput = document.getElementById("wl-image-opacity");
        const commentsList = document.getElementById("wl-comments-list");
        const commentContext = document.getElementById("wl-comment-context");
        const commentInput = document.getElementById("wl-comment-input");
        const commentSubmit = document.getElementById("wl-comment-submit");
        const bubbleBoldButton = document.getElementById("wl-bubble-bold");
        const bubbleItalicButton = document.getElementById("wl-bubble-italic");
        const bubbleQuoteButton = document.getElementById("wl-bubble-quote");
        const bubbleCommentButton = document.getElementById("wl-bubble-comment");
        const undoButton = document.getElementById("wl-undo");
        const redoButton = document.getElementById("wl-redo");
        const formatButtons = {
            bold: document.getElementById("wl-bold"),
            italic: document.getElementById("wl-italic"),
            underline: document.getElementById("wl-underline"),
            strikeThrough: document.getElementById("wl-strike"),
        };
        const alignButtons = {
            left: document.getElementById("wl-align-left"),
            center: document.getElementById("wl-align-center"),
            right: document.getElementById("wl-align-right"),
        };
        const slashActions = [
            { id: "heading1", label: "Заголовок 1", meta: "H1", run: () => applyBlockStyle("heading1") },
            { id: "heading2", label: "Заголовок 2", meta: "H2", run: () => applyBlockStyle("heading2") },
            { id: "heading3", label: "Заголовок 3", meta: "H3", run: () => applyBlockStyle("heading3") },
            { id: "quote", label: "Цитата", meta: "``", run: () => applyBlockStyle("callout") },
            { id: "code", label: "Код", meta: "</>", run: () => insertCodeBlock() },
            { id: "object", label: "Объект", meta: "@", run: () => openPicker() },
            { id: "photo", label: "Фото", meta: "image", run: () => openImagePicker() },
        ];
        let selectedObject = null;
        let lastRange = null;
        let dragRaw = "";
        let dragSourceNode = null;
        let isRendering = false;
        let storeTimer = null;
        let selectionTimer = null;
        let toolbarTimer = null;
        let outlineTimer = null;
        let frameTimer = null;
        let historyTimer = null;
        let commentsTimer = null;
        let historyStack = [];
        let historyIndex = -1;
        let applyingHistory = false;
        let commentThreads = [];
        let commentTarget = null;
        let commentsLoading = false;
        let commentsLoaded = false;

        function targetArea() {
            return parentDoc.querySelector('div[data-testid="stTextArea"] textarea') || parentDoc.querySelector("textarea");
        }

        function normalizeRaw(raw) {
            return String(raw || "").replaceAll(`\n${pageBreakMarker}\n`, "\n\n").replaceAll(pageBreakMarker, "");
        }

        function getHiddenValue() {
            const area = targetArea();
            return area ? String(area.value || "") : "";
        }

        function setHiddenValue(value) {
            const area = targetArea();
            if (!area) return;
            const descriptor = Object.getOwnPropertyDescriptor(parentWindow.HTMLTextAreaElement.prototype, "value");
            if (descriptor && descriptor.set) descriptor.set.call(area, value);
            else area.value = value;
            area.dispatchEvent(new Event("input", { bubbles: true }));
            area.dispatchEvent(new Event("change", { bubbles: true }));
        }

        function loadDraft() {
            parentWindow.__wikiliveDrafts = parentWindow.__wikiliveDrafts || {};
            const parentDraft = parentWindow.__wikiliveDrafts[draftKey];
            if (typeof parentDraft === "string") return parentDraft;
            const stored = parentWindow.sessionStorage.getItem(storageKey);
            if (stored !== null) return stored;
            return getHiddenValue();
        }

        function storeDraft(raw) {
            parentWindow.__wikiliveDrafts = parentWindow.__wikiliveDrafts || {};
            parentWindow.__wikiliveDrafts[draftKey] = raw;
            parentWindow.sessionStorage.setItem(storageKey, raw);
        }

        function ensureActiveSnippetState() {
            parentWindow.__wikiliveActiveSnippets = parentWindow.__wikiliveActiveSnippets || {};
            if (typeof activeSnippet === "string" && activeSnippet) {
                parentWindow.__wikiliveActiveSnippets[draftKey] = activeSnippet;
                parentWindow.sessionStorage.setItem(snippetKey, activeSnippet);
            } else {
                activeSnippet = parentWindow.__wikiliveActiveSnippets[draftKey] || parentWindow.sessionStorage.getItem(snippetKey) || "";
            }
            parentWindow.__wikiliveActiveHints = parentWindow.__wikiliveActiveHints || {};
            if (typeof activeHint === "string" && activeHint) {
                parentWindow.__wikiliveActiveHints[draftKey] = activeHint;
                parentWindow.sessionStorage.setItem(hintKey, activeHint);
            } else {
                activeHint = parentWindow.__wikiliveActiveHints[draftKey] || parentWindow.sessionStorage.getItem(hintKey) || "";
            }
        }

        function getTopBlocks() {
            return Array.from(editor.childNodes).filter((node) => node.nodeType === Node.ELEMENT_NODE);
        }

        function queueFrameHeight() {
            if (frameTimer !== null) window.cancelAnimationFrame(frameTimer);
            frameTimer = window.requestAnimationFrame(() => {
                frameTimer = null;
                const height = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, editor.scrollHeight + 260) + 24;
                parentWindow.postMessage({ type: "streamlit:setFrameHeight", height }, "*");
            });
        }

        function syncHiddenState() {
            const raw = serializeDocument();
            storeDraft(raw);
            setHiddenValue(raw);
        }

        function attachActionSync() {
            parentDoc.querySelectorAll("button").forEach((button) => {
                if (button.dataset.wikiliveSyncAttached === "1") return;
                button.dataset.wikiliveSyncAttached = "1";
                button.addEventListener("mousedown", () => syncHiddenState(), true);
            });
        }

        function hideContextMenu() {
            contextMenu.style.display = "none";
        }

        function refreshContextMenu() {
            ensureActiveSnippetState();
            contextInsertButton.disabled = !activeSnippet;
            contextHintNode.textContent = activeHint || (activeSnippet ? "Готово к вставке" : "Сначала выбери диапазон");
        }

        function showContextMenu(x, y) {
            refreshContextMenu();
            contextMenu.style.left = `${Math.min(x, window.innerWidth - 240)}px`;
            contextMenu.style.top = `${Math.min(y, window.innerHeight - 140)}px`;
            contextMenu.style.display = "block";
        }

        function hideSlashMenu() {
            slashMenu.style.display = "none";
            slashMenu.innerHTML = "";
        }

        function openPicker() {
            const button = Array.from(parentDoc.querySelectorAll("button")).find((node) => {
                const text = (node.textContent || "").trim();
                return text === "Таблица" || text === "Скрыть таблицу";
            });
            if (button) button.click();
        }

        function openImagePicker() {
            fileInput.setAttribute("accept", "image/*");
            fileInput.click();
        }

        function closestObjectNode(node) {
            if (!node) return null;
            if (node.nodeType === Node.ELEMENT_NODE) return node.closest("[data-raw]");
            return node.parentElement ? node.parentElement.closest("[data-raw]") : null;
        }

        function closestBlock(node) {
            if (!node) return null;
            if (node.nodeType === Node.ELEMENT_NODE) return node.closest(".wl-line, .wl-table-block, .wl-code-block");
            return node.parentElement ? node.parentElement.closest(".wl-line, .wl-table-block, .wl-code-block") : null;
        }

        function clearSelectedObject() {
            if (selectedObject) selectedObject.classList.remove("is-selected");
            selectedObject = null;
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            delete parentWindow.__wikiliveSelectedObjects[draftKey];
            parentWindow.sessionStorage.removeItem(selectedKey);
            imageWidthInput.style.display = "none";
            imageOpacityInput.style.display = "none";
        }

        function applyAttachmentPresentation(node, meta) {
            const width = Math.max(180, Math.min(Number(meta.width || 420), 720));
            const opacity = Math.max(.2, Math.min(Number(meta.opacity || 1), 1));
            node.dataset.width = String(width);
            node.dataset.opacity = String(opacity);
            node.style.maxWidth = `${width}px`;
            node.style.opacity = String(opacity);
        }

        function selectObject(node) {
            clearSelectedObject();
            selectedObject = node;
            selectedObject.classList.add("is-selected");
            const tokenIndex = selectedObject.dataset.tokenIndex || "";
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            parentWindow.__wikiliveSelectedObjects[draftKey] = tokenIndex;
            parentWindow.sessionStorage.setItem(selectedKey, tokenIndex);
            if (selectedObject.classList.contains("wl-attachment--image")) {
                imageWidthInput.value = String(parseInt(selectedObject.dataset.width || "420", 10));
                imageOpacityInput.value = String(Math.round((Number(selectedObject.dataset.opacity || "1")) * 100));
                imageWidthInput.style.display = "block";
                imageOpacityInput.style.display = "block";
            }
        }

        function restoreSelectedObject() {
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            const storedIndex = parentWindow.__wikiliveSelectedObjects[draftKey] || parentWindow.sessionStorage.getItem(selectedKey);
            if (!storedIndex) return;
            const node = editor.querySelector(`[data-token-index="${storedIndex}"]`);
            if (node) {
                selectedObject = node;
                selectedObject.classList.add("is-selected");
            }
        }

        function createTextNode(text) {
            return document.createTextNode(text);
        }

        function decodeAttachmentPayload(payload) {
            try { return JSON.parse(decodeURIComponent(payload || "")); }
            catch (error) { return { name: "Вложение", mime: "", src: "", width: 420, opacity: 1 }; }
        }

        function buildAttachmentSnippet(meta) {
            return `[[WL_ATTACHMENT:${encodeURIComponent(JSON.stringify(meta))}]]`;
        }

        function isImageMeta(meta) {
            return Boolean((meta.mime || "").startsWith("image/") || String(meta.src || "").startsWith("data:image/"));
        }

        function appendFormattedText(target, text) {
            inlineStyleRegex.lastIndex = 0;
            let cursor = 0;
            let match;
            while ((match = inlineStyleRegex.exec(text)) !== null) {
                if (match.index > cursor) target.appendChild(createTextNode(text.slice(cursor, match.index)));
                const token = match[0];
                let node = null;
                if (token.startsWith("**") && token.endsWith("**")) {
                    node = document.createElement("strong");
                    node.textContent = token.slice(2, -2);
                } else if (token.startsWith("__") && token.endsWith("__")) {
                    node = document.createElement("u");
                    node.className = "wl-inline-mark--underline";
                    node.textContent = token.slice(2, -2);
                } else if (token.startsWith("~~") && token.endsWith("~~")) {
                    node = document.createElement("s");
                    node.className = "wl-inline-mark--strike";
                    node.textContent = token.slice(2, -2);
                } else if (token.startsWith("*") && token.endsWith("*")) {
                    node = document.createElement("em");
                    node.textContent = token.slice(1, -1);
                }
                target.appendChild(node || createTextNode(token));
                cursor = inlineStyleRegex.lastIndex;
            }
            if (cursor < text.length) target.appendChild(createTextNode(text.slice(cursor)));
        }

        function createAttachmentNode(raw, meta, tokenIndex, labelOverride = "") {
            if (isImageMeta(meta)) {
                const figure = document.createElement("figure");
                figure.className = "wl-attachment wl-attachment--image";
                figure.contentEditable = "false";
                figure.draggable = true;
                figure.dataset.raw = raw;
                figure.dataset.tokenIndex = String(tokenIndex);
                applyAttachmentPresentation(figure, meta);
                const image = document.createElement("img");
                image.src = meta.src || "";
                image.alt = meta.name || labelOverride || "Вложение";
                figure.appendChild(image);
                const caption = document.createElement("div");
                caption.className = "wl-attachment__caption";
                const nameNode = document.createElement("span");
                nameNode.className = "wl-attachment__name";
                nameNode.textContent = meta.name || labelOverride || "Изображение";
                caption.appendChild(nameNode);
                const typeNode = document.createElement("span");
                typeNode.className = "wl-attachment__type";
                typeNode.textContent = labelOverride || "Фото";
                caption.appendChild(typeNode);
                figure.appendChild(caption);
                return figure;
            }
            const chip = document.createElement("div");
            chip.className = "wl-attachment wl-attachment--file";
            chip.contentEditable = "false";
            chip.draggable = true;
            chip.dataset.raw = raw;
            chip.dataset.tokenIndex = String(tokenIndex);
            const dot = document.createElement("span");
            dot.className = "wl-attachment__dot";
            chip.appendChild(dot);
            const metaRow = document.createElement("div");
            metaRow.className = "wl-attachment__meta";
            const nameNode = document.createElement("span");
            nameNode.className = "wl-attachment__name";
            nameNode.textContent = meta.name || labelOverride || "Файл";
            metaRow.appendChild(nameNode);
            const typeNode = document.createElement("span");
            typeNode.className = "wl-attachment__type";
            typeNode.textContent = meta.mime || "attachment";
            metaRow.appendChild(typeNode);
            chip.appendChild(metaRow);
            return chip;
        }

        function createObjectNode(raw, tableId, recordId, fieldName, tokenIndex) {
            const meta = lookup[`${tableId}::${recordId}::${fieldName}`] || { value: "Живое поле", resourceUrl: "", mimeType: "", isImage: false };
            if (meta.isImage && meta.resourceUrl) {
                return createAttachmentNode(
                    raw,
                    { name: meta.value || fieldName, mime: meta.mimeType || "image/*", src: meta.resourceUrl, width: 320, opacity: 1 },
                    tokenIndex,
                    fieldName,
                );
            }
            const chip = document.createElement("span");
            chip.className = "wl-object";
            chip.contentEditable = "false";
            chip.draggable = true;
            chip.dataset.raw = raw;
            chip.dataset.tokenIndex = String(tokenIndex);
            const fieldNode = document.createElement("span");
            fieldNode.className = "wl-object__field";
            fieldNode.textContent = fieldName;
            chip.appendChild(fieldNode);
            const valueNode = document.createElement("span");
            valueNode.className = "wl-object__value";
            valueNode.textContent = meta.value || "Живое поле";
            chip.appendChild(valueNode);
            return chip;
        }

        function renderInline(target, text, state) {
            tokenRegex.lastIndex = 0;
            let cursor = 0;
            let match;
            while ((match = tokenRegex.exec(text)) !== null) {
                if (match.index > cursor) appendFormattedText(target, text.slice(cursor, match.index));
                const tokenIndex = state.tokenIndex++;
                if (match[2]) target.appendChild(createObjectNode(match[0], match[2], match[3], match[4], tokenIndex));
                else target.appendChild(createAttachmentNode(match[0], decodeAttachmentPayload(match[5]), tokenIndex));
                cursor = tokenRegex.lastIndex;
            }
            if (cursor < text.length) appendFormattedText(target, text.slice(cursor));
            if (!target.childNodes.length) target.appendChild(document.createElement("br"));
        }

        function applyAlignmentToBlock(block, align) {
            block.dataset.align = align || "left";
            block.style.textAlign = block.dataset.align;
        }

        function createLineBlock(kind, text, state, align = "left") {
            const line = document.createElement("div");
            line.className = "wl-line";
            line.dataset.kind = kind;
            applyAlignmentToBlock(line, align);
            const handle = document.createElement("button");
            handle.type = "button";
            handle.className = "wl-block-handle";
            handle.dataset.ui = "1";
            handle.contentEditable = "false";
            handle.textContent = "≡";
            const body = document.createElement("div");
            body.className = "wl-line__body";
            renderInline(body, text, state);
            const commentButton = document.createElement("button");
            commentButton.type = "button";
            commentButton.className = "wl-block-comment";
            commentButton.dataset.ui = "1";
            commentButton.contentEditable = "false";
            commentButton.innerHTML = '<span class="wl-block-comment__icon">&#128172;</span><span class="wl-block-comment__count"></span>';
            line.appendChild(handle);
            line.appendChild(body);
            line.appendChild(commentButton);
            return line;
        }

        function createCodeBlock(raw, codeText) {
            const block = document.createElement("pre");
            block.className = "wl-code-block";
            block.dataset.kind = "code";
            block.dataset.blockRaw = raw;
            block.contentEditable = "false";
            block.textContent = codeText || "code";
            return block;
        }

        function parseTableCells(line) {
            return line.trim().slice(1, -1).split("|").map((cell) => cell.trim());
        }

        function isTableLine(line) {
            const stripped = line.trim();
            return stripped.startsWith("|") && stripped.endsWith("|") && stripped.length > 2;
        }

        function isTableSeparator(line) {
            const cells = parseTableCells(line);
            return cells.length > 0 && cells.every((cell) => tableSeparatorRegex.test(cell));
        }

        function createTableBlock(blockRaw, headerCells, bodyRows, state) {
            const wrap = document.createElement("div");
            wrap.className = "wl-table-block";
            wrap.dataset.kind = "table";
            wrap.dataset.blockRaw = blockRaw;
            wrap.contentEditable = "false";
            const table = document.createElement("table");
            table.className = "wl-table";
            const thead = document.createElement("thead");
            const headRow = document.createElement("tr");
            headerCells.forEach((cell) => {
                const th = document.createElement("th");
                renderInline(th, cell, state);
                headRow.appendChild(th);
            });
            thead.appendChild(headRow);
            table.appendChild(thead);
            const tbody = document.createElement("tbody");
            bodyRows.forEach((row) => {
                const tr = document.createElement("tr");
                row.forEach((cell) => {
                    const td = document.createElement("td");
                    renderInline(td, cell, state);
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            wrap.appendChild(table);
            return wrap;
        }

        function extractAlignment(text) {
            const match = String(text || "").match(/^\[\[ALIGN:(left|center|right)\]\]\s*/);
            if (!match) return { align: "left", text };
            return { align: match[1], text: String(text || "").slice(match[0].length) };
        }

        function renderBlocks(container, raw, state) {
            const lines = normalizeRaw(raw).replace(/\r\n/g, "\n").split("\n");
            let index = 0;
            while (index < lines.length) {
                const line = lines[index];
                const trimmed = line.trim();
                if (!trimmed) {
                    container.appendChild(createLineBlock("line", "", state));
                    index += 1;
                    continue;
                }
                if (trimmed.startsWith("```")) {
                    const codeLines = [];
                    const blockLines = [line];
                    index += 1;
                    while (index < lines.length && !lines[index].trim().startsWith("```")) {
                        codeLines.push(lines[index]);
                        blockLines.push(lines[index]);
                        index += 1;
                    }
                    if (index < lines.length) {
                        blockLines.push(lines[index]);
                        index += 1;
                    }
                    container.appendChild(createCodeBlock(blockLines.join("\n"), codeLines.join("\n")));
                    continue;
                }
                if (
                    isTableLine(trimmed) &&
                    index + 1 < lines.length &&
                    isTableLine(lines[index + 1].trim()) &&
                    isTableSeparator(lines[index + 1].trim())
                ) {
                    const blockLines = [line, lines[index + 1]];
                    const headerCells = parseTableCells(trimmed);
                    const bodyRows = [];
                    index += 2;
                    while (index < lines.length && isTableLine(lines[index].trim())) {
                        const rowLine = lines[index];
                        const rowCells = parseTableCells(rowLine);
                        if (rowCells.length !== headerCells.length) break;
                        blockLines.push(rowLine);
                        bodyRows.push(rowCells);
                        index += 1;
                    }
                    container.appendChild(createTableBlock(blockLines.join("\n"), headerCells, bodyRows, state));
                    continue;
                }
                let kind = "line";
                let content = line;
                if (trimmed.startsWith("### ")) {
                    kind = "heading3";
                    content = line.slice(line.indexOf("### ") + 4);
                } else if (trimmed.startsWith("## ")) {
                    kind = "heading2";
                    content = line.slice(line.indexOf("## ") + 3);
                } else if (trimmed.startsWith("# ")) {
                    kind = "heading1";
                    content = line.slice(line.indexOf("# ") + 2);
                } else if (trimmed.startsWith("> ")) {
                    kind = "callout";
                    content = line.slice(line.indexOf("> ") + 2);
                }
                const aligned = extractAlignment(content);
                container.appendChild(createLineBlock(kind, aligned.text, state, aligned.align));
                index += 1;
            }
            if (!container.childNodes.length) container.appendChild(createLineBlock("line", "", state));
        }

        function renderRaw(raw) {
            isRendering = true;
            clearSelectedObject();
            editor.innerHTML = "";
            renderBlocks(editor, raw, { tokenIndex: 0 });
            assignBlockAnchors();
            restoreSelectedObject();
            isRendering = false;
            if (commentTarget) setCommentTarget(commentTarget);
            else refreshCommentComposerState();
            updateCommentBadges();
            renderComments();
            queueToolbarRefresh();
            queueOutlineRefresh();
            queueFrameHeight();
        }

        function serializeInlineNode(node) {
            if (node.nodeType === Node.TEXT_NODE) return (node.textContent || "").replace(/\u00a0/g, " ");
            if (node.nodeType !== Node.ELEMENT_NODE) return "";
            const element = node;
            if (element.dataset && element.dataset.ui === "1") return "";
            if (element.dataset && element.dataset.raw) return element.dataset.raw;
            if (element.tagName === "BR") return "";
            if (element.tagName === "STRONG" || element.tagName === "B") return `**${Array.from(element.childNodes).map(serializeInlineNode).join("")}**`;
            if (element.tagName === "EM" || element.tagName === "I") return `*${Array.from(element.childNodes).map(serializeInlineNode).join("")}*`;
            if (element.tagName === "U") return `__${Array.from(element.childNodes).map(serializeInlineNode).join("")}__`;
            if (element.tagName === "S" || element.tagName === "STRIKE" || element.tagName === "DEL") return `~~${Array.from(element.childNodes).map(serializeInlineNode).join("")}~~`;
            return Array.from(element.childNodes).map(serializeInlineNode).join("");
        }

        function serializeBlockNode(node) {
            if (node.nodeType === Node.TEXT_NODE) return (node.textContent || "").replace(/\u00a0/g, " ");
            if (node.nodeType !== Node.ELEMENT_NODE) return "";
            const element = node;
            if (element.dataset && element.dataset.kind === "table") return element.dataset.blockRaw || "";
            if (element.dataset && element.dataset.kind === "code") return element.dataset.blockRaw || "```\ncode\n```";
            const kind = element.dataset.kind || "line";
            const alignPrefix = element.dataset.align && element.dataset.align !== "left" ? `[[ALIGN:${element.dataset.align}]] ` : "";
            const text = Array.from(element.childNodes).map(serializeInlineNode).join("");
            if (kind === "heading1") return `# ${alignPrefix}${text}`;
            if (kind === "heading2") return `## ${alignPrefix}${text}`;
            if (kind === "heading3") return `### ${alignPrefix}${text}`;
            if (kind === "callout") return `> ${alignPrefix}${text}`;
            return `${alignPrefix}${text}`;
        }

        function serializeDocument() {
            return getTopBlocks().map(serializeBlockNode).join("\n");
        }

        function blockPlainText(block) {
            if (!block) return "";
            const clone = block.cloneNode(true);
            clone.querySelectorAll('[data-ui="1"]').forEach((node) => node.remove());
            return String(clone.textContent || "").replace(/\s+/g, " ").trim();
        }

        function clipPreview(text, limit = 96) {
            const value = String(text || "").replace(/\s+/g, " ").trim();
            if (!value) return "Абзац";
            return value.length > limit ? `${value.slice(0, limit - 1)}…` : value;
        }

        function randomId(prefix = "wl") {
            return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
        }

        function loadStoredBlockMap() {
            try {
                const raw = parentWindow.sessionStorage.getItem(blockMapKey);
                const parsed = raw ? JSON.parse(raw) : [];
                return Array.isArray(parsed) ? parsed : [];
            } catch (error) {
                return [];
            }
        }

        function storeBlockMap(items) {
            parentWindow.sessionStorage.setItem(blockMapKey, JSON.stringify(items));
        }

        function assignBlockAnchors() {
            const previous = loadStoredBlockMap();
            const used = new Set();
            const next = [];
            getTopBlocks().forEach((block) => {
                const raw = serializeBlockNode(block);
                let matchIndex = previous.findIndex((item, index) => !used.has(index) && item && item.raw === raw);
                if (matchIndex < 0) {
                    const preview = clipPreview(blockPlainText(block));
                    matchIndex = previous.findIndex((item, index) => !used.has(index) && item && item.preview === preview);
                }
                const anchor = matchIndex >= 0 ? previous[matchIndex].anchor : randomId("blk");
                if (matchIndex >= 0) used.add(matchIndex);
                block.dataset.commentAnchor = anchor;
                next.push({
                    anchor,
                    raw,
                    preview: clipPreview(blockPlainText(block)),
                });
            });
            storeBlockMap(next);
        }

        function parseCommentSelectionLabel(label) {
            if (!label) return { anchor: "", preview: "", blockPreview: "" };
            try {
                const parsed = JSON.parse(label);
                if (parsed && typeof parsed === "object") {
                    return {
                        anchor: String(parsed.anchor || ""),
                        preview: clipPreview(parsed.preview || ""),
                        blockPreview: clipPreview(parsed.blockPreview || parsed.preview || ""),
                        kind: String(parsed.kind || "block"),
                    };
                }
            } catch (error) {}
            const fallback = clipPreview(label);
            return { anchor: "", preview: fallback, blockPreview: fallback, kind: "legacy" };
        }

        function formatCommentSelectionLabel(target) {
            return JSON.stringify({
                anchor: String(target?.anchor || ""),
                preview: clipPreview(target?.preview || ""),
                blockPreview: clipPreview(target?.blockPreview || target?.preview || ""),
                kind: String(target?.kind || "block"),
            });
        }

        function findBlockByAnchor(anchor) {
            if (!anchor) return null;
            return editor.querySelector(`[data-comment-anchor="${anchor}"]`);
        }

        function resolveThreadAnchor(thread) {
            const meta = parseCommentSelectionLabel(thread?.selectionLabel || "");
            if (meta.anchor) {
                const block = findBlockByAnchor(meta.anchor);
                if (block) return meta.anchor;
            }
            if (meta.blockPreview) {
                const match = getTopBlocks().find((block) => clipPreview(blockPlainText(block)) === meta.blockPreview);
                if (match) return match.dataset.commentAnchor || "";
            }
            return "";
        }

        function currentSelectionText() {
            const selection = window.getSelection();
            if (!selection || selection.rangeCount === 0 || selection.isCollapsed) return "";
            const text = selection.toString().replace(/\s+/g, " ").trim();
            return clipPreview(text, 120);
        }

        function buildCommentTarget(block, selectedText = "") {
            if (!block) return null;
            const blockPreview = clipPreview(blockPlainText(block));
            return {
                anchor: block.dataset.commentAnchor || "",
                preview: clipPreview(selectedText || blockPreview, 120),
                blockPreview,
                kind: selectedText ? "selection" : "block",
            };
        }

        function refreshCommentComposerState() {
            commentSubmit.disabled = !pageId || !commentTarget || !String(commentInput.value || "").trim();
        }

        function setCommentTarget(target) {
            commentTarget = target || null;
            getTopBlocks().forEach((block) => {
                block.classList.toggle("is-comment-target", Boolean(commentTarget && block.dataset.commentAnchor === commentTarget.anchor));
            });
            if (!pageId) {
                commentContext.classList.add("is-muted");
                commentContext.textContent = "Сначала сохрани страницу";
            } else if (!commentTarget) {
                commentContext.classList.add("is-muted");
                commentContext.textContent = "Выбери абзац или выдели текст";
            } else {
                commentContext.classList.remove("is-muted");
                commentContext.textContent = commentTarget.preview || commentTarget.blockPreview || "Абзац";
            }
            refreshCommentComposerState();
            renderComments();
        }

        function updateCommentBadges() {
            const counts = new Map();
            commentThreads.forEach((thread) => {
                const anchor = resolveThreadAnchor(thread);
                if (!anchor) return;
                counts.set(anchor, (counts.get(anchor) || 0) + 1);
            });
            getTopBlocks().forEach((block) => {
                const button = block.querySelector(".wl-block-comment");
                if (!button) return;
                const count = counts.get(block.dataset.commentAnchor || "") || 0;
                const countNode = button.querySelector(".wl-block-comment__count");
                if (countNode) countNode.textContent = count > 0 ? String(count) : "";
                block.classList.toggle("has-comments", count > 0);
            });
        }

        function initialsFromName(name) {
            const parts = String(name || "V").trim().split(/\s+/).filter(Boolean).slice(0, 2);
            return (parts.map((item) => item[0] || "").join("") || "V").toUpperCase();
        }

        function formatTimestamp(value) {
            if (!value) return "";
            const date = new Date(value);
            if (Number.isNaN(date.getTime())) return String(value);
            return date.toLocaleString("ru-RU", {
                day: "2-digit",
                month: "short",
                hour: "2-digit",
                minute: "2-digit",
            });
        }

        async function apiRequest(method, path, payload = null) {
            if (!backendUrl) throw new Error("backend_url_missing");
            const response = await fetch(`${backendUrl}${path}`, {
                method,
                headers: { "Content-Type": "application/json" },
                body: payload === null ? null : JSON.stringify(payload),
            });
            const data = await response.json().catch(() => ({ success: false, error: { message: "bad_response" } }));
            if (!response.ok || data.success !== true) {
                throw new Error(data?.error?.message || `request_failed_${response.status}`);
            }
            return data.data || {};
        }

        async function loadComments() {
            if (!pageId) {
                commentsLoaded = true;
                commentThreads = [];
                renderComments();
                updateCommentBadges();
                return;
            }
            commentsLoading = true;
            renderComments();
            try {
                const data = await apiRequest("GET", `/api/pages/${encodeURIComponent(pageId)}/comments`);
                commentThreads = Array.isArray(data.items) ? data.items : [];
            } catch (error) {
                commentThreads = [];
            } finally {
                commentsLoading = false;
                commentsLoaded = true;
                updateCommentBadges();
                renderComments();
            }
        }

        function scheduleCommentsRefresh(delay = 0) {
            if (commentsTimer !== null) window.clearTimeout(commentsTimer);
            commentsTimer = window.setTimeout(() => {
                commentsTimer = null;
                loadComments();
            }, delay);
        }

        async function submitComment() {
            const body = String(commentInput.value || "").trim();
            if (!pageId || !commentTarget || !body) return;
            commentSubmit.disabled = true;
            try {
                await apiRequest("POST", `/api/pages/${encodeURIComponent(pageId)}/comments`, {
                    body,
                    selectionLabel: formatCommentSelectionLabel(commentTarget),
                    author: "viewer",
                });
                commentInput.value = "";
                refreshCommentComposerState();
                scheduleCommentsRefresh(40);
            } catch (error) {
                commentContext.classList.add("is-muted");
                commentContext.textContent = "Не удалось отправить комментарий";
            } finally {
                refreshCommentComposerState();
            }
        }

        async function toggleThreadLike(threadId) {
            if (!pageId || !threadId) return;
            await apiRequest("POST", `/api/pages/${encodeURIComponent(pageId)}/comments/${encodeURIComponent(threadId)}/like`, {
                author: "viewer",
            });
            scheduleCommentsRefresh(20);
        }

        async function toggleThreadResolved(threadId, resolved) {
            if (!pageId || !threadId) return;
            await apiRequest("POST", `/api/pages/${encodeURIComponent(pageId)}/comments/${encodeURIComponent(threadId)}/resolve`, {
                resolved,
            });
            scheduleCommentsRefresh(20);
        }

        async function sendThreadReply(threadId, textarea) {
            const body = String(textarea?.value || "").trim();
            if (!pageId || !threadId || !body) return;
            await apiRequest("POST", `/api/pages/${encodeURIComponent(pageId)}/comments/${encodeURIComponent(threadId)}/replies`, {
                body,
                author: "viewer",
            });
            textarea.value = "";
            scheduleCommentsRefresh(20);
        }

        function renderCommentThread(thread) {
            const meta = parseCommentSelectionLabel(thread?.selectionLabel || "");
            const anchor = resolveThreadAnchor(thread);
            const messages = Array.isArray(thread?.messages) ? thread.messages : [];
            const first = messages[0] || {};
            const card = document.createElement("article");
            card.className = "wl-thread";
            if (thread?.resolved) card.classList.add("is-resolved");
            if (commentTarget && anchor && commentTarget.anchor === anchor) card.classList.add("is-focused");

            const row = document.createElement("div");
            row.className = "wl-thread__row";
            const avatar = document.createElement("div");
            avatar.className = "wl-thread__avatar";
            avatar.textContent = initialsFromName(first.author || "viewer");
            const bubble = document.createElement("div");
            bubble.className = "wl-thread__bubble";
            const author = document.createElement("div");
            author.className = "wl-thread__author";
            author.textContent = first.author || "viewer";
            const metaNode = document.createElement("div");
            metaNode.className = "wl-thread__meta";
            metaNode.textContent = formatTimestamp(first.createdAt || thread.updatedAt || thread.createdAt);
            const body = document.createElement("div");
            body.className = "wl-thread__body";
            body.textContent = first.body || "Комментарий";
            bubble.appendChild(author);
            bubble.appendChild(metaNode);
            bubble.appendChild(body);
            if (meta.preview || meta.blockPreview) {
                const selection = document.createElement("div");
                selection.className = "wl-thread__selection";
                selection.textContent = meta.preview || meta.blockPreview;
                bubble.appendChild(selection);
            }
            row.appendChild(avatar);
            row.appendChild(bubble);
            card.appendChild(row);

            if (messages.length > 1) {
                const replies = document.createElement("div");
                replies.className = "wl-thread__replies";
                messages.slice(1).forEach((message) => {
                    const replyRow = document.createElement("div");
                    replyRow.className = "wl-thread__reply-row";
                    const replyAvatar = document.createElement("div");
                    replyAvatar.className = "wl-thread__reply-avatar";
                    replyAvatar.textContent = initialsFromName(message.author || "viewer");
                    const replyBubble = document.createElement("div");
                    replyBubble.className = "wl-thread__reply-bubble";
                    const replyAuthor = document.createElement("div");
                    replyAuthor.className = "wl-thread__author";
                    replyAuthor.textContent = message.author || "viewer";
                    const replyMeta = document.createElement("div");
                    replyMeta.className = "wl-thread__meta";
                    replyMeta.textContent = formatTimestamp(message.createdAt);
                    const replyBody = document.createElement("div");
                    replyBody.className = "wl-thread__body";
                    replyBody.textContent = message.body || "";
                    replyBubble.appendChild(replyAuthor);
                    replyBubble.appendChild(replyMeta);
                    replyBubble.appendChild(replyBody);
                    replyRow.appendChild(replyAvatar);
                    replyRow.appendChild(replyBubble);
                    replies.appendChild(replyRow);
                });
                card.appendChild(replies);
            }

            const actions = document.createElement("div");
            actions.className = "wl-thread__actions";
            const likeButton = document.createElement("button");
            likeButton.type = "button";
            likeButton.textContent = `♥ ${Number(thread?.likeCount || 0)}`;
            likeButton.addEventListener("click", async (event) => {
                event.stopPropagation();
                await toggleThreadLike(thread.threadId || "");
            });
            const replyButton = document.createElement("button");
            replyButton.type = "button";
            replyButton.textContent = "Ответить";
            const resolveButton = document.createElement("button");
            resolveButton.type = "button";
            resolveButton.textContent = thread?.resolved ? "Открыть" : "Решить";
            resolveButton.addEventListener("click", async (event) => {
                event.stopPropagation();
                await toggleThreadResolved(thread.threadId || "", !Boolean(thread?.resolved));
            });
            actions.appendChild(likeButton);
            actions.appendChild(replyButton);
            actions.appendChild(resolveButton);
            card.appendChild(actions);

            const replyWrap = document.createElement("div");
            replyWrap.className = "wl-thread__reply";
            replyWrap.hidden = true;
            const replyInput = document.createElement("textarea");
            replyInput.placeholder = "Ответ";
            const replySend = document.createElement("button");
            replySend.type = "button";
            replySend.className = "wl-thread__reply-send";
            replySend.textContent = "Отправить";
            replySend.addEventListener("click", async (event) => {
                event.stopPropagation();
                await sendThreadReply(thread.threadId || "", replyInput);
            });
            replyWrap.appendChild(replyInput);
            replyWrap.appendChild(replySend);
            replyButton.addEventListener("click", (event) => {
                event.stopPropagation();
                replyWrap.hidden = !replyWrap.hidden;
                if (!replyWrap.hidden) replyInput.focus();
            });
            card.appendChild(replyWrap);

            card.addEventListener("click", () => {
                const block = findBlockByAnchor(anchor);
                if (block) {
                    setCommentTarget(buildCommentTarget(block));
                    block.scrollIntoView({ behavior: "smooth", block: "center" });
                }
            });
            return card;
        }

        function renderComments() {
            commentsList.innerHTML = "";
            if (!pageId) {
                const empty = document.createElement("div");
                empty.className = "wl-comments__empty";
                empty.textContent = "Сохрани страницу, и обсуждения появятся здесь.";
                commentsList.appendChild(empty);
                refreshCommentComposerState();
                return;
            }
            if (commentsLoading) {
                const loading = document.createElement("div");
                loading.className = "wl-comments__empty";
                loading.textContent = "Загружаю комментарии…";
                commentsList.appendChild(loading);
                refreshCommentComposerState();
                return;
            }
            const sortedThreads = [...commentThreads].sort((left, right) => {
                const leftAnchor = resolveThreadAnchor(left);
                const rightAnchor = resolveThreadAnchor(right);
                const leftFocused = commentTarget && leftAnchor === commentTarget.anchor ? 1 : 0;
                const rightFocused = commentTarget && rightAnchor === commentTarget.anchor ? 1 : 0;
                if (leftFocused !== rightFocused) return rightFocused - leftFocused;
                if (Boolean(left?.resolved) !== Boolean(right?.resolved)) return Number(left?.resolved) - Number(right?.resolved);
                return String(right?.updatedAt || right?.createdAt || "").localeCompare(String(left?.updatedAt || left?.createdAt || ""));
            });
            if (!sortedThreads.length) {
                const empty = document.createElement("div");
                empty.className = "wl-comments__empty";
                empty.textContent = commentsLoaded ? "Пока без обсуждений." : "Комментарии появятся здесь.";
                commentsList.appendChild(empty);
                refreshCommentComposerState();
                return;
            }
            sortedThreads.forEach((thread) => commentsList.appendChild(renderCommentThread(thread)));
            refreshCommentComposerState();
        }

        function getCurrentBlock() {
            if (selectedObject) return closestBlock(selectedObject);
            const selection = window.getSelection();
            if (selection && selection.rangeCount > 0) {
                const block = closestBlock(selection.getRangeAt(0).startContainer);
                if (block) return block;
            }
            return getTopBlocks()[0] || null;
        }

        function getCurrentBlockIndex() {
            const block = getCurrentBlock();
            return Math.max(0, getTopBlocks().indexOf(block));
        }

        function rememberSelection() {
            const selection = window.getSelection();
            if (!selection || selection.rangeCount === 0) return;
            const range = selection.getRangeAt(0);
            if (!editor.contains(range.startContainer) || !editor.contains(range.endContainer)) return;
            lastRange = range.cloneRange();
        }

        function queueRememberSelection() {
            if (selectionTimer !== null) window.clearTimeout(selectionTimer);
            selectionTimer = window.setTimeout(() => {
                rememberSelection();
                queueToolbarRefresh();
                queueSlashRefresh();
                refreshSelectionBubble();
            }, 0);
        }

        function restoreSelection() {
            if (!lastRange) return false;
            try {
                if (!document.contains(lastRange.startContainer) || !document.contains(lastRange.endContainer)) return false;
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(lastRange);
                return true;
            } catch (error) {
                return false;
            }
        }

        function hideSelectionBubble() {
            selectionBubble.style.display = "none";
        }

        function selectBlockContents(block) {
            if (!block) return;
            const body = block.querySelector(".wl-line__body") || block;
            const range = document.createRange();
            range.selectNodeContents(body);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            lastRange = range.cloneRange();
            queueToolbarRefresh();
            refreshSelectionBubble();
        }

        function refreshSelectionBubble() {
            const selection = window.getSelection();
            if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
                hideSelectionBubble();
                return;
            }
            const range = selection.getRangeAt(0);
            if (!editor.contains(range.commonAncestorContainer)) {
                hideSelectionBubble();
                return;
            }
            const rect = range.getBoundingClientRect();
            if (!rect || (!rect.width && !rect.height)) {
                hideSelectionBubble();
                return;
            }
            selectionBubble.style.left = `${Math.min(Math.max(12, rect.left + rect.width / 2 - 70), window.innerWidth - 160)}px`;
            selectionBubble.style.top = `${Math.max(12, rect.top - 52)}px`;
            selectionBubble.style.display = "flex";
        }

        function openCommentComposerForCurrentSelection() {
            const selection = window.getSelection();
            if (!selection || selection.rangeCount === 0) return;
            const block = closestBlock(selection.getRangeAt(0).startContainer);
            if (!block) return;
            const selectedText = currentSelectionText();
            setCommentTarget(buildCommentTarget(block, selectedText));
            commentInput.focus();
            hideSelectionBubble();
        }

        function placeCaretAtBlock(index = 0, placement = "end", scrollIntoView = false) {
            const blocks = getTopBlocks();
            if (!blocks.length) return;
            const block = blocks[Math.max(0, Math.min(index, blocks.length - 1))];
            const contentRoot = block.querySelector(".wl-line__body") || block;
            editor.focus();
            const range = document.createRange();
            range.selectNodeContents(contentRoot);
            range.collapse(placement !== "start");
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            lastRange = range.cloneRange();
            if (scrollIntoView) block.scrollIntoView({ behavior: "smooth", block: "center" });
            queueToolbarRefresh();
            hideSelectionBubble();
        }

        function placeCaretAtEnd(scrollIntoView = false) {
            const blocks = getTopBlocks();
            if (!blocks.length) return;
            placeCaretAtBlock(blocks.length - 1, "end", scrollIntoView);
        }

        function moveCaretToBlockNode(block, placement = "start") {
            if (!block) return;
            const blocks = getTopBlocks();
            const index = blocks.indexOf(block);
            if (index >= 0) placeCaretAtBlock(index, placement, true);
        }

        function queueDraftStore() {
            if (storeTimer !== null) window.clearTimeout(storeTimer);
            storeTimer = window.setTimeout(() => {
                const raw = serializeDocument();
                storeDraft(raw);
                setHiddenValue(raw);
            }, 220);
        }

        function updateHistoryButtons() {
            undoButton.disabled = historyIndex <= 0;
            redoButton.disabled = historyIndex >= historyStack.length - 1;
        }

        function pushHistory(raw, force = false) {
            if (applyingHistory) return;
            const nextRaw = String(raw || "");
            if (!force && historyStack[historyIndex] === nextRaw) {
                updateHistoryButtons();
                return;
            }
            historyStack = historyStack.slice(0, historyIndex + 1);
            historyStack.push(nextRaw);
            if (historyStack.length > 140) historyStack.shift();
            historyIndex = historyStack.length - 1;
            updateHistoryButtons();
        }

        function queueHistorySnapshot() {
            if (historyTimer !== null) window.clearTimeout(historyTimer);
            historyTimer = window.setTimeout(() => {
                const raw = serializeDocument();
                storeDraft(raw);
                setHiddenValue(raw);
                pushHistory(raw);
            }, 480);
        }

        function restoreHistory(index) {
            if (index < 0 || index >= historyStack.length) return;
            applyingHistory = true;
            historyIndex = index;
            const raw = historyStack[historyIndex];
            storeDraft(raw);
            setHiddenValue(raw);
            renderRaw(raw);
            window.requestAnimationFrame(() => {
                placeCaretAtEnd(false);
                applyingHistory = false;
                updateHistoryButtons();
            });
        }

        function undoHistory() {
            hideContextMenu();
            hideSlashMenu();
            const currentRaw = serializeDocument();
            if (historyStack[historyIndex] !== currentRaw) pushHistory(currentRaw, true);
            if (historyIndex > 0) restoreHistory(historyIndex - 1);
        }

        function redoHistory() {
            hideContextMenu();
            hideSlashMenu();
            if (historyIndex < historyStack.length - 1) restoreHistory(historyIndex + 1);
        }

        function replaceTokenAtIndex(raw, targetIndex, replacement) {
            let currentIndex = 0;
            tokenRegex.lastIndex = 0;
            return raw.replace(tokenRegex, (match) => {
                if (currentIndex === targetIndex) {
                    currentIndex += 1;
                    return replacement;
                }
                currentIndex += 1;
                return match;
            });
        }

        function updateSelectedImageMeta(patch) {
            if (!selectedObject || !selectedObject.classList.contains("wl-attachment--image")) return;
            const raw = selectedObject.dataset.raw || "";
            const match = raw.match(/\[\[WL_ATTACHMENT:([^\]]+)\]\]/);
            if (!match) return;
            const meta = decodeAttachmentPayload(match[1]);
            const nextMeta = {
                ...meta,
                ...patch,
            };
            nextMeta.width = Math.max(180, Math.min(Number(nextMeta.width || 420), 720));
            nextMeta.opacity = Math.max(.2, Math.min(Number(nextMeta.opacity || 1), 1));
            selectedObject.dataset.raw = buildAttachmentSnippet(nextMeta);
            applyAttachmentPresentation(selectedObject, nextMeta);
            queueDraftStore();
            queueHistorySnapshot();
        }

        function renderAndStore(raw, focusBlockIndex = null, placement = "end", scrollIntoView = false, pushToHistory = true) {
            const nextRaw = String(raw || "");
            storeDraft(nextRaw);
            setHiddenValue(nextRaw);
            renderRaw(nextRaw);
            if (pushToHistory) pushHistory(nextRaw);
            window.requestAnimationFrame(() => {
                if (focusBlockIndex !== null) placeCaretAtBlock(focusBlockIndex, placement, scrollIntoView);
                else placeCaretAtEnd(scrollIntoView);
            });
        }

        function refreshToolbarState() {
            const block = getCurrentBlock();
            if (block && block.dataset.kind && block.dataset.kind !== "table" && block.dataset.kind !== "code") {
                blockStyleSelect.value = block.dataset.kind;
                const align = block.dataset.align || "left";
                Object.entries(alignButtons).forEach(([key, button]) => button.classList.toggle("is-active", key === align));
            } else {
                blockStyleSelect.value = "line";
                Object.values(alignButtons).forEach((button) => button.classList.remove("is-active"));
            }
            Object.entries(formatButtons).forEach(([command, button]) => {
                try { button.classList.toggle("is-active", document.queryCommandState(command)); }
                catch (error) { button.classList.remove("is-active"); }
            });
            if (!(selectedObject && selectedObject.classList.contains("wl-attachment--image"))) {
                imageWidthInput.style.display = "none";
                imageOpacityInput.style.display = "none";
            }
        }

        function queueToolbarRefresh() {
            if (toolbarTimer !== null) window.clearTimeout(toolbarTimer);
            toolbarTimer = window.setTimeout(refreshToolbarState, 0);
        }

        function headingLevel(kind) {
            if (kind === "heading1") return 1;
            if (kind === "heading2") return 2;
            return 3;
        }

        function refreshOutline() {
            const headings = Array.from(editor.querySelectorAll('.wl-line[data-kind="heading1"], .wl-line[data-kind="heading2"], .wl-line[data-kind="heading3"]'));
            if (!headings.length) {
                outlineList.innerHTML = '<div class="wl-outline__empty"># H1 H2 H3</div>';
                return;
            }
            outlineList.innerHTML = "";
            headings.forEach((heading, index) => {
                heading.id = `wl-heading-${index + 1}`;
                const item = document.createElement("button");
                item.type = "button";
                item.className = `wl-outline__item level-${headingLevel(heading.dataset.kind || "heading1")}`;
                item.textContent = blockPlainText(heading) || `H${headingLevel(heading.dataset.kind || "heading1")}`;
                item.addEventListener("click", () => moveCaretToBlockNode(heading, "start"));
                outlineList.appendChild(item);
            });
        }

        function queueOutlineRefresh() {
            if (outlineTimer !== null) window.clearTimeout(outlineTimer);
            outlineTimer = window.setTimeout(refreshOutline, 70);
        }

        function runEditorCommand(command) {
            const blockIndex = getCurrentBlockIndex();
            editor.focus();
            if (!restoreSelection()) placeCaretAtBlock(blockIndex, "end");
            document.execCommand(command, false, null);
            window.setTimeout(() => {
                const raw = serializeDocument();
                storeDraft(raw);
                setHiddenValue(raw);
                pushHistory(raw);
                queueRememberSelection();
                queueOutlineRefresh();
                queueFrameHeight();
            }, 0);
        }

        function applyBlockStyle(kind) {
            const block = getCurrentBlock();
            if (!block || block.dataset.kind === "table" || block.dataset.kind === "code") return;
            block.dataset.kind = kind;
            queueDraftStore();
            queueHistorySnapshot();
            queueToolbarRefresh();
            queueOutlineRefresh();
            queueFrameHeight();
        }

        function applyAlignment(align) {
            const block = getCurrentBlock();
            if (!block || block.dataset.kind === "table" || block.dataset.kind === "code") return;
            applyAlignmentToBlock(block, align);
            queueDraftStore();
            queueHistorySnapshot();
            queueToolbarRefresh();
        }

        function stripTrailingSlashFromBlock(block) {
            if (!block || block.dataset.kind === "table" || block.dataset.kind === "code") return;
            const cleaned = blockPlainText(block).replace(/(^|\s)\/[^\s/]*$/, "$1").trimEnd();
            const body = block.querySelector(".wl-line__body") || block;
            body.innerHTML = "";
            if (cleaned) body.appendChild(document.createTextNode(cleaned));
            else body.appendChild(document.createElement("br"));
        }

        function insertSnippet(snippet) {
            if (!snippet) return;
            const blockIndex = getCurrentBlockIndex();
            if (selectedObject && selectedObject.dataset.tokenIndex !== undefined) {
                const nextRaw = replaceTokenAtIndex(serializeDocument(), Number(selectedObject.dataset.tokenIndex), snippet);
                clearSelectedObject();
                renderAndStore(nextRaw, blockIndex, "end", false, true);
                hideContextMenu();
                return;
            }
            editor.focus();
            if (!restoreSelection()) placeCaretAtBlock(blockIndex, "end");
            document.execCommand("insertText", false, snippet);
            renderAndStore(serializeDocument(), blockIndex, "end", false, true);
            hideContextMenu();
        }

        function insertCodeBlock() {
            insertSnippet("```\ncode\n```");
        }

        function readFileAsDataUrl(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(String(reader.result || ""));
                reader.onerror = () => reject(reader.error || new Error("file_read_error"));
                reader.readAsDataURL(file);
            });
        }

        async function buildAttachmentSnippetFromFile(file) {
            const src = await readFileAsDataUrl(file);
            return buildAttachmentSnippet({
                name: file.name || "Вложение",
                mime: file.type || "application/octet-stream",
                src,
                width: file.type.startsWith("image/") ? 420 : 0,
                opacity: 1,
            });
        }

        async function insertFiles(files) {
            const items = Array.from(files || []);
            if (!items.length) return;
            const snippets = [];
            for (const file of items) snippets.push(await buildAttachmentSnippetFromFile(file));
            insertSnippet(snippets.join("\n"));
        }

        function rangeFromPoint(x, y) {
            if (document.caretRangeFromPoint) return document.caretRangeFromPoint(x, y);
            if (document.caretPositionFromPoint) {
                const position = document.caretPositionFromPoint(x, y);
                if (!position) return null;
                const range = document.createRange();
                range.setStart(position.offsetNode, position.offset);
                range.collapse(true);
                return range;
            }
            return null;
        }

        async function insertDroppedFiles(files, event) {
            const range = rangeFromPoint(event.clientX, event.clientY);
            if (range) {
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                lastRange = range.cloneRange();
            }
            await insertFiles(files);
        }

        function getSlashState() {
            const selection = window.getSelection();
            if (!selection || selection.rangeCount === 0 || !selection.isCollapsed) return null;
            const range = selection.getRangeAt(0);
            if (!editor.contains(range.startContainer)) return null;
            const block = closestBlock(range.startContainer);
            if (!block || block.dataset.kind === "table" || block.dataset.kind === "code") return null;
            const probe = range.cloneRange();
            probe.selectNodeContents(block.querySelector(".wl-line__body") || block);
            probe.setEnd(range.endContainer, range.endOffset);
            const textBefore = probe.toString();
            const match = textBefore.match(/(?:^|\s)\/([^\s/]*)$/);
            if (!match) return null;
            return {
                block,
                query: match[1].toLowerCase(),
                rect: range.getBoundingClientRect(),
            };
        }

        function renderSlashMenu(items, state) {
            if (!items.length) {
                hideSlashMenu();
                return;
            }
            slashMenu.innerHTML = "";
            items.forEach((item) => {
                const button = document.createElement("button");
                button.type = "button";
                button.innerHTML = `${item.label}<span class="wl-slash-menu__meta">${item.meta}</span>`;
                button.addEventListener("click", () => {
                    stripTrailingSlashFromBlock(state.block);
                    rememberSelection();
                    item.run();
                    hideSlashMenu();
                });
                slashMenu.appendChild(button);
            });
            slashMenu.style.left = `${Math.min(Math.max(12, state.rect.left), window.innerWidth - 240)}px`;
            slashMenu.style.top = `${Math.min(state.rect.bottom + 10, window.innerHeight - 240)}px`;
            slashMenu.style.display = "block";
        }

        function refreshSlashMenu() {
            const state = getSlashState();
            if (!state) {
                hideSlashMenu();
                return;
            }
            const items = slashActions.filter((item) => {
                if (!state.query) return true;
                const haystack = `${item.id} ${item.label} ${item.meta}`.toLowerCase();
                return haystack.includes(state.query);
            });
            renderSlashMenu(items, state);
        }

        function queueSlashRefresh() {
            window.setTimeout(refreshSlashMenu, 0);
        }

        editor.addEventListener("focus", () => {
            queueToolbarRefresh();
            queueOutlineRefresh();
        });

        editor.addEventListener("click", (event) => {
            const handleButton = event.target.closest(".wl-block-handle");
            if (handleButton) {
                event.preventDefault();
                event.stopPropagation();
                const block = closestBlock(handleButton);
                if (block) {
                    setCommentTarget(buildCommentTarget(block));
                    selectBlockContents(block);
                }
                return;
            }
            const commentButton = event.target.closest(".wl-block-comment");
            if (commentButton) {
                event.preventDefault();
                event.stopPropagation();
                const block = closestBlock(commentButton);
                if (block) {
                    setCommentTarget(buildCommentTarget(block, currentSelectionText()));
                    commentInput.focus();
                }
                return;
            }
            const objectNode = closestObjectNode(event.target);
            if (objectNode) {
                event.preventDefault();
                event.stopPropagation();
                selectObject(objectNode);
                openPicker();
                hideSelectionBubble();
                return;
            }
            clearSelectedObject();
            hideContextMenu();
            rememberSelection();
            queueToolbarRefresh();
            queueSlashRefresh();
            refreshSelectionBubble();
        });

        editor.addEventListener("keydown", (event) => {
            const modifier = event.ctrlKey || event.metaKey;
            if (modifier && event.key.toLowerCase() === "z" && !event.shiftKey) {
                event.preventDefault();
                undoHistory();
                return;
            }
            if ((modifier && event.key.toLowerCase() === "y") || (modifier && event.shiftKey && event.key.toLowerCase() === "z")) {
                event.preventDefault();
                redoHistory();
                return;
            }
            if (event.altKey && !modifier && event.key === "1") {
                event.preventDefault();
                applyBlockStyle("heading1");
                return;
            }
            if (event.altKey && !modifier && event.key === "2") {
                event.preventDefault();
                applyBlockStyle("heading2");
                return;
            }
            if (event.altKey && !modifier && event.key === "3") {
                event.preventDefault();
                applyBlockStyle("heading3");
                return;
            }
            if (selectedObject && (event.key === "Backspace" || event.key === "Delete")) {
                event.preventDefault();
                const blockIndex = getCurrentBlockIndex();
                selectedObject.remove();
                clearSelectedObject();
                renderAndStore(serializeDocument(), blockIndex, "end", false, true);
                return;
            }
            if (event.key === "Escape") {
                hideContextMenu();
                hideSlashMenu();
                hideSelectionBubble();
            }
            queueRememberSelection();
        });

        editor.addEventListener("input", () => {
            if (isRendering) return;
            queueDraftStore();
            queueHistorySnapshot();
            queueRememberSelection();
            queueOutlineRefresh();
            queueFrameHeight();
            updateCommentBadges();
        });

        editor.addEventListener("paste", async (event) => {
            const clipboard = event.clipboardData || window.clipboardData;
            const files = clipboard ? Array.from(clipboard.files || []) : [];
            if (files.length) {
                event.preventDefault();
                await insertFiles(files);
                return;
            }
            event.preventDefault();
            const text = clipboard ? clipboard.getData("text/plain") : "";
            document.execCommand("insertText", false, text);
            queueDraftStore();
            queueHistorySnapshot();
            queueRememberSelection();
            queueOutlineRefresh();
        });

        editor.addEventListener("mouseup", () => {
            rememberSelection();
            queueToolbarRefresh();
            queueSlashRefresh();
            refreshSelectionBubble();
        });

        editor.addEventListener("keyup", () => {
            queueRememberSelection();
            queueSlashRefresh();
            refreshSelectionBubble();
        });

        editor.addEventListener("dragstart", (event) => {
            const objectNode = closestObjectNode(event.target);
            if (!objectNode) return;
            dragSourceNode = objectNode;
            dragRaw = objectNode.dataset.raw || "";
            event.dataTransfer.setData("text/plain", dragRaw);
            event.dataTransfer.effectAllowed = "move";
        });

        editor.addEventListener("dragover", (event) => {
            if ((event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files.length) || dragRaw) event.preventDefault();
        });

        editor.addEventListener("drop", async (event) => {
            const fileList = event.dataTransfer ? event.dataTransfer.files : null;
            if (fileList && fileList.length) {
                event.preventDefault();
                await insertDroppedFiles(fileList, event);
                return;
            }
            if (!dragRaw) return;
            event.preventDefault();
            const range = rangeFromPoint(event.clientX, event.clientY);
            if (dragSourceNode) dragSourceNode.remove();
            if (range) {
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                lastRange = range.cloneRange();
            } else {
                placeCaretAtEnd(false);
            }
            document.execCommand("insertText", false, dragRaw);
            dragRaw = "";
            dragSourceNode = null;
            renderAndStore(serializeDocument(), getCurrentBlockIndex(), "end", false, true);
        });

        editor.addEventListener("contextmenu", (event) => {
            event.preventDefault();
            const objectNode = closestObjectNode(event.target);
            if (objectNode) {
                selectObject(objectNode);
            } else {
                clearSelectedObject();
                const range = rangeFromPoint(event.clientX, event.clientY);
                if (range) {
                    const selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                    lastRange = range.cloneRange();
                } else {
                    rememberSelection();
                }
            }
            hideSlashMenu();
            hideSelectionBubble();
            showContextMenu(event.clientX, event.clientY);
        });

        undoButton.addEventListener("click", () => undoHistory());
        redoButton.addEventListener("click", () => redoHistory());
        document.getElementById("wl-insert-object").addEventListener("click", () => openPicker());
        document.getElementById("wl-insert-code").addEventListener("click", () => insertCodeBlock());
        document.getElementById("wl-insert-quote").addEventListener("click", () => applyBlockStyle("callout"));
        document.getElementById("wl-insert-photo").addEventListener("click", () => openImagePicker());
        Object.entries(formatButtons).forEach(([command, button]) => button.addEventListener("click", () => runEditorCommand(command)));
        Object.entries(alignButtons).forEach(([align, button]) => button.addEventListener("click", () => applyAlignment(align)));
        blockStyleSelect.addEventListener("change", () => applyBlockStyle(blockStyleSelect.value));
        commentInput.addEventListener("input", refreshCommentComposerState);
        commentSubmit.addEventListener("click", async () => {
            await submitComment();
        });
        bubbleBoldButton.addEventListener("click", () => {
            runEditorCommand("bold");
            hideSelectionBubble();
        });
        bubbleItalicButton.addEventListener("click", () => {
            runEditorCommand("italic");
            hideSelectionBubble();
        });
        bubbleQuoteButton.addEventListener("click", () => {
            applyBlockStyle("callout");
            hideSelectionBubble();
        });
        bubbleCommentButton.addEventListener("click", () => openCommentComposerForCurrentSelection());
        imageWidthInput.addEventListener("input", () => updateSelectedImageMeta({ width: Number(imageWidthInput.value) }));
        imageOpacityInput.addEventListener("input", () => updateSelectedImageMeta({ opacity: Number(imageOpacityInput.value) / 100 }));
        fileInput.addEventListener("change", async () => {
            await insertFiles(fileInput.files);
            fileInput.value = "";
            fileInput.removeAttribute("accept");
        });
        contextOpenButton.addEventListener("click", () => {
            openPicker();
            hideContextMenu();
        });
        contextInsertButton.addEventListener("click", () => {
            ensureActiveSnippetState();
            if (activeSnippet) insertSnippet(activeSnippet);
        });
        document.addEventListener("click", (event) => {
            if (!contextMenu.contains(event.target)) hideContextMenu();
            if (!slashMenu.contains(event.target)) hideSlashMenu();
            if (!selectionBubble.contains(event.target) && !editor.contains(event.target)) hideSelectionBubble();
        }, true);
        document.addEventListener("scroll", () => {
            hideContextMenu();
            hideSlashMenu();
            hideSelectionBubble();
        }, true);
        window.addEventListener("resize", () => {
            queueFrameHeight();
            refreshSelectionBubble();
        });
        parentWindow.__wikiliveInsertSnippet = insertSnippet;
        parentWindow.__wikiliveSyncEditor = syncHiddenState;
        parentWindow.__wikiliveSetActiveSnippet = (snippet, hint) => {
            activeSnippet = snippet || "";
            activeHint = hint || "";
            ensureActiveSnippetState();
            refreshContextMenu();
        };
        attachActionSync();
        window.setTimeout(attachActionSync, 300);
        window.setTimeout(attachActionSync, 1200);
        ensureActiveSnippetState();
        const initialRaw = normalizeRaw(loadDraft());
        renderRaw(initialRaw);
        storeDraft(initialRaw);
        setHiddenValue(initialRaw);
        pushHistory(initialRaw, true);
        setCommentTarget(null);
        scheduleCommentsRefresh(0);
        updateHistoryButtons();
        window.requestAnimationFrame(() => {
            placeCaretAtEnd(false);
            queueOutlineRefresh();
            queueFrameHeight();
        });
        </script>
    """
    html = html.replace("__WIKILIVE_LOOKUP__", json.dumps(insert_lookup, ensure_ascii=False))
    html = html.replace("__WIKILIVE_DRAFT_KEY__", json.dumps(draft_key))
    html = html.replace("__WIKILIVE_PAGE_BREAK_MARKER__", json.dumps(PAGE_BREAK_MARKER))
    html = html.replace("__WIKILIVE_ACTIVE_SNIPPET__", json.dumps(active_snippet))
    html = html.replace("__WIKILIVE_ACTIVE_HINT__", json.dumps(active_hint))
    html = html.replace("__WIKILIVE_PAGE_ID__", json.dumps(page_id or ""))
    html = html.replace("__WIKILIVE_BACKEND_URL__", json.dumps(backend_url))
    components.html(html, height=1180)

