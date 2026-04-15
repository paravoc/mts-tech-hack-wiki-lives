from __future__ import annotations

from textwrap import dedent


def editor_plugins_styles() -> str:
    return dedent(
        """
        .wikilive-callout {
          margin: 18px 0;
          border-radius: 18px;
          border: 1px solid #e7ebf3;
          background: #fbfcff;
          overflow: hidden;
          box-shadow: 0 12px 26px rgba(17, 24, 39, 0.06);
        }

        .wikilive-callout__head {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 14px;
          border-bottom: 1px solid #eef2f7;
          font-weight: 800;
          font-size: 13px;
          color: #2a3140;
          background: #f8fafc;
          user-select: none;
        }

        .wikilive-callout__icon {
          width: 24px;
          height: 24px;
          border-radius: 999px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: 13px;
          font-weight: 800;
          background: #ffffff;
          border: 1px solid #e7ebf3;
          flex: none;
        }

        .wikilive-callout__title {
          min-width: 0;
          flex: 1;
        }

        .wikilive-callout__body {
          padding: 14px;
          min-height: 56px;
          outline: none;
        }

        .wikilive-callout__body:empty::before {
          content: attr(data-placeholder);
          color: #9aa3b3;
        }

        .wikilive-callout--info {
          border-color: #d6e6ff;
          background: #f7fbff;
        }

        .wikilive-callout--warning {
          border-color: #ffe2a8;
          background: #fffaf0;
        }

        .wikilive-callout--success {
          border-color: #cfead6;
          background: #f6fdf8;
        }

        .wikilive-callout--note {
          border-color: #eadffd;
          background: #fbf8ff;
        }

        .wikilive-template {
          margin: 18px 0;
          border: 1px dashed #d9deea;
          border-radius: 18px;
          background: #fcfdff;
          padding: 16px 18px;
        }

        .wikilive-template h3 {
          margin: 0 0 12px;
          font-size: 16px;
          color: #232833;
        }

        .wikilive-template p {
          margin: 8px 0;
        }

        .wikilive-template ul {
          margin: 10px 0 0 18px;
          padding: 0;
        }

        .wikilive-template li {
          margin: 6px 0;
        }

        .wikilive-plugin-focus {
          box-shadow: 0 0 0 3px rgba(255, 0, 50, 0.08);
        }
        """
    ).strip()


def editor_plugins_script() -> str:
    return dedent(
        r"""
        (function () {
          if (window.__wikiliveEditorPluginsBooted) {
            return;
          }
          window.__wikiliveEditorPluginsBooted = true;

          function getSafeBodyEditor(ctx) {
            return ctx?.bodyEditor || document.getElementById("bodyEditor") || null;
          }

          function escapeHtml(value) {
            return String(value || "")
              .replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#39;");
          }

          function ensureParagraphAfter(node) {
            if (!node || !node.parentNode) return null;

            const next = node.nextElementSibling;
            if (next && (next.matches("p") || next.matches("div"))) {
              return next;
            }

            const paragraph = document.createElement("p");
            paragraph.innerHTML = "<br>";
            node.insertAdjacentElement("afterend", paragraph);
            return paragraph;
          }

          function placeCaretInside(node) {
            if (!node) return;
            const selection = window.getSelection();
            if (!selection) return;

            const range = document.createRange();
            range.selectNodeContents(node);
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);
          }

          function getTopLevelNodeWithinEditor(node, editor) {
            if (!node || !editor) return null;

            let current = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
            while (current && current.parentElement && current.parentElement !== editor) {
              current = current.parentElement;
            }

            if (current && current.parentElement === editor) {
              return current;
            }

            return null;
          }

          function removeSlashTriggerText(ctx) {
            const bodyEditor = getSafeBodyEditor(ctx);
            if (!bodyEditor) return;

            const selection = window.getSelection();
            if (!selection || !selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            if (!bodyEditor.contains(range.commonAncestorContainer)) return;

            let container = range.startContainer;
            if (!container) return;

            if (container.nodeType !== Node.TEXT_NODE) {
              const textNode = Array.from(container.childNodes).find((node) => node.nodeType === Node.TEXT_NODE);
              if (!textNode) return;
              container = textNode;
            }

            const text = container.textContent || "";
            const cursorOffset = Math.min(range.startOffset, text.length);
            const beforeCursor = text.slice(0, cursorOffset);

            const slashIndex = beforeCursor.lastIndexOf("/");
            if (slashIndex === -1) return;

            const triggerText = beforeCursor.slice(slashIndex);
            if (!/^\/[^\s]*$/.test(triggerText)) return;

            container.textContent = text.slice(0, slashIndex) + text.slice(cursorOffset);

            const nextOffset = slashIndex;
            const newRange = document.createRange();
            newRange.setStart(container, Math.min(nextOffset, container.textContent.length));
            newRange.collapse(true);
            selection.removeAllRanges();
            selection.addRange(newRange);
          }

          function insertBlockIntoEditor(block, bodyEditor) {
            if (!bodyEditor || !block) return null;

            const selection = window.getSelection();
            const range = selection && selection.rangeCount ? selection.getRangeAt(0) : null;

            if (!range || !bodyEditor.contains(range.commonAncestorContainer)) {
              bodyEditor.appendChild(block);
              const tail = ensureParagraphAfter(block);
              placeCaretInside(tail || bodyEditor);
              return block;
            }

            const currentBlock = getTopLevelNodeWithinEditor(range.startContainer, bodyEditor);
            if (currentBlock && currentBlock !== bodyEditor) {
              currentBlock.insertAdjacentElement("afterend", block);
            } else {
              bodyEditor.appendChild(block);
            }

            const tail = ensureParagraphAfter(block);
            placeCaretInside(tail || bodyEditor);
            return block;
          }

          function queueEditorSave(label, author) {
            try {
              window.scheduleCommentDocumentSave?.(label || "Изменение документа", author || "editor");
            } catch (error) {
              console.warn("Plugin save schedule failed", error);
            }
          }

          window.notifyEditorChanged = function notifyEditorChanged(ctx, options) {
            const opts = options || {};
            const root = getSafeBodyEditor(ctx) || document;

            try {
              if (typeof window.runEditorPluginHydrators === "function") {
                window.runEditorPluginHydrators(root);
              }

              ctx?.saveCurrentRange?.();
              ctx?.renderOutline?.();
              ctx?.updateActiveToolbarButtons?.();
              ctx?.updateSelectionToolbar?.();

              if (!opts.skipSave) {
                queueEditorSave(opts.label || "Вставка блока", opts.author || "editor");
              }
            } catch (error) {
              console.warn("Failed to sync editor after plugin insert", error);
            }
          };

          function attachEditableListeners(root, onChange) {
            if (!root) return;

            const editables = root.querySelectorAll('[contenteditable="true"]');
            editables.forEach((node) => {
              if (node.dataset.wikilivePluginBound === "1") return;
              node.dataset.wikilivePluginBound = "1";

              node.addEventListener("input", () => {
                onChange?.();
              });

              node.addEventListener("focus", () => {
                root.classList.add("wikilive-plugin-focus");
              });

              node.addEventListener("blur", () => {
                root.classList.remove("wikilive-plugin-focus");
              });
            });
          }

          function createCalloutBlock(type, title, bodyText) {
            const block = document.createElement("div");
            block.className = `wikilive-callout wikilive-callout--${type}`;
            block.dataset.kind = "plugin-callout";
            block.dataset.pluginType = type;
            block.dataset.commentObject = "1";
            block.contentEditable = "false";

            const iconMap = {
              info: "i",
              warning: "!",
              success: "✓",
              note: "✎"
            };

            block.innerHTML = `
              <div class="wikilive-callout__head">
                <span class="wikilive-callout__icon">${escapeHtml(iconMap[type] || "i")}</span>
                <span class="wikilive-callout__title">${escapeHtml(title || "Блок")}</span>
              </div>
              <div
                class="wikilive-callout__body"
                contenteditable="true"
                data-placeholder="Введите текст..."
              >${bodyText || ""}</div>
            `;
            return block;
          }

          function createTemplateBlock(templateKey) {
            const block = document.createElement("div");
            block.className = "wikilive-template";
            block.dataset.kind = "plugin-template";
            block.dataset.pluginType = templateKey;
            block.dataset.commentObject = "1";
            block.contentEditable = "true";

            if (templateKey === "meeting") {
              block.innerHTML = `
                <h3>Заметки встречи</h3>
                <p><strong>Дата:</strong> </p>
                <p><strong>Участники:</strong> </p>
                <p><strong>Повестка:</strong> </p>
                <ul>
                  <li>Пункт 1</li>
                  <li>Пункт 2</li>
                </ul>
                <p><strong>Следующие шаги:</strong> </p>
              `;
            } else if (templateKey === "decision") {
              block.innerHTML = `
                <h3>Принятое решение</h3>
                <p><strong>Контекст:</strong> </p>
                <p><strong>Решение:</strong> </p>
                <p><strong>Последствия:</strong> </p>
              `;
            } else {
              block.innerHTML = `
                <h3>Список задач</h3>
                <ul>
                  <li>[ ] Задача 1</li>
                  <li>[ ] Задача 2</li>
                  <li>[ ] Задача 3</li>
                </ul>
              `;
            }

            return block;
          }

          function hydrateCalloutBlocks(root) {
            const container = root || document;
            const blocks = container.querySelectorAll(".wikilive-callout");

            blocks.forEach((block) => {
              attachEditableListeners(block, () => {
                queueEditorSave("Изменение заметки", "editor");
              });
            });
          }

          function hydrateTemplateBlocks(root) {
            const container = root || document;
            const blocks = container.querySelectorAll(".wikilive-template");

            blocks.forEach((block) => {
              attachEditableListeners(block, () => {
                queueEditorSave("Изменение шаблона", "editor");
              });
            });
          }

          function insertAndSync(ctx, block, label) {
            const bodyEditor = getSafeBodyEditor(ctx);
            if (!bodyEditor || !block) return;

            removeSlashTriggerText(ctx);
            insertBlockIntoEditor(block, bodyEditor);
            window.notifyEditorChanged(ctx, { label: label || "Вставка блока" });
          }

          window.registerEditorPlugin({
            name: "callout-plugin",
            slashItems: [
              { icon: "i", label: "Инфо-блок", queries: ["инфо", "info", "заметка"], kind: "insert", value: "callout-info" },
              { icon: "!", label: "Предупреждение", queries: ["warning", "warn", "предупреждение"], kind: "insert", value: "callout-warning" },
              { icon: "✓", label: "Успешно", queries: ["success", "успех"], kind: "insert", value: "callout-success" },
              { icon: "✎", label: "Заметка", queries: ["note", "заметка"], kind: "insert", value: "callout-note" }
            ],
            inserts: {
              "callout-info": function (ctx) {
                insertAndSync(ctx, createCalloutBlock("info", "Информация"), "Вставка инфо-блока");
              },
              "callout-warning": function (ctx) {
                insertAndSync(ctx, createCalloutBlock("warning", "Предупреждение"), "Вставка предупреждения");
              },
              "callout-success": function (ctx) {
                insertAndSync(ctx, createCalloutBlock("success", "Успешно"), "Вставка блока успеха");
              },
              "callout-note": function (ctx) {
                insertAndSync(ctx, createCalloutBlock("note", "Заметка"), "Вставка заметки");
              }
            },
            hydrate: function (root) {
              hydrateCalloutBlocks(root);
            }
          });

          window.registerEditorPlugin({
            name: "template-plugin",
            slashItems: [
              { icon: "В", label: "Шаблон встречи", queries: ["meeting", "встреча", "митинг"], kind: "insert", value: "template-meeting" },
              { icon: "Р", label: "Шаблон решения", queries: ["decision", "решение"], kind: "insert", value: "template-decision" },
              { icon: "З", label: "Список задач", queries: ["task", "todo", "задачи"], kind: "insert", value: "template-tasklist" }
            ],
            inserts: {
              "template-meeting": function (ctx) {
                insertAndSync(ctx, createTemplateBlock("meeting"), "Вставка шаблона встречи");
              },
              "template-decision": function (ctx) {
                insertAndSync(ctx, createTemplateBlock("decision"), "Вставка шаблона решения");
              },
              "template-tasklist": function (ctx) {
                insertAndSync(ctx, createTemplateBlock("tasklist"), "Вставка списка задач");
              }
            },
            hydrate: function (root) {
              hydrateTemplateBlocks(root);
            }
          });

          if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", function () {
              window.runEditorPluginHydrators?.(document);
            }, { once: true });
          } else {
            window.runEditorPluginHydrators?.(document);
          }
        })();
        """
    ).strip()