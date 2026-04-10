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
) -> None:
    html = r"""
        <style>
        html, body { margin: 0; padding: 0; background: transparent; color: #111827; font-family: 'Manrope', sans-serif; }
        .wikilive-rich-root { min-height: 78vh; padding: 0.2rem 0 1rem; }
        .wl-toolbar { position: sticky; top: 0; z-index: 50; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.55rem; padding: 0.25rem 0 0.95rem; background: linear-gradient(180deg, rgba(246,247,249,.98), rgba(246,247,249,.90), rgba(246,247,249,0)); backdrop-filter: blur(10px); }
        .wl-toolbar__group { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem; }
        .wl-toolbar__sep { width: 1px; height: 1.85rem; background: rgba(17,24,39,.10); margin: 0 0.08rem; }
        .wl-toolbar button, .wl-toolbar select, .wl-toolbar input[type="range"] { min-height: 2.15rem; border-radius: 12px; border: 1px solid rgba(227,6,19,.18); background: rgba(255,255,255,.98); color: #111827; box-shadow: 0 1px 2px rgba(17,24,39,.04); transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease; }
        .wl-toolbar button, .wl-toolbar select { padding: 0.45rem 0.72rem; font: 700 .84rem/1.1 Manrope, sans-serif; }
        .wl-toolbar button:hover, .wl-toolbar select:hover { transform: translateY(-1px); border-color: rgba(227,6,19,.42); box-shadow: 0 10px 20px rgba(17,24,39,.06); }
        .wl-toolbar button.is-active { background: rgba(227,6,19,.08); color: #bf0812; border-color: rgba(227,6,19,.48); }
        .wl-toolbar__icon { width: 2.3rem; padding: 0; }
        .wl-toolbar__meta { color: #6b7280; font: 700 .8rem/1.2 Manrope, sans-serif; white-space: nowrap; }
        #wl-image-width { width: 8rem; display: none; accent-color: #e30613; }
        .wl-pages { display: flex; flex-direction: column; gap: 1.3rem; }
        .wl-page { max-width: 950px; margin: 0 auto; padding: 0.95rem 1.35rem 1.25rem; border-radius: 24px; background: rgba(255,255,255,.98); box-shadow: 0 16px 36px rgba(17,24,39,.06); transition: transform .2s ease, box-shadow .2s ease; }
        .wl-page.is-active { transform: translateY(-1px); box-shadow: 0 24px 44px rgba(17,24,39,.10); }
        .wl-page__number { display: inline-flex; align-items: center; margin-bottom: 0.9rem; padding: 0.28rem 0.64rem; border-radius: 999px; background: rgba(243,244,246,.96); color: #6b7280; font: 700 .77rem/1 Manrope, sans-serif; }
        .wl-page__content { min-height: 760px; outline: none; color: #111827; caret-color: #e30613; font: 500 17px/1.85 Manrope, sans-serif; word-break: break-word; }
        .wl-page__content:empty::before { content: attr(data-placeholder); color: #9ca3af; }
        .wl-line { min-height: 1.85em; white-space: pre-wrap; }
        .wl-line[data-kind="heading1"] { font: 800 2rem/1.25 'Onest', sans-serif; letter-spacing: -0.03em; margin: 0.08rem 0 0.32rem; }
        .wl-line[data-kind="heading2"] { font: 800 1.45rem/1.35 'Onest', sans-serif; letter-spacing: -0.02em; margin: 0.06rem 0 0.2rem; }
        .wl-line[data-kind="heading3"] { font: 700 1.12rem/1.5 'Onest', sans-serif; letter-spacing: -0.01em; margin: 0.03rem 0 0.08rem; }
        .wl-line[data-kind="callout"] { padding: 0.4rem 0.85rem; margin: 0.18rem 0; border-left: 3px solid #e30613; border-radius: 0 14px 14px 0; background: rgba(227,6,19,.05); }
        .wl-inline-mark--underline { text-decoration: underline; }
        .wl-inline-mark--strike { text-decoration: line-through; color: #6b7280; }
        .wl-object, .wl-attachment { display: inline-flex; align-items: center; gap: 0.4rem; margin: 0 0.14rem; border: 1px solid rgba(17,24,39,.10); background: rgba(255,255,255,.98); box-shadow: 0 8px 20px rgba(17,24,39,.06); cursor: pointer; transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease; vertical-align: middle; }
        .wl-object:hover, .wl-object.is-selected, .wl-attachment:hover, .wl-attachment.is-selected { transform: translateY(-1px); border-color: rgba(227,6,19,.42); box-shadow: 0 14px 30px rgba(227,6,19,.10); }
        .wl-object { padding: 0.22rem 0.55rem; border-radius: 999px; }
        .wl-object__field { color: #bf0812; font-size: .74rem; font-weight: 800; }
        .wl-object__value { color: #4b5563; font-size: .8rem; }
        .wl-attachment { border-radius: 18px; }
        .wl-attachment--image { flex-direction: column; align-items: stretch; padding: 0.46rem; width: fit-content; max-width: 460px; }
        .wl-attachment--image img { display: block; width: 100%; max-height: 360px; object-fit: cover; border-radius: 14px; background: #f3f4f6; }
        .wl-attachment__caption, .wl-attachment__meta { display: flex; align-items: center; gap: 0.48rem; flex-wrap: wrap; padding: 0 0.1rem; }
        .wl-attachment__name { color: #111827; font-size: .82rem; font-weight: 700; }
        .wl-attachment__type { color: #6b7280; font-size: .74rem; font-weight: 700; }
        .wl-attachment--file { padding: 0.45rem 0.7rem; border-radius: 999px; }
        .wl-attachment__dot { width: .5rem; height: .5rem; border-radius: 999px; background: #e30613; flex: none; }
        .wl-table-block { margin: 0.55rem 0 0.85rem; overflow: auto; border-radius: 18px; border: 1px solid rgba(17,24,39,.08); background: #ffffff; }
        .wl-table { width: 100%; border-collapse: collapse; font-size: .93rem; }
        .wl-table th, .wl-table td { padding: 0.68rem 0.76rem; border-bottom: 1px solid rgba(17,24,39,.06); text-align: left; vertical-align: top; }
        .wl-table th { background: rgba(243,244,246,.92); font-weight: 800; color: #374151; }
        .wl-table .wl-attachment--image { max-width: 220px; }
        .wl-context-menu { position: fixed; z-index: 99999; display: none; min-width: 220px; padding: 8px; border-radius: 16px; border: 1px solid rgba(17,24,39,.08); background: rgba(255,255,255,.98); box-shadow: 0 18px 40px rgba(17,24,39,.14); }
        .wl-context-menu button { width: 100%; border: 1px solid rgba(227,6,19,.22); background: #ffffff; color: #111827; border-radius: 12px; padding: 0.74rem 0.85rem; text-align: left; font: 800 .84rem/1.2 Manrope, sans-serif; cursor: pointer; }
        .wl-context-menu button + button { margin-top: 0.35rem; }
        .wl-context-menu__hint { margin-top: 0.45rem; padding: 0 0.18rem; color: #6b7280; font: 600 .74rem/1.45 Manrope, sans-serif; }
        @media (max-width: 900px) {
            .wl-page { padding: 0.72rem 0.9rem 1rem; border-radius: 18px; }
            .wl-page__content { min-height: 540px; font-size: 16px; }
        }
        </style>
        <div class="wikilive-rich-root">
            <div class="wl-toolbar">
                <div class="wl-toolbar__group">
                    <button id="wl-undo" class="wl-toolbar__icon" type="button" title="Отменить">↶</button>
                    <button id="wl-redo" class="wl-toolbar__icon" type="button" title="Вернуть">↷</button>
                    <span class="wl-toolbar__sep"></span>
                    <select id="wl-block-style" title="Стиль текста">
                        <option value="line">Текст</option>
                        <option value="heading1">H1</option>
                        <option value="heading2">H2</option>
                        <option value="heading3">H3</option>
                        <option value="callout">Цитата</option>
                    </select>
                    <button id="wl-bold" class="wl-toolbar__icon" type="button" title="Жирный">B</button>
                    <button id="wl-italic" class="wl-toolbar__icon" type="button" title="Курсив">I</button>
                    <button id="wl-underline" class="wl-toolbar__icon" type="button" title="Подчеркнутый">U</button>
                    <button id="wl-strike" class="wl-toolbar__icon" type="button" title="Зачеркнутый">S</button>
                    <span class="wl-toolbar__sep"></span>
                    <button id="wl-align-left" class="wl-toolbar__icon" type="button" title="Слева">L</button>
                    <button id="wl-align-center" class="wl-toolbar__icon" type="button" title="По центру">C</button>
                    <button id="wl-align-right" class="wl-toolbar__icon" type="button" title="Справа">R</button>
                </div>
                <div class="wl-toolbar__group">
                    <button id="wl-insert-object" type="button">Объект</button>
                    <button id="wl-insert-file" type="button">Файл</button>
                    <input id="wl-image-width" type="range" min="180" max="720" step="10" />
                    <span class="wl-toolbar__sep"></span>
                    <button id="wl-add-page" type="button">+ Страница</button>
                    <button id="wl-delete-page" type="button">Удалить страницу</button>
                    <div id="wl-page-meta" class="wl-toolbar__meta">1 / 1</div>
                </div>
            </div>
            <input id="wl-file-input" type="file" multiple hidden />
            <div id="wikilive-pages" class="wl-pages"></div>
        </div>
        <div id="wikilive-context-menu" class="wl-context-menu">
            <button id="wikilive-context-open" type="button">Выбрать из таблицы</button>
            <button id="wikilive-context-insert" type="button">Вставить значение</button>
            <div id="wikilive-context-hint" class="wl-context-menu__hint"></div>
        </div>
        <script>
        const parentWindow = window.parent;
        const parentDoc = parentWindow.document;
        const lookup = __WIKILIVE_LOOKUP__;
        const draftKey = __WIKILIVE_DRAFT_KEY__;
        const pageBreakMarker = __WIKILIVE_PAGE_BREAK_MARKER__;
        let activeSnippet = __WIKILIVE_ACTIVE_SNIPPET__;
        let activeHint = __WIKILIVE_ACTIVE_HINT__;
        const storageKey = `wikilive:draft:${draftKey}`;
        const selectedKey = `wikilive:selected:${draftKey}`;
        const snippetKey = `wikilive:active-snippet:${draftKey}`;
        const hintKey = `wikilive:active-hint:${draftKey}`;
        const tokenRegex = /(\{\{([^:}\n]+):([^:}\n]+):([^}\n]+)\}\}|\[\[WL_ATTACHMENT:([^\]]+)\]\])/g;
        const tableSeparatorRegex = /^:?-{3,}:?$/;
        const inlineStyleRegex = /(\*\*[^*][^*]*\*\*|__[^_][^_]*__|~~[^~][^~]*~~|\*[^*][^*]*\*)/g;
        const pagesHost = document.getElementById("wikilive-pages");
        const contextMenu = document.getElementById("wikilive-context-menu");
        const contextOpenButton = document.getElementById("wikilive-context-open");
        const contextInsertButton = document.getElementById("wikilive-context-insert");
        const contextHintNode = document.getElementById("wikilive-context-hint");
        const blockStyleSelect = document.getElementById("wl-block-style");
        const fileInput = document.getElementById("wl-file-input");
        const pageMetaNode = document.getElementById("wl-page-meta");
        const deletePageButton = document.getElementById("wl-delete-page");
        const imageWidthInput = document.getElementById("wl-image-width");
        const formatButtons = { bold: document.getElementById("wl-bold"), italic: document.getElementById("wl-italic"), underline: document.getElementById("wl-underline"), strikeThrough: document.getElementById("wl-strike") };
        const alignButtons = { left: document.getElementById("wl-align-left"), center: document.getElementById("wl-align-center"), right: document.getElementById("wl-align-right") };
        let selectedObject = null;
        let lastRange = null;
        let dragRaw = "";
        let dragSourceNode = null;
        let activePageIndex = 0;
        let isRendering = false;
        let storeTimer = null;
        let selectionTimer = null;
        let toolbarTimer = null;
        let frameTimer = null;

        function targetArea() { return parentDoc.querySelector('div[data-testid="stTextArea"] textarea') || parentDoc.querySelector("textarea"); }
        function getHiddenValue() { const area = targetArea(); return area ? String(area.value || "") : ""; }
        function setHiddenValue(value) {
            const area = targetArea();
            if (!area) return;
            const descriptor = Object.getOwnPropertyDescriptor(parentWindow.HTMLTextAreaElement.prototype, "value");
            if (descriptor && descriptor.set) { descriptor.set.call(area, value); } else { area.value = value; }
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
        function splitRawIntoPages(raw) {
            const lines = String(raw || "").replace(/\r\n/g, "\n").split("\n");
            const pages = [];
            let current = [];
            lines.forEach((line) => {
                if (line.trim() === pageBreakMarker) { pages.push(current.join("\n")); current = []; return; }
                current.push(line);
            });
            pages.push(current.join("\n"));
            return pages.length ? pages : [""];
        }
        function joinPages(pages) { return (pages.length ? pages : [""]).join(`\n${pageBreakMarker}\n`); }
        function getPages() { return Array.from(pagesHost.querySelectorAll(".wl-page")); }
        function getPageContents() { return Array.from(pagesHost.querySelectorAll(".wl-page__content")); }
        function queueFrameHeight() {
            if (frameTimer !== null) window.cancelAnimationFrame(frameTimer);
            frameTimer = window.requestAnimationFrame(() => {
                frameTimer = null;
                const height = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, pagesHost.scrollHeight + 180) + 24;
                parentWindow.postMessage({ type: "streamlit:setFrameHeight", height }, "*");
            });
        }
        function syncHiddenState() { const raw = serializeDocument(); storeDraft(raw); setHiddenValue(raw); }
        function attachActionSync() {
            parentDoc.querySelectorAll("button").forEach((button) => {
                if (button.dataset.wikiliveSyncAttached === "1") return;
                button.dataset.wikiliveSyncAttached = "1";
                button.addEventListener("mousedown", () => syncHiddenState(), true);
            });
        }
        function hideContextMenu() { contextMenu.style.display = "none"; }
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
        function openPicker() {
            const button = Array.from(parentDoc.querySelectorAll("button")).find((node) => {
                const text = (node.textContent || "").trim();
                return text === "Таблица" || text === "Скрыть таблицу";
            });
            if (button) button.click();
        }
        function closestObjectNode(node) {
            if (!node) return null;
            if (node.nodeType === Node.ELEMENT_NODE) return node.closest("[data-raw]");
            return node.parentElement ? node.parentElement.closest("[data-raw]") : null;
        }
        function closestPageContent(node) {
            if (!node) return null;
            if (node.nodeType === Node.ELEMENT_NODE) return node.closest(".wl-page__content");
            return node.parentElement ? node.parentElement.closest(".wl-page__content") : null;
        }
        function closestBlock(node) {
            if (!node) return null;
            if (node.nodeType === Node.ELEMENT_NODE) return node.closest(".wl-line, .wl-table-block");
            return node.parentElement ? node.parentElement.closest(".wl-line, .wl-table-block") : null;
        }
        function clearSelectedObject() {
            if (selectedObject) selectedObject.classList.remove("is-selected");
            selectedObject = null;
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            delete parentWindow.__wikiliveSelectedObjects[draftKey];
            parentWindow.sessionStorage.removeItem(selectedKey);
            imageWidthInput.style.display = "none";
        }
        function selectObject(node) {
            clearSelectedObject();
            selectedObject = node;
            selectedObject.classList.add("is-selected");
            const tokenIndex = selectedObject.dataset.tokenIndex || "";
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            parentWindow.__wikiliveSelectedObjects[draftKey] = tokenIndex;
            parentWindow.sessionStorage.setItem(selectedKey, tokenIndex);
            const page = closestPageContent(node);
            if (page) { activePageIndex = Number(page.dataset.pageIndex || "0"); updatePageMeta(); }
            if (selectedObject.classList.contains("wl-attachment--image")) {
                imageWidthInput.value = String(parseInt(selectedObject.dataset.width || "420", 10));
                imageWidthInput.style.display = "block";
            }
        }
        function restoreSelectedObject() {
            parentWindow.__wikiliveSelectedObjects = parentWindow.__wikiliveSelectedObjects || {};
            const storedIndex = parentWindow.__wikiliveSelectedObjects[draftKey] || parentWindow.sessionStorage.getItem(selectedKey);
            if (!storedIndex) return;
            const node = pagesHost.querySelector(`[data-token-index="${storedIndex}"]`);
            if (node) { selectedObject = node; selectedObject.classList.add("is-selected"); }
        }
        function createTextNode(text) { return document.createTextNode(text); }
        function decodeAttachmentPayload(payload) {
            try { return JSON.parse(decodeURIComponent(payload || "")); }
            catch (error) { return { name: "Вложение", mime: "", src: "", width: 420 }; }
        }
        function buildAttachmentSnippet(meta) { return `[[WL_ATTACHMENT:${encodeURIComponent(JSON.stringify(meta))}]]`; }
        function isImageMeta(meta) { return Boolean((meta.mime || "").startsWith("image/") || String(meta.src || "").startsWith("data:image/")); }
        function appendFormattedText(target, text) {
            inlineStyleRegex.lastIndex = 0;
            let cursor = 0;
            let match;
            while ((match = inlineStyleRegex.exec(text)) !== null) {
                if (match.index > cursor) target.appendChild(createTextNode(text.slice(cursor, match.index)));
                const token = match[0];
                let node = null;
                if (token.startsWith("**") && token.endsWith("**")) { node = document.createElement("strong"); node.textContent = token.slice(2, -2); }
                else if (token.startsWith("__") && token.endsWith("__")) { node = document.createElement("u"); node.className = "wl-inline-mark--underline"; node.textContent = token.slice(2, -2); }
                else if (token.startsWith("~~") && token.endsWith("~~")) { node = document.createElement("s"); node.className = "wl-inline-mark--strike"; node.textContent = token.slice(2, -2); }
                else if (token.startsWith("*") && token.endsWith("*")) { node = document.createElement("em"); node.textContent = token.slice(1, -1); }
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
                figure.dataset.width = String(meta.width || 420);
                figure.style.maxWidth = `${Math.max(180, Math.min(Number(meta.width || 420), 720))}px`;
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
                return createAttachmentNode(raw, { name: meta.value || fieldName, mime: meta.mimeType || "image/*", src: meta.resourceUrl, width: 320 }, tokenIndex, fieldName);
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
        function applyAlignmentToBlock(block, align) { block.dataset.align = align || "left"; block.style.textAlign = block.dataset.align; }
        function createLineBlock(kind, text, state, align = "left") {
            const line = document.createElement("div");
            line.className = "wl-line";
            line.dataset.kind = kind;
            applyAlignmentToBlock(line, align);
            renderInline(line, text, state);
            return line;
        }
        function parseTableCells(line) { return line.trim().slice(1, -1).split("|").map((cell) => cell.trim()); }
        function isTableLine(line) { const stripped = line.trim(); return stripped.startsWith("|") && stripped.endsWith("|") && stripped.length > 2; }
        function isTableSeparator(line) { const cells = parseTableCells(line); return cells.length > 0 && cells.every((cell) => tableSeparatorRegex.test(cell)); }
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
            headerCells.forEach((cell) => { const th = document.createElement("th"); renderInline(th, cell, state); headRow.appendChild(th); });
            thead.appendChild(headRow);
            table.appendChild(thead);
            const tbody = document.createElement("tbody");
            bodyRows.forEach((row) => {
                const tr = document.createElement("tr");
                row.forEach((cell) => { const td = document.createElement("td"); renderInline(td, cell, state); tr.appendChild(td); });
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
            const lines = String(raw || "").split("\n");
            let index = 0;
            while (index < lines.length) {
                const line = lines[index];
                const trimmed = line.trim();
                if (isTableLine(trimmed) && index + 1 < lines.length && isTableLine(lines[index + 1].trim()) && isTableSeparator(lines[index + 1].trim())) {
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
                if (!trimmed) { container.appendChild(createLineBlock("line", "", state)); index += 1; continue; }
                let kind = "line";
                let content = line;
                if (trimmed.startsWith("### ")) { kind = "heading3"; content = line.slice(line.indexOf("### ") + 4); }
                else if (trimmed.startsWith("## ")) { kind = "heading2"; content = line.slice(line.indexOf("## ") + 3); }
                else if (trimmed.startsWith("# ")) { kind = "heading1"; content = line.slice(line.indexOf("# ") + 2); }
                else if (trimmed.startsWith("> ")) { kind = "callout"; content = line.slice(line.indexOf("> ") + 2); }
                const aligned = extractAlignment(content);
                container.appendChild(createLineBlock(kind, aligned.text, state, aligned.align));
                index += 1;
            }
            if (!container.childNodes.length) container.appendChild(createLineBlock("line", "", state));
        }
        function updatePageMeta(scrollIntoView = false) {
            const pages = getPages();
            if (!pages.length) { pageMetaNode.textContent = "1 / 1"; return; }
            activePageIndex = Math.max(0, Math.min(activePageIndex, pages.length - 1));
            pages.forEach((page, index) => {
                page.classList.toggle("is-active", index === activePageIndex);
                const badge = page.querySelector(".wl-page__number");
                if (badge) badge.textContent = `Страница ${index + 1}`;
            });
            pageMetaNode.textContent = `${activePageIndex + 1} / ${pages.length}`;
            deletePageButton.textContent = pages.length > 1 ? "Удалить страницу" : "Очистить страницу";
            if (scrollIntoView) pages[activePageIndex].scrollIntoView({ behavior: "smooth", block: "start" });
            queueFrameHeight();
        }
        function renderRaw(raw) {
            isRendering = true;
            clearSelectedObject();
            pagesHost.innerHTML = "";
            const state = { tokenIndex: 0 };
            splitRawIntoPages(raw).forEach((pageRaw, pageIndex) => {
                const page = document.createElement("section");
                page.className = "wl-page";
                page.dataset.pageIndex = String(pageIndex);
                const badge = document.createElement("div");
                badge.className = "wl-page__number";
                badge.textContent = `Страница ${pageIndex + 1}`;
                page.appendChild(badge);
                const content = document.createElement("div");
                content.className = "wl-page__content";
                content.contentEditable = "true";
                content.spellcheck = true;
                content.dataset.pageIndex = String(pageIndex);
                content.dataset.placeholder = "Пиши здесь";
                renderBlocks(content, pageRaw, state);
                page.appendChild(content);
                pagesHost.appendChild(page);
                attachPageEvents(content);
            });
            restoreSelectedObject();
            updatePageMeta();
            isRendering = false;
            queueToolbarRefresh();
        }
        function serializeInlineNode(node) {
            if (node.nodeType === Node.TEXT_NODE) return (node.textContent || "").replace(/\u00a0/g, " ");
            if (node.nodeType !== Node.ELEMENT_NODE) return "";
            const element = node;
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
            const kind = element.dataset.kind || "line";
            const alignPrefix = element.dataset.align && element.dataset.align !== "left" ? `[[ALIGN:${element.dataset.align}]] ` : "";
            const text = Array.from(element.childNodes).map(serializeInlineNode).join("");
            if (kind === "heading1") return `# ${alignPrefix}${text}`;
            if (kind === "heading2") return `## ${alignPrefix}${text}`;
            if (kind === "heading3") return `### ${alignPrefix}${text}`;
            if (kind === "callout") return `> ${alignPrefix}${text}`;
            return `${alignPrefix}${text}`;
        }
        function serializePage(pageContent) { return Array.from(pageContent.childNodes).map(serializeBlockNode).join("\n"); }
        function serializeDocument() { return joinPages(getPageContents().map(serializePage)); }
        function queueDraftStore() {
            if (storeTimer !== null) window.clearTimeout(storeTimer);
            storeTimer = window.setTimeout(() => storeDraft(serializeDocument()), 220);
        }
        function rememberSelection() {
            const selection = window.getSelection();
            if (!selection || selection.rangeCount === 0) return;
            const range = selection.getRangeAt(0);
            const page = closestPageContent(range.startContainer);
            if (!page || !page.contains(range.endContainer)) return;
            activePageIndex = Number(page.dataset.pageIndex || "0");
            lastRange = range.cloneRange();
            updatePageMeta();
        }
        function queueRememberSelection() {
            if (selectionTimer !== null) window.clearTimeout(selectionTimer);
            selectionTimer = window.setTimeout(() => { rememberSelection(); queueToolbarRefresh(); }, 0);
        }
        function restoreSelection() {
            if (!lastRange) return false;
            try {
                if (!document.contains(lastRange.startContainer) || !document.contains(lastRange.endContainer)) return false;
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(lastRange);
                return true;
            } catch (error) { return false; }
        }
        function placeCaret(pageIndex = activePageIndex, placement = "end", scrollIntoView = false) {
            const pages = getPageContents();
            if (!pages.length) return;
            activePageIndex = Math.max(0, Math.min(pageIndex, pages.length - 1));
            const page = pages[activePageIndex];
            page.focus();
            const range = document.createRange();
            range.selectNodeContents(page);
            range.collapse(placement !== "start");
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            lastRange = range.cloneRange();
            updatePageMeta(scrollIntoView);
            queueToolbarRefresh();
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
        function replaceTokenAtIndex(raw, targetIndex, replacement) {
            let currentIndex = 0;
            tokenRegex.lastIndex = 0;
            return raw.replace(tokenRegex, (match) => {
                if (currentIndex === targetIndex) { currentIndex += 1; return replacement; }
                currentIndex += 1;
                return match;
            });
        }
        function updateSelectedImageWidth(width) {
            if (!selectedObject || !selectedObject.classList.contains("wl-attachment--image")) return;
            const nextWidth = Math.max(180, Math.min(Number(width || 420), 720));
            selectedObject.dataset.width = String(nextWidth);
            selectedObject.style.maxWidth = `${nextWidth}px`;
            queueDraftStore();
        }
        function renderAndStore(raw, focusPageIndex = activePageIndex, placement = "end", scrollIntoView = false) {
            activePageIndex = focusPageIndex;
            storeDraft(raw);
            renderRaw(raw);
            window.requestAnimationFrame(() => placeCaret(activePageIndex, placement, scrollIntoView));
        }
        function getCurrentBlock() {
            if (selectedObject) return closestBlock(selectedObject);
            const selection = window.getSelection();
            if (selection && selection.rangeCount > 0) {
                const block = closestBlock(selection.getRangeAt(0).startContainer);
                if (block) return block;
            }
            const page = getPageContents()[activePageIndex];
            return page ? page.querySelector(".wl-line, .wl-table-block") : null;
        }
        function queueToolbarRefresh() {
            if (toolbarTimer !== null) window.clearTimeout(toolbarTimer);
            toolbarTimer = window.setTimeout(refreshToolbarState, 0);
        }
        function refreshToolbarState() {
            const block = getCurrentBlock();
            if (block && block.dataset.kind && block.dataset.kind !== "table") {
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
            if (!(selectedObject && selectedObject.classList.contains("wl-attachment--image"))) imageWidthInput.style.display = "none";
        }
        function runEditorCommand(command) {
            const page = getPageContents()[activePageIndex] || getPageContents()[0];
            if (!page) return;
            page.focus();
            if (!restoreSelection()) placeCaret(activePageIndex, "end");
            document.execCommand(command, false, null);
            window.setTimeout(() => { queueDraftStore(); queueRememberSelection(); }, 0);
        }
        function applyBlockStyle(kind) {
            const block = getCurrentBlock();
            if (!block || block.dataset.kind === "table") return;
            block.dataset.kind = kind;
            queueDraftStore();
            queueToolbarRefresh();
            queueFrameHeight();
        }
        function applyAlignment(align) {
            const block = getCurrentBlock();
            if (!block || block.dataset.kind === "table") return;
            applyAlignmentToBlock(block, align);
            queueDraftStore();
            queueToolbarRefresh();
        }
        function insertSnippet(snippet) {
            if (!snippet) return;
            if (selectedObject && selectedObject.dataset.tokenIndex !== undefined) {
                const nextRaw = replaceTokenAtIndex(serializeDocument(), Number(selectedObject.dataset.tokenIndex), snippet);
                clearSelectedObject();
                renderAndStore(nextRaw, activePageIndex, "end");
                hideContextMenu();
                return;
            }
            const page = getPageContents()[activePageIndex] || getPageContents()[0];
            if (!page) return;
            page.focus();
            if (!restoreSelection()) placeCaret(activePageIndex, "end");
            document.execCommand("insertText", false, snippet);
            renderAndStore(serializeDocument(), activePageIndex, "end");
            hideContextMenu();
        }
        function addPage() {
            const pages = splitRawIntoPages(serializeDocument());
            const insertAt = Math.min(activePageIndex + 1, pages.length);
            pages.splice(insertAt, 0, "");
            renderAndStore(joinPages(pages), insertAt, "start", true);
        }
        function deleteCurrentPage() {
            const pages = splitRawIntoPages(serializeDocument());
            if (pages.length <= 1) { renderAndStore("", 0, "start"); return; }
            pages.splice(activePageIndex, 1);
            renderAndStore(joinPages(pages), Math.min(activePageIndex, pages.length - 1), "start", true);
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
            return buildAttachmentSnippet({ name: file.name || "Вложение", mime: file.type || "application/octet-stream", src, width: file.type.startsWith("image/") ? 420 : 0 });
        }
        async function insertFiles(files) {
            const items = Array.from(files || []);
            if (!items.length) return;
            const snippets = [];
            for (const file of items) snippets.push(await buildAttachmentSnippetFromFile(file));
            insertSnippet(snippets.join("\n"));
        }
        async function insertDroppedFiles(files, event) {
            const range = rangeFromPoint(event.clientX, event.clientY);
            if (range) {
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                lastRange = range.cloneRange();
                const page = closestPageContent(range.startContainer);
                if (page) { activePageIndex = Number(page.dataset.pageIndex || "0"); updatePageMeta(); }
            }
            await insertFiles(files);
        }
        function attachPageEvents(pageContent) {
            if (pageContent.dataset.bound === "1") return;
            pageContent.dataset.bound = "1";
            pageContent.addEventListener("focus", () => { activePageIndex = Number(pageContent.dataset.pageIndex || "0"); updatePageMeta(); queueToolbarRefresh(); });
            pageContent.addEventListener("click", (event) => {
                activePageIndex = Number(pageContent.dataset.pageIndex || "0");
                updatePageMeta();
                const objectNode = closestObjectNode(event.target);
                if (objectNode) {
                    event.preventDefault();
                    event.stopPropagation();
                    selectObject(objectNode);
                    openPicker();
                    return;
                }
                clearSelectedObject();
                hideContextMenu();
                rememberSelection();
                queueToolbarRefresh();
            });
            pageContent.addEventListener("keydown", (event) => {
                if (selectedObject && (event.key === "Backspace" || event.key === "Delete")) {
                    event.preventDefault();
                    selectedObject.remove();
                    clearSelectedObject();
                    renderAndStore(serializeDocument(), activePageIndex, "end");
                    return;
                }
                queueRememberSelection();
            });
            pageContent.addEventListener("input", () => {
                if (isRendering) return;
                queueDraftStore();
                queueRememberSelection();
                queueFrameHeight();
            });
            pageContent.addEventListener("paste", async (event) => {
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
                queueRememberSelection();
            });
            pageContent.addEventListener("mouseup", () => { rememberSelection(); queueToolbarRefresh(); });
            pageContent.addEventListener("keyup", queueRememberSelection);
            pageContent.addEventListener("dragstart", (event) => {
                const objectNode = closestObjectNode(event.target);
                if (!objectNode) return;
                dragSourceNode = objectNode;
                dragRaw = objectNode.dataset.raw || "";
                event.dataTransfer.setData("text/plain", dragRaw);
                event.dataTransfer.effectAllowed = "move";
            });
            pageContent.addEventListener("dragover", (event) => {
                if ((event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files.length) || dragRaw) event.preventDefault();
            });
            pageContent.addEventListener("drop", async (event) => {
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
                    placeCaret(activePageIndex, "end");
                }
                document.execCommand("insertText", false, dragRaw);
                dragRaw = "";
                dragSourceNode = null;
                renderAndStore(serializeDocument(), activePageIndex, "end");
            });
            pageContent.addEventListener("contextmenu", (event) => {
                event.preventDefault();
                activePageIndex = Number(pageContent.dataset.pageIndex || "0");
                updatePageMeta();
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
                showContextMenu(event.clientX, event.clientY);
            });
        }
        document.getElementById("wl-undo").addEventListener("click", () => runEditorCommand("undo"));
        document.getElementById("wl-redo").addEventListener("click", () => runEditorCommand("redo"));
        document.getElementById("wl-insert-object").addEventListener("click", () => openPicker());
        document.getElementById("wl-insert-file").addEventListener("click", () => fileInput.click());
        document.getElementById("wl-add-page").addEventListener("click", () => addPage());
        deletePageButton.addEventListener("click", () => deleteCurrentPage());
        Object.entries(formatButtons).forEach(([command, button]) => button.addEventListener("click", () => runEditorCommand(command)));
        Object.entries(alignButtons).forEach(([align, button]) => button.addEventListener("click", () => applyAlignment(align)));
        blockStyleSelect.addEventListener("change", () => applyBlockStyle(blockStyleSelect.value));
        imageWidthInput.addEventListener("input", () => updateSelectedImageWidth(imageWidthInput.value));
        fileInput.addEventListener("change", async () => { await insertFiles(fileInput.files); fileInput.value = ""; });
        contextOpenButton.addEventListener("click", () => { openPicker(); hideContextMenu(); });
        contextInsertButton.addEventListener("click", () => { ensureActiveSnippetState(); if (activeSnippet) insertSnippet(activeSnippet); });
        document.addEventListener("click", (event) => { if (!contextMenu.contains(event.target)) hideContextMenu(); }, true);
        document.addEventListener("scroll", hideContextMenu, true);
        window.addEventListener("resize", queueFrameHeight);
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
        const initialRaw = loadDraft();
        renderRaw(initialRaw);
        storeDraft(initialRaw);
        window.requestAnimationFrame(() => { placeCaret(activePageIndex, "end"); queueFrameHeight(); });
        </script>
    """
    html = html.replace("__WIKILIVE_LOOKUP__", json.dumps(insert_lookup, ensure_ascii=False))
    html = html.replace("__WIKILIVE_DRAFT_KEY__", json.dumps(draft_key))
    html = html.replace("__WIKILIVE_PAGE_BREAK_MARKER__", json.dumps(PAGE_BREAK_MARKER))
    html = html.replace("__WIKILIVE_ACTIVE_SNIPPET__", json.dumps(active_snippet))
    html = html.replace("__WIKILIVE_ACTIVE_HINT__", json.dumps(active_hint))
    components.html(html, height=1180)
