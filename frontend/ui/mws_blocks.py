from __future__ import annotations

from textwrap import dedent


def mws_blocks_styles() -> str:
    return dedent(
        """
        .mws-modal{position:fixed;inset:0;display:none;align-items:center;justify-content:center;padding:24px;z-index:58}
        .mws-modal.is-visible{display:flex}
        .mws-modal__backdrop{position:absolute;inset:0;background:rgba(16,22,31,.22);backdrop-filter:blur(8px)}
        .mws-modal__dialog{position:relative;width:min(920px,calc(100vw - 40px));max-height:min(760px,calc(100vh - 40px));padding:22px;border-radius:24px;background:#fff;border:1px solid #eceff5;box-shadow:0 26px 60px rgba(15,23,42,.18);display:flex;flex-direction:column;gap:16px;overflow:hidden}
        .mws-modal__close{position:absolute;top:16px;right:16px;width:32px;height:32px;border:0;border-radius:999px;background:#f4f6fb;color:#667085;font-size:20px}
        .mws-modal__title{margin:0;font-size:20px;font-weight:800;color:#1f2430}
        .mws-modal__subtitle{font-size:13px;color:#8b93a4;padding-right:32px}
        .mws-modal__toolbar,.mws-modal__panes{display:grid;grid-template-columns:minmax(220px,280px) minmax(200px,1fr) minmax(200px,1fr);gap:12px}
        .mws-modal__panes{grid-template-columns:1.1fr .9fr;min-height:0;flex:1}
        .mws-modal__field{display:flex;flex-direction:column;gap:7px}
        .mws-modal__label{font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#97a0b1}
        .mws-modal__select,.mws-modal__search{width:100%;min-height:40px;border-radius:12px;border:1px solid #e1e6ef;background:#fff;color:#2b3340;padding:0 13px;outline:none}
        .mws-modal__select:focus,.mws-modal__search:focus{border-color:#ff0032;box-shadow:0 0 0 3px rgba(255,0,50,.1)}
        .mws-modal__summary{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12px;color:#7d8797}
        .mws-modal__preview{border-radius:18px;border:1px solid #edf1f6;background:#ffffff;padding:12px 14px;display:flex;flex-direction:column;gap:8px}
        .mws-modal__preview-title{font-size:12px;font-weight:800;color:#2b3340}
        .mws-modal__preview-grid{border-radius:14px;border:1px solid #eef1f6;overflow:hidden}
        .mws-modal__preview-table{width:100%;border-collapse:separate;border-spacing:0}
        .mws-modal__preview-table th,.mws-modal__preview-table td{font-size:11px;padding:8px 10px;border-bottom:1px solid #eef1f6;text-align:left}
        .mws-modal__preview-table th{background:#f7f9fc;color:#6a7284;font-weight:700;text-transform:uppercase;letter-spacing:.03em}
        .mws-modal__preview-cell{cursor:pointer;transition:background .15s ease,color .15s ease}
        .mws-modal__preview-cell.is-selected{background:#ffe9ef;color:#c9153b}
        .mws-modal__preview-cell.is-anchor{box-shadow:inset 0 0 0 2px rgba(255,0,50,.35)}
        .mws-modal__preview-table tbody tr:last-child td{border-bottom:0}
        .mws-modal__preview-empty{font-size:12px;color:#98a2b3;padding:10px 12px;border-radius:12px;background:#f9fafc;border:1px dashed #e5e9f0}
        .mws-modal__badge{display:inline-flex;align-items:center;min-height:28px;padding:0 12px;border-radius:999px;background:#fff4f6;color:#ff0032;font-weight:700}
        .mws-modal__badge--ghost{background:#f6f8fb;color:#6c7485}
        .mws-modal__pane{min-height:0;border-radius:20px;border:1px solid #edf1f6;background:#fbfcfe;display:flex;flex-direction:column}
        .mws-modal__pane-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 16px 12px}
        .mws-modal__pane-title{font-size:14px;font-weight:800;color:#232833}
        .mws-modal__pane-meta{font-size:11px;color:#9aa3b3}
        .mws-modal__list{min-height:0;overflow:auto;padding:0 10px 10px;display:flex;flex-direction:column;gap:8px}
        .mws-modal__item{display:flex;align-items:flex-start;gap:10px;padding:11px 12px;border-radius:16px;border:1px solid #edf1f6;background:#fff}
        .mws-modal__item input{margin:2px 0 0;accent-color:#ff0032}
        .mws-modal__item-title{font-size:13px;font-weight:700;color:#232833;word-break:break-word}
        .mws-modal__item-meta{margin-top:4px;font-size:11px;color:#8b93a4}
        .mws-modal__empty{margin:10px;padding:18px 16px;border-radius:16px;border:1px dashed #dce2ed;background:#fff;text-align:center;font-size:12px;color:#98a2b3}
        .mws-modal__actions{display:flex;justify-content:flex-end;gap:10px}
        .mws-modal__action{min-width:140px;min-height:42px;border:0;border-radius:14px;background:#eff2f7;color:#2a3140;font-size:13px;font-weight:800}
        .mws-modal__action--primary{background:linear-gradient(135deg,#ff0032 0%,#ff335f 100%);color:#fff}
        .mws-modal__action:disabled{opacity:.45;cursor:default}
        .mws-live-block{display:block;width:100%;margin:18px 0;border-radius:24px;border:1px solid #ebeef5;background:linear-gradient(180deg,#fff 0%,#fcfdff 100%);box-shadow:0 18px 34px rgba(17,24,39,.08);overflow:hidden}
        .mws-live-block.is-selected{border-color:rgba(255,0,50,.28);box-shadow:0 18px 38px rgba(255,0,50,.14)}
        .mws-live-block__head{display:flex;align-items:center;gap:12px;padding:16px 18px 14px;border-bottom:1px solid #eef1f6;background:linear-gradient(180deg,rgba(255,255,255,.95) 0%,rgba(247,249,253,.95) 100%)}
        .mws-live-block__drag,.mws-live-block__refresh{height:34px;border:0;border-radius:12px;background:#f5f7fb;color:#434b5b;font-size:12px;font-weight:800}
        .mws-live-block__drag{width:34px;font-size:18px;flex:none}
        .mws-live-block__meta{min-width:0;display:flex;flex-direction:column;gap:5px;flex:1}
        .mws-live-block__title{font-size:15px;font-weight:800;color:#232833;word-break:break-word}
        .mws-live-block__subtitle{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12px;color:#8790a1}
        .mws-live-block__chip{display:inline-flex;align-items:center;min-height:24px;padding:0 9px;border-radius:999px;background:#fff4f6;color:#ff0032;font-size:11px;font-weight:800}
        .mws-live-block__body{padding:14px 16px 18px;overflow:auto}
        .mws-live-block__status{min-height:112px;border-radius:18px;border:1px dashed #dde4ef;background:#f9fbfe;display:flex;align-items:center;justify-content:center;text-align:center;padding:16px;font-size:13px;color:#8b93a4}
        .mws-live-block__status.is-error{color:#d92d20;background:#fff7f7;border-color:#ffd1d1}
        .mws-live-block__table-wrap{overflow:auto;border-radius:18px;border:1px solid #eef1f6}
        .mws-live-block__table{width:100%;min-width:520px;border-collapse:separate;border-spacing:0;background:#fff}
        .mws-live-block__table thead th{position:sticky;top:0;z-index:1;background:#f8fafc;color:#677084;font-size:11px;font-weight:800;letter-spacing:.03em;text-transform:uppercase;text-align:left;padding:12px;border-bottom:1px solid #e8edf4}
        .mws-live-block__table tbody td{padding:10px 12px;border-bottom:1px solid #eef2f7;vertical-align:top}
        .mws-live-block__row-name{font-size:13px;font-weight:700;color:#232833}
        .mws-live-block__row-meta{margin-top:3px;font-size:11px;color:#98a1b2}
        .mws-live-cell__input,.mws-live-cell__textarea{width:100%;min-height:40px;border-radius:12px;border:1px solid #e0e6ef;background:#fff;color:#243040;padding:10px 12px;outline:none;resize:vertical}
        .mws-live-cell__input:focus,.mws-live-cell__textarea:focus{border-color:#ff0032;box-shadow:0 0 0 3px rgba(255,0,50,.1)}
        .mws-live-cell__input.is-pending,.mws-live-cell__textarea.is-pending{background:#fff8f9;border-color:#ffc2cf}
        .mws-live-cell__image{display:flex;flex-direction:column;gap:8px}
        .mws-live-cell__image img{width:100%;max-width:200px;max-height:140px;object-fit:cover;border-radius:14px;border:1px solid #e8edf5;background:#f8fafc}
        .mws-live-cell__caption{font-size:12px;color:#6c7485;word-break:break-word}
        .mws-live-block__persisted{display:flex;align-items:center;gap:10px;min-height:74px;padding:16px 18px}
        .mws-live-block__persisted-icon{width:38px;height:38px;border-radius:14px;background:#fff4f6;color:#ff0032;display:inline-flex;align-items:center;justify-content:center;font-weight:900}
        .mws-live-block__persisted-meta{display:flex;flex-direction:column;gap:5px}
        .mws-live-block__persisted-title{font-size:14px;font-weight:800;color:#232833}
        .mws-live-block__persisted-subtitle{font-size:12px;color:#8b93a4}
        .mws-block-ghost{position:fixed;display:none;align-items:center;gap:10px;min-width:220px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.96);border:1px solid rgba(255,0,50,.22);box-shadow:0 18px 30px rgba(17,24,39,.14);pointer-events:none;z-index:48}
        .mws-block-ghost__icon{width:32px;height:32px;border-radius:12px;background:#fff4f6;color:#ff0032;display:inline-flex;align-items:center;justify-content:center;font-size:14px;font-weight:900;flex:none}
        .mws-block-ghost__label{font-size:13px;font-weight:700;color:#232833;word-break:break-word}
        @media (max-width:900px){.mws-modal__toolbar,.mws-modal__panes{grid-template-columns:1fr}.mws-live-block__table{min-width:420px}}
        """
    ).strip()


def mws_blocks_markup() -> str:
    return dedent(
        """
        <div class="mws-modal" id="mwsModal" aria-hidden="true">
          <div class="mws-modal__backdrop" data-mws-close="1"></div>
          <div class="mws-modal__dialog" role="dialog" aria-modal="true" aria-labelledby="mwsModalTitle">
            <button class="mws-modal__close" id="mwsModalClose" type="button" aria-label="Закрыть">&times;</button>
            <h2 class="mws-modal__title" id="mwsModalTitle">Живая таблица MWS</h2>
            <div class="mws-modal__subtitle">Выберите таблицу, строки и поля. Блок останется живым: его можно редактировать в документе, а изменения уйдут обратно в MWS.</div>
            <div class="mws-modal__toolbar">
              <div class="mws-modal__field"><label class="mws-modal__label" for="mwsTableSelect">Таблица</label><select class="mws-modal__select" id="mwsTableSelect"></select></div>
              <div class="mws-modal__field"><label class="mws-modal__label" for="mwsRecordSearch">Поиск по строкам</label><input class="mws-modal__search" id="mwsRecordSearch" type="search" placeholder="Например, проект, клиент, задача" /></div>
              <div class="mws-modal__field"><label class="mws-modal__label" for="mwsFieldSearch">Поиск по полям</label><input class="mws-modal__search" id="mwsFieldSearch" type="search" placeholder="Например, статус, ответственный, срок" /></div>
            </div>
            <div class="mws-modal__summary" id="mwsModalSummary"></div>
            <div class="mws-modal__preview" id="mwsModalPreview">
              <div class="mws-modal__preview-title">Предпросмотр</div>
              <div class="mws-modal__preview-empty">Выберите строки и поля — здесь появится мини-таблица.</div>
            </div>
            <div class="mws-modal__panes">
              <section class="mws-modal__pane"><div class="mws-modal__pane-head"><div class="mws-modal__pane-title">Строки / записи</div><div class="mws-modal__pane-meta" id="mwsRecordsMeta">0 выбрано</div></div><div class="mws-modal__list" id="mwsRecordList"></div></section>
              <section class="mws-modal__pane"><div class="mws-modal__pane-head"><div class="mws-modal__pane-title">Колонки / поля</div><div class="mws-modal__pane-meta" id="mwsFieldsMeta">0 выбрано</div></div><div class="mws-modal__list" id="mwsFieldList"></div></section>
            </div>
            <div class="mws-modal__actions">
              <button class="mws-modal__action" id="mwsModalCancel" type="button">Отменить</button>
              <button class="mws-modal__action mws-modal__action--primary" id="mwsModalInsert" type="button" disabled>Вставить живой блок</button>
            </div>
          </div>
        </div>
        """
    ).strip()


_SCRIPT_CHUNKS = [
    dedent(
        r"""
        (function() {
          const mwsModal = document.getElementById("mwsModal");
          if (!mwsModal) { return; }
          const mwsModalClose = document.getElementById("mwsModalClose");
          const mwsTableSelect = document.getElementById("mwsTableSelect");
          const mwsRecordSearch = document.getElementById("mwsRecordSearch");
          const mwsFieldSearch = document.getElementById("mwsFieldSearch");
          const mwsModalSummary = document.getElementById("mwsModalSummary");
          const mwsRecordList = document.getElementById("mwsRecordList");
          const mwsFieldList = document.getElementById("mwsFieldList");
          const mwsRecordsMeta = document.getElementById("mwsRecordsMeta");
          const mwsFieldsMeta = document.getElementById("mwsFieldsMeta");
          const mwsModalPreview = document.getElementById("mwsModalPreview");
          const mwsModalCancel = document.getElementById("mwsModalCancel");
          const mwsModalInsert = document.getElementById("mwsModalInsert");
          const mwsGhost = document.createElement("div");
          mwsGhost.className = "mws-block-ghost";
          mwsGhost.innerHTML = '<span class="mws-block-ghost__icon">MWS</span><span class="mws-block-ghost__label"></span>';
          editorCanvas.appendChild(mwsGhost);
          const mwsGhostLabel = mwsGhost.querySelector(".mws-block-ghost__label");
          const mwsState = { presets: [], tableLabel: "", tableId: "", viewId: "", recordSearch: "", fieldSearch: "", records: [], fieldNames: [], selectedRecords: new Set(), selectedFields: new Set(), loaded: false, loading: false, previewRows: [], previewCols: [] };
          const mwsCellSaveTimers = new Map();
          let selectedMwsBlock = null;
          let mwsInteraction = null;
          let mwsUidCounter = 0;
          let previewDragState = null;
          function safeHtml(value) {
            const text = String(value ?? "");
            if (typeof escapeHtml === "function") { return escapeHtml(text); }
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#39;");
          }
          function safeAttr(value) { return safeHtml(String(value ?? "")).replace(/`/g, "&#96;"); }
          function nextMwsBlockId() { mwsUidCounter += 1; return "mws-block-" + Date.now() + "-" + mwsUidCounter; }
          function parseMwsConfig(block) {
            if (!block) { return null; }
            const raw = block.dataset.mwsConfig || "";
            if (!raw) { return null; }
            try {
              const parsed = JSON.parse(raw);
              parsed.blockId = parsed.blockId || block.dataset.blockId || block.id || nextMwsBlockId();
              parsed.recordIds = Array.isArray(parsed.recordIds) ? parsed.recordIds.filter(Boolean) : [];
              parsed.fieldNames = Array.isArray(parsed.fieldNames) ? parsed.fieldNames.filter(Boolean) : [];
              return parsed;
            } catch (error) {
              console.warn("Failed to parse MWS block config", error);
              return null;
            }
          }
          function persistMwsConfig(block, config) {
            const normalized = { blockId: (config.blockId || block.dataset.blockId || block.id || nextMwsBlockId()), label: (config.label || config.tableLabel || "MWS"), tableLabel: (config.tableLabel || config.label || "MWS"), tableId: (config.tableId || ""), viewId: (config.viewId || ""), recordIds: Array.isArray(config.recordIds) ? config.recordIds.filter(Boolean) : [], fieldNames: Array.isArray(config.fieldNames) ? config.fieldNames.filter(Boolean) : [] };
            block.id = normalized.blockId;
            block.dataset.blockId = normalized.blockId;
            block.dataset.mwsLabel = normalized.label;
            block.dataset.mwsConfig = JSON.stringify(normalized);
            return normalized;
          }
          function summarizeMwsConfig(config) {
            if (!config) { return "MWS"; }
            const rows = Array.isArray(config.recordIds) ? config.recordIds.length : 0;
            const cols = Array.isArray(config.fieldNames) ? config.fieldNames.length : 0;
            const label = config.label || config.tableLabel || "MWS";
            return rows || cols ? `${label} · ${rows || 0}×${cols || 0}` : label;
          }
          function canonicalizeMwsBlockElement(block) {
            const config = parseMwsConfig(block);
            if (!config) { return; }
            persistMwsConfig(block, config);
            block.className = "mws-live-block";
            block.contentEditable = "false";
            block.dataset.kind = "mws-grid";
            block.dataset.commentObject = "1";
            block.innerHTML = `<div class="mws-live-block__persisted"><span class="mws-live-block__persisted-icon">MWS</span><div class="mws-live-block__persisted-meta"><div class="mws-live-block__persisted-title">${safeHtml(config.label || config.tableLabel || "Живая таблица MWS")}</div><div class="mws-live-block__persisted-subtitle">${safeHtml(summarizeMwsConfig(config))}</div></div></div>`;
          }
          window.wikiliveCanonicalizeMwsBlocksRoot = function(root) { if (!root || typeof root.querySelectorAll !== "function") { return root; } root.querySelectorAll(".mws-live-block").forEach((block) => canonicalizeMwsBlockElement(block)); return root; };
          window.wikiliveCanonicalizeMwsBlocksHtml = function(html) { const root = document.createElement("div"); root.innerHTML = html || ""; window.wikiliveCanonicalizeMwsBlocksRoot(root); return root.innerHTML; };
          window.wikiliveGetSerializableEditorHtml = function(rootElement = bodyEditor) { if (!rootElement) { return ""; } const clone = rootElement.cloneNode(true); window.wikiliveCanonicalizeMwsBlocksRoot(clone); return clone.innerHTML; };
          function inferRecordLabel(record, preferredFields = []) {
            if (!record) { return "Без названия"; }
            const fields = record.fields || {};
            const preferred = preferredFields.concat(Object.keys(fields));
            for (const name of preferred) { const value = String(fields[name] ?? "").trim(); if (value) { return value; } }
            return record.recordId || "Без названия";
          }
          function getPresetByKey(key) { return (mwsState.presets || []).find((preset) => preset.key === key) || null; }
        """
    ).strip(),
    dedent(
        r"""
          async function loadMwsDirectory(tableId = "", viewId = "") {
            if (mwsState.loading) { return; }
            mwsState.loading = true;
            renderMwsModal();
            try {
              const params = new URLSearchParams();
              if (tableId) { params.set("tableId", tableId); }
              if (viewId) { params.set("viewId", viewId); }
              const query = params.toString();
              const payload = await commentApiRequest(`/api/mws/insert-options${query ? "?" + query : ""}`, { timeoutMs: 30000 });
              mwsState.presets = Array.isArray(payload.tablePresets) ? payload.tablePresets : [];
              mwsState.tableId = payload.tableId || tableId || "";
              mwsState.viewId = payload.viewId || viewId || "";
              mwsState.tableLabel = payload.activeTable && payload.activeTable.label ? payload.activeTable.label : ((mwsState.presets[0] && mwsState.presets[0].label) || "Живая таблица MWS");
              const fieldNames = Array.isArray(payload.fieldNames) ? payload.fieldNames : [];
              const records = Array.isArray(payload.records) ? payload.records : [];
              mwsState.fieldNames = fieldNames.slice();
              mwsState.records = records.map((record) => ({ ...record, __label: inferRecordLabel(record, fieldNames) }));
              if (!mwsState.selectedRecords.size) {
                mwsState.records.slice(0, Math.min(3, mwsState.records.length)).forEach((record) => { if (record && record.recordId) { mwsState.selectedRecords.add(record.recordId); } });
              }
              if (!mwsState.selectedFields.size) {
                mwsState.fieldNames.slice(0, Math.min(4, mwsState.fieldNames.length)).forEach((fieldName) => mwsState.selectedFields.add(fieldName));
              }
              mwsState.loaded = true;
            } catch (error) {
              console.warn("Failed to load MWS insert options", error);
              mwsState.loaded = false;
            } finally {
              mwsState.loading = false;
              renderMwsModal();
            }
          }
          function getFilteredRecords() {
            const query = String(mwsState.recordSearch || "").trim().toLowerCase();
            if (!query) { return mwsState.records; }
            return mwsState.records.filter((record) => {
              const haystack = `${record.__label || ""} ${record.recordId || ""} ${JSON.stringify(record.fields || {})}`.toLowerCase();
              return haystack.includes(query);
            });
          }
          function getFilteredFields() {
            const query = String(mwsState.fieldSearch || "").trim().toLowerCase();
            if (!query) { return mwsState.fieldNames; }
            return mwsState.fieldNames.filter((fieldName) => String(fieldName || "").toLowerCase().includes(query));
          }
          function renderMwsPreview() {
            if (!mwsModalPreview) { return; }
            const recordIds = Array.from(mwsState.selectedRecords);
            const fieldNames = Array.from(mwsState.selectedFields);
            const previewRecords = getFilteredRecords();
            const previewFields = getFilteredFields();
            const previewRowLimit = 8;
            const previewColLimit = 6;
            mwsState.previewRows = previewRecords.slice(0, previewRowLimit);
            mwsState.previewCols = previewFields.slice(0, previewColLimit);
            if (!recordIds.length || !fieldNames.length) {
              mwsModalPreview.innerHTML = '<div class="mws-modal__preview-title">Предпросмотр</div><div class="mws-modal__preview-empty">Выберите строки и поля — здесь появится мини-таблица.</div>';
              return;
            }
            const recordsById = new Map((mwsState.records || []).map((record) => [record.recordId, record]));
            const rows = mwsState.previewRows.length ? mwsState.previewRows : recordIds.slice(0, 4).map((recordId) => recordsById.get(recordId)).filter(Boolean);
            const cols = mwsState.previewCols.length ? mwsState.previewCols : fieldNames.slice(0, 3);
            const tableHead = `<thead><tr><th>Строка</th>${cols.map((name) => `<th>${safeHtml(name)}</th>`).join("")}</tr></thead>`;
            const tableBody = `<tbody>${rows.map((record) => {
              const label = inferRecordLabel(record, cols);
              return `<tr><td>${safeHtml(label)}</td>${cols.map((fieldName, colIndex) => {
                const value = record.fields && Object.prototype.hasOwnProperty.call(record.fields, fieldName) ? record.fields[fieldName] : "";
                const isSelected = mwsState.selectedRecords.has(record.recordId) && mwsState.selectedFields.has(fieldName);
                return `<td class="mws-modal__preview-cell${isSelected ? " is-selected" : ""}" data-preview-row="${safeAttr(String(rows.indexOf(record)))}" data-preview-col="${safeAttr(String(colIndex))}" data-preview-record="${safeAttr(record.recordId || "")}" data-preview-field="${safeAttr(fieldName)}">${safeHtml(String(value ?? ""))}</td>`;
              }).join("")}</tr>`;
            }).join("")}</tbody>`;
            const extraRow = recordIds.length > rows.length ? `<tr><td colspan="${cols.length + 1}">… ещё ${recordIds.length - rows.length} строк</td></tr>` : "";
            const extraColNote = fieldNames.length > cols.length ? `Показаны ${cols.length} из ${fieldNames.length} полей` : `Поля: ${fieldNames.length}`;
            mwsModalPreview.innerHTML = [
              '<div class="mws-modal__preview-title">Предпросмотр</div>',
              '<div class="mws-modal__preview-grid"><table class="mws-modal__preview-table" data-mws-preview-table="1">',
              tableHead,
              tableBody,
              extraRow ? `<tbody>${extraRow}</tbody>` : "",
              '</table></div>',
              `<div class="mws-modal__summary"><span class="mws-modal__badge mws-modal__badge--ghost">${safeHtml(extraColNote)}</span></div>`
            ].join("");
            wirePreviewSelection();
          }
          function wirePreviewSelection() {
            if (!mwsModalPreview) { return; }
            const table = mwsModalPreview.querySelector("[data-mws-preview-table]");
            if (!table) { return; }
            table.addEventListener("pointerdown", (event) => {
              const cell = event.target.closest("[data-preview-row][data-preview-col]");
              if (!cell) { return; }
              event.preventDefault();
              const startRow = Number(cell.dataset.previewRow);
              const startCol = Number(cell.dataset.previewCol);
              previewDragState = { startRow, startCol, endRow: startRow, endCol: startCol };
              updatePreviewSelection();
              document.addEventListener("pointermove", handlePreviewDrag);
              document.addEventListener("pointerup", finishPreviewDrag);
              document.addEventListener("pointercancel", finishPreviewDrag);
            });
          }
          function handlePreviewDrag(event) {
            if (!previewDragState) { return; }
            const cell = event.target.closest("[data-preview-row][data-preview-col]");
            if (!cell) { return; }
            previewDragState.endRow = Number(cell.dataset.previewRow);
            previewDragState.endCol = Number(cell.dataset.previewCol);
            updatePreviewSelection();
          }
          function finishPreviewDrag() {
            if (!previewDragState) { return; }
            previewDragState = null;
            document.removeEventListener("pointermove", handlePreviewDrag);
            document.removeEventListener("pointerup", finishPreviewDrag);
            document.removeEventListener("pointercancel", finishPreviewDrag);
            renderMwsModal();
          }
          function updatePreviewSelection() {
            if (!previewDragState) { return; }
            const rows = mwsState.previewRows || [];
            const cols = mwsState.previewCols || [];
            if (!rows.length || !cols.length) { return; }
            const minRow = Math.max(0, Math.min(previewDragState.startRow, previewDragState.endRow));
            const maxRow = Math.min(rows.length - 1, Math.max(previewDragState.startRow, previewDragState.endRow));
            const minCol = Math.max(0, Math.min(previewDragState.startCol, previewDragState.endCol));
            const maxCol = Math.min(cols.length - 1, Math.max(previewDragState.startCol, previewDragState.endCol));
            const nextRecords = new Set();
            const nextFields = new Set();
            for (let i = minRow; i <= maxRow; i += 1) {
              const record = rows[i];
              if (record && record.recordId) { nextRecords.add(record.recordId); }
            }
            for (let j = minCol; j <= maxCol; j += 1) {
              const fieldName = cols[j];
              if (fieldName) { nextFields.add(fieldName); }
            }
            mwsState.selectedRecords = nextRecords;
            mwsState.selectedFields = nextFields;
            const table = mwsModalPreview.querySelector("[data-mws-preview-table]");
            if (!table) { return; }
            table.querySelectorAll("[data-preview-row][data-preview-col]").forEach((cell) => {
              const rowIndex = Number(cell.dataset.previewRow);
              const colIndex = Number(cell.dataset.previewCol);
              const isSelected = rowIndex >= minRow && rowIndex <= maxRow && colIndex >= minCol && colIndex <= maxCol;
              cell.classList.toggle("is-selected", isSelected);
              cell.classList.toggle("is-anchor", rowIndex === previewDragState.startRow && colIndex === previewDragState.startCol);
            });
          }
          function renderMwsModal() {
            if (mwsTableSelect) {
              mwsTableSelect.innerHTML = (mwsState.presets || []).map((preset) => {
                const selected = preset.tableId === mwsState.tableId && preset.viewId === mwsState.viewId;
                return `<option value="${safeAttr(preset.key)}" ${selected ? "selected" : ""}>${safeHtml(preset.label || preset.key || "MWS")}</option>`;
              }).join("");
            }
            if (mwsModalSummary) {
              const badges = [
                `<span class="mws-modal__badge">${safeHtml(mwsState.tableLabel || "MWS")}</span>`,
                `<span class="mws-modal__badge mws-modal__badge--ghost">${mwsState.selectedRecords.size} строк</span>`,
                `<span class="mws-modal__badge mws-modal__badge--ghost">${mwsState.selectedFields.size} полей</span>`
              ];
              if (mwsState.loading) { badges.push('<span class="mws-modal__badge mws-modal__badge--ghost">Загружаем структуру…</span>'); }
              mwsModalSummary.innerHTML = badges.join("");
            }
            if (mwsRecordsMeta) { mwsRecordsMeta.textContent = `${mwsState.selectedRecords.size} выбрано`; }
            if (mwsFieldsMeta) { mwsFieldsMeta.textContent = `${mwsState.selectedFields.size} выбрано`; }
            if (mwsRecordList) {
              const records = getFilteredRecords();
              mwsRecordList.innerHTML = !records.length
                ? `<div class="mws-modal__empty">${mwsState.loading ? "Загружаем записи…" : "Записи не найдены"}</div>`
                : records.map((record) => `<label class="mws-modal__item"><input type="checkbox" value="${safeAttr(record.recordId || "")}" ${mwsState.selectedRecords.has(record.recordId) ? "checked" : ""} /><span><div class="mws-modal__item-title">${safeHtml(record.__label || record.recordId || "Без названия")}</div><div class="mws-modal__item-meta">${safeHtml(record.recordId || "")}</div></span></label>`).join("");
            }
            if (mwsFieldList) {
              const fields = getFilteredFields();
              mwsFieldList.innerHTML = !fields.length
                ? `<div class="mws-modal__empty">${mwsState.loading ? "Загружаем поля…" : "Поля не найдены"}</div>`
                : fields.map((fieldName) => `<label class="mws-modal__item"><input type="checkbox" value="${safeAttr(fieldName)}" ${mwsState.selectedFields.has(fieldName) ? "checked" : ""} /><span><div class="mws-modal__item-title">${safeHtml(fieldName)}</div><div class="mws-modal__item-meta">Поле таблицы</div></span></label>`).join("");
            }
            renderMwsPreview();
            if (mwsModalInsert) { mwsModalInsert.disabled = mwsState.loading || !mwsState.selectedRecords.size || !mwsState.selectedFields.size; }
          }
          function openMwsModal() {
            hideFloatingMenus();
            mwsModal.classList.add("is-visible");
            mwsModal.setAttribute("aria-hidden", "false");
            renderMwsModal();
            const preset = getPresetByKey(mwsTableSelect ? mwsTableSelect.value : "");
            loadMwsDirectory(preset ? preset.tableId : mwsState.tableId, preset ? preset.viewId : mwsState.viewId);
          }
          function closeMwsModal() { mwsModal.classList.remove("is-visible"); mwsModal.setAttribute("aria-hidden", "true"); }
          function createMwsBlock(config) {
            const block = document.createElement("div");
            block.className = "mws-live-block";
            block.contentEditable = "false";
            block.dataset.kind = "mws-grid";
            block.dataset.commentObject = "1";
            const normalized = persistMwsConfig(block, config);
            block.innerHTML = `<div class="mws-live-block__head"><button class="mws-live-block__drag" type="button" data-mws-drag="1" aria-label="Переместить блок">⋮⋮</button><div class="mws-live-block__meta"><div class="mws-live-block__title">${safeHtml(normalized.label || normalized.tableLabel || "Живая таблица MWS")}</div><div class="mws-live-block__subtitle"><span class="mws-live-block__chip">MWS live</span><span>${safeHtml((normalized.recordIds || []).length + " строк · " + (normalized.fieldNames || []).length + " полей")}</span></div></div><button class="mws-live-block__refresh" type="button" data-mws-refresh="1">Обновить</button></div><div class="mws-live-block__body"><div class="mws-live-block__status">Подключаемся к таблице MWS…</div></div>`;
            return block;
          }
          function clearSelectedMwsBlock() {
            if (selectedMwsBlock) { selectedMwsBlock.classList.remove("is-selected"); }
            selectedMwsBlock = null;
            mwsGhost.style.display = "none";
            hideImageDropIndicator();
          }
          function selectMwsBlock(block) {
            if (!block) { clearSelectedMwsBlock(); return; }
            if (selectedMwsBlock && selectedMwsBlock !== block) { selectedMwsBlock.classList.remove("is-selected"); }
            selectedMwsBlock = block;
            selectedMwsBlock.classList.add("is-selected");
            if (typeof clearSelectedImageBlock === "function") { clearSelectedImageBlock(); }
          }
          function showMwsGhost(rect, label) {
            if (!rect) { mwsGhost.style.display = "none"; return; }
            mwsGhost.style.display = "inline-flex";
            mwsGhost.style.left = rect.left + "px";
            mwsGhost.style.top = rect.top + "px";
            mwsGhostLabel.textContent = label || "Живая таблица MWS";
          }
        """
    ).strip(),
    dedent(
        r"""
          function getBlockDropTarget(clientX, clientY, draggedBlock) {
            const range = getCaretRangeFromPoint(clientX, clientY);
            if (!range || !bodyEditor.contains(range.commonAncestorContainer)) { return null; }
            const owner = range.startContainer.nodeType === Node.ELEMENT_NODE ? range.startContainer : range.startContainer.parentElement;
            const ownerBlock = owner ? owner.closest(".mws-live-block, .embedded-image-block") : null;
            if (ownerBlock && ownerBlock === draggedBlock) {
              const rect = draggedBlock.getBoundingClientRect();
              return { range: null, rect: { left: rect.right, top: rect.top, height: rect.height } };
            }
            let rect = null;
            const rects = Array.from(range.getClientRects()).filter((item) => item.width || item.height);
            if (rects.length) {
              rect = rects[0];
            } else {
              const block = findEditableBlock(range.startContainer);
              if (block) {
                const blockRect = block.getBoundingClientRect();
                rect = { left: blockRect.left, top: blockRect.top, height: blockRect.height };
              }
            }
            return { range: range.cloneRange(), rect: rect || { left: bodyEditor.getBoundingClientRect().left, top: bodyEditor.getBoundingClientRect().top, height: 26 } };
          }
          function commitMwsBlockMove(block, clientX, clientY) {
            const target = getBlockDropTarget(clientX, clientY, block);
            if (!block || !block.parentNode || !target || !target.range) { return; }
            const selection = window.getSelection();
            block.remove();
            target.range.insertNode(block);
            const spacer = document.createTextNode("\u00A0");
            if (block.parentNode) { block.parentNode.insertBefore(spacer, block.nextSibling); }
            if (selection) {
              const nextRange = document.createRange();
              nextRange.setStartAfter(spacer);
              nextRange.collapse(true);
              selection.removeAllRanges();
              selection.addRange(nextRange);
              savedRange = nextRange.cloneRange();
            }
          }
          function finishMwsInteraction(event) {
            if (!mwsInteraction) { return; }
            const interaction = mwsInteraction;
            mwsInteraction = null;
            clearCursorState();
            document.removeEventListener("pointermove", handleMwsInteractionMove);
            document.removeEventListener("pointerup", finishMwsInteraction);
            document.removeEventListener("pointercancel", finishMwsInteraction);
            if (interaction.hasMoved) {
              commitMwsBlockMove(interaction.block, event.clientX, event.clientY);
              if (typeof scheduleCommentDocumentSave === "function" && typeof getCurrentCommentActor === "function") { scheduleCommentDocumentSave("Перемещен блок MWS", getCurrentCommentActor().id); }
            }
            clearSelectedMwsBlock();
            selectMwsBlock(interaction.block);
          }
          function handleMwsInteractionMove(event) {
            if (!mwsInteraction) { return; }
            event.preventDefault();
            const moveX = Math.abs(event.clientX - mwsInteraction.startX);
            const moveY = Math.abs(event.clientY - mwsInteraction.startY);
            if (!mwsInteraction.hasMoved && moveX + moveY < 6) { return; }
            mwsInteraction.hasMoved = true;
            showMwsGhost({ left: event.clientX - mwsInteraction.offsetX, top: event.clientY - mwsInteraction.offsetY }, mwsInteraction.label);
            showImageDropIndicator(getBlockDropTarget(event.clientX, event.clientY, mwsInteraction.block));
          }
          function startMwsBlockMove(block, event) {
            if (!block || event.button !== 0) { return; }
            event.preventDefault();
            event.stopPropagation();
            const rect = block.getBoundingClientRect();
            mwsInteraction = { block, label: summarizeMwsConfig(parseMwsConfig(block)), startX: event.clientX, startY: event.clientY, offsetX: event.clientX - rect.left, offsetY: event.clientY - rect.top, hasMoved: false };
            selectMwsBlock(block);
            setCursorState("grabbing");
            document.addEventListener("pointermove", handleMwsInteractionMove);
            document.addEventListener("pointerup", finishMwsInteraction);
            document.addEventListener("pointercancel", finishMwsInteraction);
          }
          function getGridUrl(config) {
            const params = new URLSearchParams();
            if (config.tableId) { params.set("tableId", config.tableId); }
            if (config.viewId) { params.set("viewId", config.viewId); }
            if (Array.isArray(config.recordIds) && config.recordIds.length) { params.set("recordIds", config.recordIds.join(",")); }
            if (Array.isArray(config.fieldNames) && config.fieldNames.length) { params.set("fieldNames", config.fieldNames.join(",")); }
            return `/api/mws/grid?${params.toString()}`;
          }
          function renderMwsBlockError(block, message) {
            const config = parseMwsConfig(block);
            if (!config) { return; }
            block.innerHTML = `<div class="mws-live-block__head"><button class="mws-live-block__drag" type="button" data-mws-drag="1" aria-label="Переместить блок">⋮⋮</button><div class="mws-live-block__meta"><div class="mws-live-block__title">${safeHtml(config.label || config.tableLabel || "Живая таблица MWS")}</div><div class="mws-live-block__subtitle"><span class="mws-live-block__chip">MWS live</span><span>${safeHtml(summarizeMwsConfig(config))}</span></div></div><button class="mws-live-block__refresh" type="button" data-mws-refresh="1">Повторить</button></div><div class="mws-live-block__body"><div class="mws-live-block__status is-error">${safeHtml(message || "Не удалось загрузить данные MWS")}</div></div>`;
          }
          function renderMwsGrid(block, payload) {
            const config = parseMwsConfig(block);
            if (!config) { return; }
            const records = Array.isArray(payload.records) ? payload.records : [];
            const fieldNames = Array.isArray(payload.fieldNames) ? payload.fieldNames : (config.fieldNames || []);
            const title = payload.activeTable && payload.activeTable.label ? payload.activeTable.label : (config.label || config.tableLabel || "Живая таблица MWS");
            block.innerHTML = `<div class="mws-live-block__head"><button class="mws-live-block__drag" type="button" data-mws-drag="1" aria-label="Переместить блок">⋮⋮</button><div class="mws-live-block__meta"><div class="mws-live-block__title">${safeHtml(title)}</div><div class="mws-live-block__subtitle"><span class="mws-live-block__chip">MWS live</span><span>${safeHtml(records.length + " строк · " + fieldNames.length + " полей")}</span></div></div><button class="mws-live-block__refresh" type="button" data-mws-refresh="1">Обновить</button></div><div class="mws-live-block__body">${
              records.length && fieldNames.length
                ? `<div class="mws-live-block__table-wrap"><table class="mws-live-block__table"><thead><tr><th>Строка</th>${fieldNames.map((fieldName) => `<th>${safeHtml(fieldName)}</th>`).join("")}</tr></thead><tbody>${records.map((record) => {
                    const rowLabel = inferRecordLabel(record, fieldNames);
                    const fieldMeta = record.fieldMeta || {};
                    return `<tr><td><div class="mws-live-block__row-name">${safeHtml(rowLabel)}</div><div class="mws-live-block__row-meta">${safeHtml(record.recordId || "")}</div></td>${fieldNames.map((fieldName) => {
                      const value = record.fields && Object.prototype.hasOwnProperty.call(record.fields, fieldName) ? record.fields[fieldName] : "";
                      const textValue = String(value ?? "");
                      const meta = fieldMeta[fieldName] || {};
                      if (meta.isImage && meta.resourceUrl) {
                        return `<td class="mws-live-cell"><div class="mws-live-cell__image"><img src="${safeAttr(meta.resourceUrl)}" alt="${safeAttr(fieldName)}" /><div class="mws-live-cell__caption">${safeHtml(textValue || fieldName)}</div></div></td>`;
                      }
                      if (textValue.length > 88 || textValue.includes("\n")) {
                        return `<td class="mws-live-cell"><textarea class="mws-live-cell__textarea" data-mws-record-id="${safeAttr(record.recordId || "")}" data-mws-field-name="${safeAttr(fieldName)}">${safeHtml(textValue)}</textarea></td>`;
                      }
                      return `<td class="mws-live-cell"><input class="mws-live-cell__input" type="text" value="${safeAttr(textValue)}" data-mws-record-id="${safeAttr(record.recordId || "")}" data-mws-field-name="${safeAttr(fieldName)}" /></td>`;
                    }).join("")}</tr>`;
                  }).join("")}</tbody></table></div>`
                : `<div class="mws-live-block__status">Нет данных для выбранного диапазона. Измените набор строк или полей.</div>`
            }</div>`;
            persistMwsConfig(block, { ...config, label: title, tableLabel: title, fieldNames });
          }
          async function hydrateMwsBlock(block, options = {}) {
            const config = parseMwsConfig(block);
            if (!config || !config.tableId || !config.recordIds.length || !config.fieldNames.length) { renderMwsBlockError(block, "У блока MWS не хватает параметров диапазона"); return null; }
            const activeField = document.activeElement;
            if (!options.force && activeField && block.contains(activeField) && activeField.matches("[data-mws-field-name]")) { return null; }
            try {
              const payload = await commentApiRequest(getGridUrl(config), { timeoutMs: 30000 });
              renderMwsGrid(block, payload || {});
              return payload;
            } catch (error) {
              console.warn("Failed to hydrate MWS block", error);
              renderMwsBlockError(block, error && error.message ? error.message : "Не удалось загрузить данные MWS");
              return null;
            }
          }
          async function persistMwsCell(block, recordId, fieldName, value, input) {
            const config = parseMwsConfig(block);
            if (!config) { return; }
            if (input) {
              input.classList.add("is-pending");
              if (input.tagName === "INPUT") { input.setAttribute("value", value); } else { input.textContent = value; }
            }
            try {
              const payload = await commentApiRequest("/api/mws/grid/update", { method: "POST", timeoutMs: 30000, body: JSON.stringify({ tableId: config.tableId, viewId: config.viewId, recordIds: config.recordIds || [], fieldNames: config.fieldNames || [], updates: [{ recordId, fields: { [fieldName]: value } }] }) });
              renderMwsGrid(block, payload || {});
              if (typeof scheduleCommentDocumentSave === "function" && typeof getCurrentCommentActor === "function") { scheduleCommentDocumentSave("Обновлены данные MWS", getCurrentCommentActor().id); }
              if (typeof window.refreshTimeMachinePanel === "function") { window.refreshTimeMachinePanel(); }
            } catch (error) {
              console.warn("Failed to save MWS cell", error);
              renderMwsBlockError(block, error && error.message ? error.message : "Не удалось сохранить изменения в MWS");
            } finally {
              if (input) { input.classList.remove("is-pending"); }
            }
          }
          function queueMwsCellSave(block, recordId, fieldName, value, input) {
            const key = `${block.id}:${recordId}:${fieldName}`;
            if (mwsCellSaveTimers.has(key)) { clearTimeout(mwsCellSaveTimers.get(key)); }
            mwsCellSaveTimers.set(key, window.setTimeout(async () => {
              mwsCellSaveTimers.delete(key);
              await persistMwsCell(block, recordId, fieldName, value, input);
            }, 650));
          }
        """
    ).strip(),
    dedent(
        r"""
          function applyMwsSelectionFromModal() {
            const preset = getPresetByKey(mwsTableSelect ? mwsTableSelect.value : "") || { tableId: mwsState.tableId, viewId: mwsState.viewId, label: mwsState.tableLabel || "Живая таблица MWS" };
            const config = { blockId: nextMwsBlockId(), label: preset.label || mwsState.tableLabel || "Живая таблица MWS", tableLabel: preset.label || mwsState.tableLabel || "Живая таблица MWS", tableId: preset.tableId || mwsState.tableId, viewId: preset.viewId || mwsState.viewId, recordIds: Array.from(mwsState.selectedRecords), fieldNames: Array.from(mwsState.selectedFields) };
            const block = createMwsBlock(config);
            insertNodeWithTrailingParagraph(block);
            closeMwsModal();
            saveCurrentRange();
            selectMwsBlock(block);
            hydrateMwsBlock(block, { force: true });
            updateActiveToolbarButtons();
            updateSelectionToolbar();
            updateBlockHandleFromSelection();
            showTooltip("Живая таблица MWS");
            if (typeof scheduleCommentDocumentSave === "function" && typeof getCurrentCommentActor === "function") { scheduleCommentDocumentSave("Вставка данных из таблицы", getCurrentCommentActor().id); }
          }
          window.wikiliveHydrateMwsBlocks = function(force = false) {
            const blocks = Array.from(bodyEditor.querySelectorAll(".mws-live-block"));
            return Promise.all(blocks.map((block) => hydrateMwsBlock(block, { force: Boolean(force) })));
          };
          window.wikiliveOpenMwsBlockDialog = openMwsModal;
          slashItems.push({ icon: "MWS", label: "Живая таблица MWS", queries: ["mws", "таблица", "данные", "cells", "grid"], kind: "insert", value: "mws-grid" });
          if (mwsTableSelect) {
            mwsTableSelect.addEventListener("change", () => {
              const preset = getPresetByKey(mwsTableSelect.value);
              mwsState.selectedRecords = new Set();
              mwsState.selectedFields = new Set();
              loadMwsDirectory(preset ? preset.tableId : "", preset ? preset.viewId : "");
            });
          }
          if (mwsRecordSearch) { mwsRecordSearch.addEventListener("input", () => { mwsState.recordSearch = mwsRecordSearch.value || ""; renderMwsModal(); }); }
          if (mwsFieldSearch) { mwsFieldSearch.addEventListener("input", () => { mwsState.fieldSearch = mwsFieldSearch.value || ""; renderMwsModal(); }); }
          if (mwsRecordList) {
            mwsRecordList.addEventListener("change", (event) => {
              const input = event.target.closest('input[type="checkbox"]');
              if (!input) { return; }
              if (input.checked) { mwsState.selectedRecords.add(input.value || ""); } else { mwsState.selectedRecords.delete(input.value || ""); }
              renderMwsModal();
            });
          }
          if (mwsFieldList) {
            mwsFieldList.addEventListener("change", (event) => {
              const input = event.target.closest('input[type="checkbox"]');
              if (!input) { return; }
              if (input.checked) { mwsState.selectedFields.add(input.value || ""); } else { mwsState.selectedFields.delete(input.value || ""); }
              renderMwsModal();
            });
          }
          if (mwsModalInsert) { mwsModalInsert.addEventListener("click", applyMwsSelectionFromModal); }
          if (mwsModalCancel) { mwsModalCancel.addEventListener("click", closeMwsModal); }
          if (mwsModalClose) { mwsModalClose.addEventListener("click", closeMwsModal); }
          mwsModal.addEventListener("click", (event) => { if (event.target.closest("[data-mws-close='1']")) { closeMwsModal(); } });
          bodyEditor.addEventListener("click", (event) => {
            const block = event.target.closest(".mws-live-block");
            if (!block) { return; }
            selectMwsBlock(block);
            if (event.target.closest("[data-mws-refresh='1']")) { hydrateMwsBlock(block, { force: true }); }
          });
          bodyEditor.addEventListener("pointerdown", (event) => {
            const dragHandle = event.target.closest("[data-mws-drag='1']");
            if (!dragHandle) { return; }
            startMwsBlockMove(dragHandle.closest(".mws-live-block"), event);
          });
          bodyEditor.addEventListener("input", (event) => {
            const input = event.target.closest("[data-mws-record-id][data-mws-field-name]");
            if (!input) { return; }
            const block = input.closest(".mws-live-block");
            if (!block) { return; }
            queueMwsCellSave(block, input.dataset.mwsRecordId || "", input.dataset.mwsFieldName || "", input.value || "", input);
          });
          document.addEventListener("keydown", (event) => {
            if (mwsModal.classList.contains("is-visible") && event.key === "Escape") { event.preventDefault(); closeMwsModal(); return; }
            if (selectedMwsBlock && (event.key === "Delete" || event.key === "Backspace")) {
              if (document.activeElement && selectedMwsBlock.contains(document.activeElement) && document.activeElement.matches("[data-mws-field-name]")) { return; }
              event.preventDefault();
              const removed = selectedMwsBlock;
              clearSelectedMwsBlock();
              removed.remove();
              if (typeof scheduleCommentDocumentSave === "function" && typeof getCurrentCommentActor === "function") { scheduleCommentDocumentSave("Удален блок MWS", getCurrentCommentActor().id); }
            }
          });
          document.addEventListener("click", (event) => { if (!event.target.closest(".mws-live-block")) { clearSelectedMwsBlock(); } });
          document.addEventListener("wikilive:page-ready", () => { window.requestAnimationFrame(() => window.wikiliveHydrateMwsBlocks(true)); });
          window.setInterval(() => { if (!document.hidden) { window.wikiliveHydrateMwsBlocks(false); } }, 8000);
        })();
        """
    ).strip(),
]


def mws_blocks_script() -> str:
    return "\n".join(_SCRIPT_CHUNKS)
