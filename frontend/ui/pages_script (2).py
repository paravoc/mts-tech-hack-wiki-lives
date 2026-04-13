from __future__ import annotations

from textwrap import dedent


def pages_script() -> str:
    return dedent(
        r"""
        function ensurePagesWorkspaceStyles() {
          if (document.getElementById("wikilivePagesWorkspaceStyles")) {
            return;
          }
          const style = document.createElement("style");
          style.id = "wikilivePagesWorkspaceStyles";
          style.textContent = `
            .doc-head__inline-tools {
              display: inline-flex;
              align-items: center;
              gap: 10px;
              min-width: 0;
            }

            .pages-switcher {
              position: relative;
              flex: none;
            }

            .pages-switcher__trigger {
              min-height: 34px;
              padding: 0 12px;
              border: 1px solid #dde2ea;
              border-radius: 999px;
              background: #ffffff;
              color: #4a5568;
              display: inline-flex;
              align-items: center;
              gap: 8px;
              font-size: 12px;
              font-weight: 700;
              box-shadow: 0 8px 18px rgba(17, 24, 39, 0.07);
              transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
            }

            .pages-switcher__trigger:hover,
            .pages-switcher.is-open .pages-switcher__trigger {
              border-color: #cfd6e1;
              box-shadow: 0 12px 22px rgba(17, 24, 39, 0.10);
              transform: translateY(-1px);
            }

            .pages-switcher__count {
              min-width: 18px;
              height: 18px;
              padding: 0 6px;
              border-radius: 999px;
              background: #fff4f6;
              color: #ff0032;
              display: inline-flex;
              align-items: center;
              justify-content: center;
              font-size: 11px;
              font-weight: 800;
            }

            .pages-switcher__menu {
              position: absolute;
              top: calc(100% + 10px);
              left: 0;
              width: 286px;
              max-height: 360px;
              padding: 10px;
              border-radius: 16px;
              border: 1px solid #e3e7ef;
              background: rgba(255, 255, 255, 0.99);
              box-shadow: 0 18px 36px rgba(17, 24, 39, 0.14);
              opacity: 0;
              visibility: hidden;
              transform: translateY(-6px);
              transition: opacity .18s ease, transform .18s ease, visibility .18s ease;
              z-index: 42;
            }

            .pages-switcher.is-open .pages-switcher__menu {
              opacity: 1;
              visibility: visible;
              transform: translateY(0);
            }

            .pages-switcher__menu-head {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 12px;
              margin-bottom: 10px;
            }

            .pages-switcher__menu-title {
              font-size: 13px;
              font-weight: 800;
              color: #222733;
            }

            .pages-switcher__create {
              border: 0;
              border-radius: 10px;
              background: #fff4f6;
              color: #ff0032;
              padding: 7px 10px;
              font-size: 12px;
              font-weight: 700;
            }

            .pages-switcher__list {
              display: flex;
              flex-direction: column;
              gap: 6px;
              max-height: 286px;
              overflow: auto;
              padding-right: 2px;
            }

            .pages-switcher__section {
              display: flex;
              flex-direction: column;
              gap: 6px;
            }

            .pages-switcher__section + .pages-switcher__section {
              margin-top: 10px;
              padding-top: 10px;
              border-top: 1px solid #eef1f6;
            }

            .pages-switcher__section-label {
              font-size: 11px;
              line-height: 1.2;
              font-weight: 800;
              letter-spacing: .04em;
              text-transform: uppercase;
              color: #9aa3b3;
              padding: 0 2px;
            }

            .pages-switcher__item {
              width: 100%;
              border: 1px solid #e7ebf2;
              border-radius: 12px;
              background: #ffffff;
              padding: 10px 11px;
              display: flex;
              flex-direction: column;
              align-items: flex-start;
              gap: 4px;
              text-align: left;
            }

            .pages-switcher__item:hover {
              background: #f7f9fc;
              border-color: #d8dee8;
            }

            .pages-switcher__item.is-active {
              border-color: #ffccd8;
              background: #fff7f9;
            }

            .pages-switcher__item-title {
              font-size: 13px;
              line-height: 1.2;
              font-weight: 700;
              color: #232833;
            }

            .pages-switcher__item-meta {
              font-size: 11px;
              line-height: 1.2;
              color: #8b93a4;
            }

            
            .pages-switcher__footer {
              margin-top: 10px;
              display: flex;
              gap: 8px;
            }

            .pages-switcher__action {
              flex: 1;
              border: 1px solid #e3e7ef;
              border-radius: 10px;
              background: #ffffff;
              color: #4a5568;
              padding: 8px 10px;
              font-size: 12px;
              font-weight: 700;
            }

            .pages-switcher__action:hover {
              background: #f7f9fc;
              border-color: #d6dce7;
            }

            .pages-switcher__action--danger {
              background: #fff4f6;
              color: #ff0032;
              border-color: #ffd2dc;
            }

            .page-access-panel {
              position: fixed;
              top: 96px;
              right: 30px;
              width: 300px;
              padding: 16px;
              border-radius: 16px;
              border: 1px solid #e3e7ef;
              background: #ffffff;
              box-shadow: 0 18px 36px rgba(17, 24, 39, 0.14);
              opacity: 0;
              visibility: hidden;
              transform: translateY(-6px);
              transition: opacity .18s ease, transform .18s ease, visibility .18s ease;
              z-index: 46;
            }

            .page-access-panel.is-open {
              opacity: 1;
              visibility: visible;
              transform: translateY(0);
            }

            .page-access-panel__head {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 8px;
            }

            .page-access-panel__title {
              font-size: 14px;
              font-weight: 800;
              color: #252b36;
            }

            .page-access-panel__close {
              width: 26px;
              height: 26px;
              border: 0;
              border-radius: 999px;
              background: #f4f6fb;
              color: #6b7280;
            }

            .page-access-panel__subtitle {
              margin-top: 6px;
              font-size: 12px;
              color: #8b93a4;
            }

            .page-access-panel__list {
              margin-top: 12px;
              display: flex;
              flex-direction: column;
              gap: 8px;
              max-height: 220px;
              overflow: auto;
            }

            .page-access-item {
              display: flex;
              align-items: center;
              gap: 8px;
              padding: 6px 8px;
              border-radius: 10px;
              background: #f7f9fc;
            }

            .page-access-item input {
              margin: 0;
              accent-color: #ff0032;
            }

            .page-access-item__meta {
              font-size: 11px;
              color: #8b93a4;
            }

            .page-access-panel__actions {
              margin-top: 12px;
              display: flex;
              justify-content: flex-end;
            }

            .page-access-panel__save {
              border: 0;
              border-radius: 10px;
              background: #ff0032;
              color: #ffffff;
              padding: 8px 12px;
              font-size: 12px;
              font-weight: 700;
            }

            .pages-switcher__empty {
              padding: 12px 8px;
              border-radius: 12px;
              background: #f7f9fc;
              color: #8b93a4;
              font-size: 12px;
              text-align: center;
            }

            .page-presence {
              min-height: 34px;
              padding: 4px 8px 4px 6px;
              border: 1px solid #dde2ea;
              border-radius: 999px;
              background: #ffffff;
              box-shadow: 0 8px 18px rgba(17, 24, 39, 0.07);
              display: inline-flex;
              align-items: center;
              gap: 7px;
            }

            .page-presence.is-empty {
              opacity: 0.7;
            }

            .page-presence__avatars {
              display: inline-flex;
              align-items: center;
            }

            .page-presence__avatar {
              width: 22px;
              height: 22px;
              border-radius: 999px;
              border: 2px solid #ffffff;
              display: inline-flex;
              align-items: center;
              justify-content: center;
              color: #ffffff;
              font-size: 11px;
              font-weight: 800;
              margin-left: -6px;
            }

            .page-presence__avatar:first-child {
              margin-left: 0;
            }

            .page-presence__count {
              font-size: 12px;
              line-height: 1;
              font-weight: 800;
              color: #ff0032;
              min-width: 10px;
            }

            .link-menu__section {
              border-top: 1px solid #eef1f6;
              padding-top: 8px;
              margin-top: 8px;
            }

            .link-menu__section:first-child {
              border-top: 0;
              margin-top: 0;
              padding-top: 0;
            }

            .link-menu__section-title {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 8px;
              font-size: 11px;
              line-height: 1.2;
              font-weight: 800;
              letter-spacing: .02em;
              text-transform: uppercase;
              color: #8a93a4;
              margin-bottom: 6px;
            }

            .link-menu__section-subtitle {
              font-size: 11px;
              font-weight: 600;
              color: #b0b7c4;
              text-transform: none;
              letter-spacing: normal;
            }

            .link-menu__section-items {
              display: flex;
              flex-direction: column;
              gap: 6px;
            }

            .link-menu__heading--subtle {
              padding-left: 34px;
            }
          `;
          document.head.appendChild(style);
        }

        let commentWorkspaceToken = 0;
        let commentProjects = [];

        function getActorPageStorageKey(actorId = currentCommentActorId) {
          return `${commentPageStorageKey}:${normalizeActorId(actorId || "viewer")}`;
        }

        function getActorProjectStorageKey(actorId = currentCommentActorId) {
          return `${commentPageStorageKey}:project:${normalizeActorId(actorId || "viewer")}`;
        }

        function getOwnedProjectsForActor(actorId = currentCommentActorId) {
          return (commentProjects || []).filter((project) => normalizeActorId(project.ownerId || "viewer") === normalizeActorId(actorId || "viewer"));
        }

        function getProjectById(projectId) {
          return (commentProjects || []).find((project) => project.projectId === projectId) || null;
        }

        function getProjectLabel(project, fallbackPage = null) {
          if (project && String(project.name || "").trim()) {
            return String(project.name || "").trim();
          }
          const ownerName = String((project && project.ownerName) || (fallbackPage && fallbackPage.ownerName) || "Гость").trim() || "Гость";
          return `Проект ${ownerName}`;
        }

        async function ensureProjectForCurrentActor(forceCatalog = false) {
          await loadPagesCatalog(forceCatalog);
          const actor = getCurrentCommentActor();
          const normalizedActorId = normalizeActorId(currentCommentActorId || "viewer");
          const savedProjectId = window.localStorage.getItem(getActorProjectStorageKey()) || "";
          const ownedProjects = getOwnedProjectsForActor();
          const savedProject = ownedProjects.find((project) => project.projectId === savedProjectId);
          const project = savedProject || ownedProjects[0] || null;
          if (project && project.projectId) {
            window.localStorage.setItem(getActorProjectStorageKey(), project.projectId);
            return project;
          }

          const created = await commentApiRequest("/api/projects", {
            method: "POST",
            body: JSON.stringify({
              name: actor && actor.name ? `Проект ${actor.name}` : "Личный проект",
              description: "Личная рабочая область",
              ownerId: normalizedActorId,
              ownerName: actor.name || "Гость",
              actorId: normalizedActorId,
              sharedWith: [normalizedActorId],
              access: {
                public: false,
                users: [normalizedActorId],
                groups: [],
                roles: []
              }
            }),
            timeoutMs: 30000
          });

          const nextProject = created.item || created;
          if (nextProject && nextProject.projectId) {
            commentProjects = [...(commentProjects || []).filter((item) => item.projectId !== nextProject.projectId), nextProject]
              .sort((left, right) => String(right.updatedAt || "").localeCompare(String(left.updatedAt || "")));
            window.localStorage.setItem(getActorProjectStorageKey(), nextProject.projectId);
            renderPagesSwitcher();
            return nextProject;
          }
          return null;
        }

        loadPagesCatalog = async function(force = false) {
          if (commentPagesPromise && !force) {
            return commentPagesPromise;
          }

          const actorId = normalizeActorId(currentCommentActorId || "viewer");
          commentPagesPromise = commentApiRequest(`/api/workspace?actorId=${encodeURIComponent(actorId)}`, { timeoutMs: 12000 })
            .then((workspaceData) => {
              commentProjects = (workspaceData.projects || []).slice().sort((left, right) => {
                return String(right.updatedAt || "").localeCompare(String(left.updatedAt || ""));
              });
              commentPages = (workspaceData.pages || []).slice().sort((left, right) => {
                return String(right.updatedAt || "").localeCompare(String(left.updatedAt || ""));
              });
              renderPagesSwitcher();
              if (typeof renderLinkHeadingList === "function") {
                renderLinkHeadingList();
              }
              renderBacklinksList();
              return commentPages;
            })
            .finally(() => {
              commentPagesPromise = null;
            });

          return commentPagesPromise;
        };

        function getCurrentPageSnapshot() {
  const currentPage = (commentPages || []).find((page) => page.pageId === commentPageId) || {};
  return {
    pageId: commentPageId,
    title: titleEditor.textContent.replace(/\u200B/g, "").trim() || "Новая страница",
    description: typeof getDocumentDescriptionText === "function" ? getDocumentDescriptionText() : "",
    content: bodyEditor.innerHTML || "",
    ownerId: normalizeActorId(currentCommentActorId || "viewer"),
    ownerName: getCurrentCommentActor().name || "Гость",
    mwsScenarioId: currentPage.mwsScenarioId || "",
    mwsScenarioTitle: currentPage.mwsScenarioTitle || "",
  };
}

        function getOwnedPagesForActor(actorId = currentCommentActorId) {
          return (commentPages || []).filter((page) => normalizeActorId(page.ownerId || "viewer") === normalizeActorId(actorId || "viewer"));
        }

        function getAccessiblePagesForActor(actorId = currentCommentActorId) {
          const normalizedActorId = normalizeActorId(actorId || "viewer");
          return (commentPages || []).filter((page) => {
            const ownerId = normalizeActorId(page.ownerId || "viewer");
            const sharedWith = Array.isArray(page.sharedWith) ? page.sharedWith : [];
            return ownerId === normalizedActorId || sharedWith.includes(normalizedActorId) || sharedWith.includes("*");
          });
        }

        function normalizePageTitleText(value) {
          const text = String(value || "").replace(/\u200B/g, "").replace(/\s+/g, " ").trim();
          return text || "Новая страница";
        }

        function syncCurrentPageSnapshot(partial = {}) {
          if (!commentPageId) {
            return;
          }
          const currentPage = (commentPages || []).find((page) => page.pageId === commentPageId);
          if (!currentPage) {
            return;
          }
          Object.assign(currentPage, partial);
          currentPage.updatedAt = partial.updatedAt || currentPage.updatedAt || new Date().toISOString();
        }

        function focusTitleEditor(selectAll = false) {
          if (!titleEditor) {
            return;
          }
          titleEditor.focus();
          if (selectAll) {
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(titleEditor);
            selection.removeAllRanges();
            selection.addRange(range);
            return;
          }
          placeCaretAtEnd(titleEditor);
        }

        function syncHeaderTitleFromEditor() {
          const normalizedTitle = normalizePageTitleText(titleEditor ? titleEditor.textContent : "");
          if (docHeaderTitle) {
            docHeaderTitle.textContent = normalizedTitle;
          }
          syncCurrentPageSnapshot({ title: normalizedTitle });
          renderPagesSwitcher();
        }

        function closePagesSwitcher() {
          if (pagesSwitcher) {
            pagesSwitcher.classList.remove("is-open");
          }
        }

        function renderPagesSwitcher() {
          if (!pagesSwitcher || !pagesList || !pagesCount) {
            renderPagePresence();
            return;
          }

          const accessiblePages = getAccessiblePagesForActor();
          const ownedPages = accessiblePages.filter((page) => isCurrentActorPage(page));
          const sharedPages = accessiblePages.filter((page) => !isCurrentActorPage(page));
          const projectMap = new Map((commentProjects || []).map((project) => [project.projectId, project]));

          const groupPages = (pages) => {
            const groups = new Map();
            (pages || []).forEach((page) => {
              const key = page.projectId || `owner:${normalizeActorId(page.ownerId || "viewer")}`;
              if (!groups.has(key)) {
                groups.set(key, {
                  key,
                  project: page.projectId ? (projectMap.get(page.projectId) || null) : null,
                  pages: []
                });
              }
              groups.get(key).pages.push(page);
            });
            return Array.from(groups.values()).sort((left, right) => {
              const leftStamp = String((left.project && left.project.updatedAt) || (left.pages[0] && left.pages[0].updatedAt) || "");
              const rightStamp = String((right.project && right.project.updatedAt) || (right.pages[0] && right.pages[0].updatedAt) || "");
              return rightStamp.localeCompare(leftStamp);
            });
          };

          pagesCount.textContent = String(accessiblePages.length);
          if (!accessiblePages.length) {
            pagesList.innerHTML = '<div class="pages-switcher__empty">Пока нет страниц</div>';
            renderPagePresence();
            return;
          }

          const renderPageItem = (page, isSharedView) => {
            const isActive = page.pageId === commentPageId;
            const headingCount = extractPageHeadingTargets(page).filter((item) => item.kind === "heading").length;
            const ownerName = String(page.ownerName || "Гость").trim() || "Гость";
            const scenarioMeta = page.mwsScenarioTitle ? `MWS: ${page.mwsScenarioTitle}` : "";
            const meta = scenarioMeta || (
              isSharedView
                ? `Автор: ${ownerName}`
                : (headingCount ? `${headingCount} заголовков` : "Без разделов")
            );
            return `
              <button class="pages-switcher__item${isActive ? " is-active" : ""}" data-page-id="${page.pageId}" type="button">
                <span class="pages-switcher__item-title">${escapeHtml(page.title || "Без названия")}</span>
                <span class="pages-switcher__item-meta">${escapeHtml(meta)}</span>
              </button>
            `;
          };

          const renderProjectSection = (group, isSharedView = false) => {
            const title = getProjectLabel(group.project, group.pages[0]);
            const subtitle = isSharedView
              ? String((group.project && group.project.ownerName) || (group.pages[0] && group.pages[0].ownerName) || "").trim()
              : `${group.pages.length} ${group.pages.length === 1 ? "страница" : "страниц"}`;
            return `
              <div class="pages-switcher__section">
                <div class="pages-switcher__section-label">${escapeHtml(title)}</div>
                ${subtitle ? `<div class="pages-switcher__section-label pages-switcher__section-label--subtle">${escapeHtml(subtitle)}</div>` : ""}
                ${group.pages.map((page) => renderPageItem(page, isSharedView)).join("")}
              </div>
            `;
          };

          const sections = [];
          const ownedGroups = groupPages(ownedPages);
          const sharedGroups = groupPages(sharedPages);

          if (ownedGroups.length) {
            sections.push(ownedGroups.map((group) => renderProjectSection(group, false)).join(""));
          }
          if (sharedGroups.length) {
            sections.push(`
              <div class="pages-switcher__section">
                <div class="pages-switcher__section-label">Доступные мне проекты</div>
                ${sharedGroups.map((group) => renderProjectSection(group, true)).join("")}
              </div>
            `);
          }

          pagesList.innerHTML = sections.join("");
          renderPagePresence();
        }

        function updatePresenceState(payload) {
          if (!payload || payload.pageId !== commentPageId) {
            return;
          }
          commentPresencePeople = Array.isArray(payload.people) ? payload.people : [];
          renderPagePresence();
        }

        function applyEditorDocumentSafely(page) {
          commentApplyingDocument = true;
          try {
            titleEditor.textContent = (page && page.title) || "Новая страница";
            bodyEditor.innerHTML = page && page.content && page.content.trim()
              ? page.content
              : `<p class="body-placeholder">${emptyHint}</p>`;
            updateDocumentHeader(page || {});
            renderOutline();
            commentLastSavedSnapshot = typeof window.wikiliveBuildVersionSnapshot === "function"
              ? window.wikiliveBuildVersionSnapshot({
                  title: (page && page.title) || "",
                  description: (page && page.description) || "",
                  content: (page && page.content) || ""
                })
              : null;
          } finally {
            window.setTimeout(() => {
              commentApplyingDocument = false;
              scheduleCommentAnchors();
            }, 0);
          }
        }

        applyEditorDocument = function(page) {
          applyEditorDocumentSafely(page);
        };

        async function saveCurrentPageNow(label = "Изменение текста", author = getCurrentCommentActor().id) {
          if (!commentPageId || commentApplyingDocument) {
            return null;
          }
          if (commentSaveTimer) {
            clearTimeout(commentSaveTimer);
            commentSaveTimer = null;
          }
          if (commentSaveInFlight) {
            commentSaveQueued = true;
            queueCommentVersionLabel(label, author);
            return null;
          }

          commentSaveInFlight = true;
          try {
            const documentState = serializeEditorDocument();
            const nextSnapshot = typeof window.wikiliveBuildVersionSnapshot === "function"
              ? window.wikiliveBuildVersionSnapshot(documentState)
              : null;
            const pendingLabel = commentPendingVersionLabel || label || "Изменение текста";
            const payload = {
              ...documentState,
              ownerId: normalizeActorId(currentCommentActorId || "viewer"),
              ownerName: getCurrentCommentActor().name || "Гость",
              versionLabel: typeof window.wikiliveInferDocumentVersionLabel === "function" && typeof isGenericVersionLabel === "function" && isGenericVersionLabel(pendingLabel)
                ? window.wikiliveInferDocumentVersionLabel(commentLastSavedSnapshot, nextSnapshot, pendingLabel)
                : pendingLabel,
              versionAuthor: commentPendingVersionAuthor || author || "editor",
            };
            const response = await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}`, {
              method: "PUT",
              body: JSON.stringify(payload),
              timeoutMs: 30000
            });
            const savedPage = response.item || {
              pageId: commentPageId,
              ...payload,
              updatedAt: new Date().toISOString(),
            };
            upsertCommentPage(savedPage);
            updateDocumentHeader(savedPage);
            renderPagesSwitcher();
            commentLastSavedSnapshot = nextSnapshot;
            commentPendingVersionLabel = "";
            commentPendingVersionAuthor = "";
            if (window.refreshTimeMachinePanel) {
              window.refreshTimeMachinePanel();
            }
            return savedPage;
          } catch (error) {
            console.warn("Failed to save comment page", error);
            return null;
          } finally {
            commentSaveInFlight = false;
            if (commentSaveQueued) {
              commentSaveQueued = false;
              scheduleCommentDocumentSave(commentPendingVersionLabel || label, commentPendingVersionAuthor || author);
            }
          }
        }

        scheduleCommentDocumentSave = function(label = "", author = "editor") {
          if (!commentPageId || commentApplyingDocument) {
            return;
          }
          queueCommentVersionLabel(label || "Изменение текста", author);
          if (commentSaveTimer) {
            clearTimeout(commentSaveTimer);
          }
          commentSaveTimer = window.setTimeout(async () => {
            if (commentSaveInFlight) {
              commentSaveQueued = true;
              return;
            }
            await saveCurrentPageNow(
              commentPendingVersionLabel || label || "Изменение текста",
              commentPendingVersionAuthor || author || "editor"
            );
          }, 1800);
        };

        async function refreshCurrentPageFromServer(force = false) {
          if (!commentPageId) {
            return null;
          }
          const loaded = await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}`, {
            timeoutMs: 15000
          });
          const page = loaded.item || loaded;
          if (!page || !page.pageId) {
            return null;
          }

          upsertCommentPage(page);
          updateDocumentHeader(page);
          const currentTitle = titleEditor.textContent.replace(/\u200B/g, "").trim();
          const currentContent = bodyEditor.innerHTML.trim();
          if (force || currentTitle !== String(page.title || "").trim() || currentContent !== String(page.content || "").trim()) {
            applyEditorDocumentSafely(page);
          }
          renderPagesSwitcher();
          return page;
        }

        function scrollToPageAnchor(anchorId) {
          if (!anchorId) {
            titleEditor.scrollIntoView({ behavior: "smooth", block: "start" });
            return;
          }
          const target = document.getElementById(anchorId);
          if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }

        async function switchCommentPage(pageId, options = {}) {
          if (!pageId) {
            return null;
          }

          const {
            persist = true,
            skipSave = false,
            forceLoad = false,
            anchorId = "",
            discussionTargetId = "",
            workspaceToken = commentWorkspaceToken,
          } = options;

          if (workspaceToken !== commentWorkspaceToken) {
            return null;
          }

          if (commentPageId && commentPageId !== pageId && !skipSave) {
            await saveCurrentPageNow("Сохранение перед переключением", getCurrentCommentActor().id);
          }

          if (!forceLoad && commentPageId === pageId) {
            if (anchorId) {
              window.requestAnimationFrame(() => scrollToPageAnchor(anchorId));
            }
            if (discussionTargetId) {
              window.requestAnimationFrame(() => openThreadForTarget(discussionTargetId, true));
            }
            return getCurrentPageSnapshot();
          }

          const loaded = await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}`, {
            timeoutMs: 15000
          });
          if (workspaceToken !== commentWorkspaceToken) {
            return null;
          }
          const page = loaded.item || loaded;
          if (!page || !page.pageId) {
            return null;
          }

          commentOpenTargetId = null;
          commentReplyTo = null;
          commentMenuOpenId = null;
          commentEditingId = null;
          commentPageId = page.pageId;
          commentPresencePeople = [];
          if (persist) {
            window.localStorage.setItem(getActorPageStorageKey(), commentPageId);
          }

          applyEditorDocumentSafely(page);
          upsertCommentPage(page);
          renderPagesSwitcher();
          renderCommentsPanel();
          renderPagePresence();
          ensureCommentSocket();
          subscribeCommentSocketToPage();
          await ensurePersistedCommentTargets();
          await syncThreadsFromServer(true);
          scheduleCommentAnchors();
          commentBootstrapPromise = Promise.resolve(page);
          document.dispatchEvent(new CustomEvent("wikilive:page-ready", { detail: { pageId: commentPageId } }));
          if (discussionTargetId) {
            window.setTimeout(() => openThreadForTarget(discussionTargetId, true), 120);
          } else if (anchorId) {
            window.setTimeout(() => scrollToPageAnchor(anchorId), 120);
          }
          return page;
        }

        window.switchCommentPageByLink = async function(pageId, anchorId) {
          return switchCommentPage(pageId, { persist: true, anchorId });
        };

        window.openCommentDiscussionTarget = function(targetId) {
          if (!targetId) {
            return;
          }
          openThreadForTarget(targetId, true);
        };

        async function createPageForCurrentActor(workspaceToken = commentWorkspaceToken) {
          const actor = getCurrentCommentActor();
          const mwsContext = window.currentMwsContext || null;
          const project = await ensureProjectForCurrentActor();
          if (!project || !project.projectId) {
            throw new Error("Не удалось подготовить проект для пользователя");
          }

          const created = await commentApiRequest("/api/pages", {
            method: "POST",
            body: JSON.stringify({
              projectId: project.projectId,
              title: mwsContext ? `Страница по ${mwsContext.label || "MWS"}` : "Новая страница",
              content: "",
              ownerId: normalizeActorId(currentCommentActorId || "viewer"),
              ownerName: actor.name || "Гость",
              mwsScenarioId: mwsContext ? (mwsContext.tableId || "") : "",
              mwsScenarioTitle: mwsContext ? (mwsContext.label || "") : "",
              versionLabel: mwsContext ? "Создана страница из сценария MWS" : "Создана страница",
              versionAuthor: actor.id || "viewer",
            }),
            timeoutMs: 30000
          });
          if (workspaceToken !== commentWorkspaceToken) {
            return null;
          }
          const page = created.item || created;
          upsertCommentPage(page);
          renderPagesSwitcher();
          await switchCommentPage(page.pageId, { persist: true, skipSave: true, forceLoad: true, workspaceToken });
          syncHeaderTitleFromEditor();
          return page;
        }

        async function ensureActorPage(forceCatalog = false, workspaceToken = commentWorkspaceToken) {
          await loadPagesCatalog(forceCatalog);
          if (workspaceToken !== commentWorkspaceToken) {
            return null;
          }
          const actorProject = await ensureProjectForCurrentActor(false);
          if (workspaceToken !== commentWorkspaceToken) {
            return null;
          }
          const ownedPages = getOwnedPagesForActor();
          const projectOwnedPages = actorProject && actorProject.projectId
            ? ownedPages.filter((page) => page.projectId === actorProject.projectId)
            : ownedPages;
          const accessiblePages = getAccessiblePagesForActor();
          const savedPageId = window.localStorage.getItem(getActorPageStorageKey()) || "";
          const candidatePageId = savedPageId || (projectOwnedPages[0] && projectOwnedPages[0].pageId) || (ownedPages[0] && ownedPages[0].pageId) || (accessiblePages[0] && accessiblePages[0].pageId) || "";
          if (!candidatePageId) {
            return createPageForCurrentActor(workspaceToken);
          }
          const page = commentPages.find((item) => item.pageId === candidatePageId) || projectOwnedPages[0] || ownedPages[0] || accessiblePages[0];
          if (!page) {
            return createPageForCurrentActor(workspaceToken);
          }
          return switchCommentPage(page.pageId, { persist: true, skipSave: true, forceLoad: true, workspaceToken });
        }

        ensureCommentPage = async function() {
          if (commentBootstrapPromise) {
            return commentBootstrapPromise;
          }

          commentBootstrapPromise = ensureActorPage(true).catch((error) => {
            console.warn("Failed to bootstrap actor page", error);
            commentBootstrapPromise = null;
            return null;
          });
          return commentBootstrapPromise;
        };

        setCurrentCommentActor = function(actorId, persist = true) {
          commentWorkspaceToken += 1;
          currentCommentActorId = actorId || "viewer";
          commentBootstrapPromise = null;
          commentOpenTargetId = null;
          commentReplyTo = null;
          commentMenuOpenId = null;
          commentEditingId = null;
          commentPresencePeople = [];
          commentThreads = new Map();
          if (persist) {
            window.localStorage.setItem(commentActorStorageKey, currentCommentActorId);
          }
          renderActorPicker();
          renderAccountSwitcher();
          renderPagesSwitcher();
          renderCommentsPanel();
          closePagesSwitcher();
          if (accountSwitcher) {
            accountSwitcher.classList.remove("is-open");
          }
          ensureActorPage(true, commentWorkspaceToken).catch((error) => console.warn("Failed to switch actor page", error));
          ensureCommentSocket();
        };

        let commentSocketPresenceKey = "";

        subscribeCommentSocketToPage = function() {
          if (!commentSocket || commentSocket.readyState !== WebSocket.OPEN || !commentPageId) {
            return;
          }

          const actor = getCurrentCommentActor();
          const presenceKey = `${commentPageId}:${normalizeActorId(actor.id || "viewer")}`;
          if (commentSocketPageId && commentSocketPageId !== commentPageId) {
            commentSocket.send(JSON.stringify({ action: "unsubscribe", pageId: commentSocketPageId }));
            commentSocketPresenceKey = "";
          }
          if (commentSocketPageId === commentPageId && commentSocketPresenceKey === presenceKey) {
            return;
          }
          commentSocket.send(JSON.stringify({
            action: "subscribe",
            pageId: commentPageId,
            actorId: normalizeActorId(actor.id || "viewer"),
            actorName: actor.name || "Гость",
            actorShort: actor.short || "Г",
            actorColor: actor.color || "#a6afbf",
          }));
          commentSocketPageId = commentPageId;
          commentSocketPresenceKey = presenceKey;
        };

        ensureCommentSocket = function() {
          if (typeof window.WebSocket !== "function") {
            return;
          }
          if (commentSocket && (commentSocket.readyState === WebSocket.OPEN || commentSocket.readyState === WebSocket.CONNECTING)) {
            subscribeCommentSocketToPage();
            return;
          }

          try {
            commentSocket = new WebSocket(getCommentSocketUrl());
          } catch (error) {
            console.warn("Failed to open comment socket", error);
            return;
          }

          commentSocketPageId = "";
          commentSocketPresenceKey = "";
          commentSocket.addEventListener("open", () => {
            subscribeCommentSocketToPage();
          });
          commentSocket.addEventListener("message", (event) => {
            try {
              const payload = JSON.parse(event.data);
              if (!payload) {
                return;
              }
              if (payload.event === "presence.changed") {
                updatePresenceState(payload);
                return;
              }
              if (payload.pageId !== commentPageId) {
                return;
              }
              if (payload.event === "comments.changed" || payload.event === "comments.access.changed") {
                refreshCommentsFromServer().catch((error) => console.warn("Failed to refresh comments from socket", error));
                return;
              }
              if (payload.event === "page.updated") {
                return;
              }
              if (payload.event === "page.deleted") {
                ensureActorPage(true).catch((error) => console.warn("Failed to recover after page delete", error));
              }
            } catch (error) {
              console.warn("Failed to parse comment socket payload", error);
            }
          });
          commentSocket.addEventListener("close", () => {
            commentSocket = null;
            commentSocketPageId = "";
            commentSocketPresenceKey = "";
            commentPresencePeople = [];
            renderPagePresence();
            if (commentSocketReconnectTimer) {
              clearTimeout(commentSocketReconnectTimer);
            }
            commentSocketReconnectTimer = window.setTimeout(() => {
              ensureCommentSocket();
            }, 1600);
          });
          commentSocket.addEventListener("error", () => {
            if (commentSocket) {
              commentSocket.close();
            }
          });
        };

        navigateToLink = (function(originalNavigateToLink) {
          return function(link) {
            if (!link) {
              return;
            }
            const href = (link.getAttribute("href") || "").trim();
            if (href.startsWith("wikilive://page/")) {
              const match = href.match(/^wikilive:\/\/page\/([^#]+)(?:#(.+))?$/);
              if (match) {
                const pageId = decodeURIComponent(match[1] || "");
                const anchorId = match[2] ? decodeURIComponent(match[2]) : "";
                switchCommentPage(pageId, { persist: true, anchorId }).catch((error) => console.warn("Failed to switch page by link", error));
              }
              return;
            }
            if (href.startsWith("wikilive://discussion/")) {
              const targetId = decodeURIComponent(href.replace("wikilive://discussion/", ""));
              openThreadForTarget(targetId, true);
              return;
            }
            originalNavigateToLink(link);
          };
        })(navigateToLink);

        renderLinkHeadingList = function() {
          if (!linkHeadingList) {
            return;
          }
          const sections = buildWikiLiveLinkSections();
          if (!sections.length) {
            linkHeadingList.innerHTML = '<div class="link-menu__empty">Нет доступных ссылок</div>';
            return;
          }

          linkHeadingList.innerHTML = sections.map((section) => {
            const items = (section.items || []).map((item) => `
              <button
                class="link-menu__heading${item.kind === "heading" ? " link-menu__heading--subtle" : ""}"
                type="button"
                data-heading-target="${item.href}"
              >
                <span class="link-menu__heading-badge">${escapeHtml(item.level || item.kind || "")}</span>
                <span>${escapeHtml(item.label || "Без названия")}</span>
              </button>
            `).join("");

            return `
              <div class="link-menu__section">
                <div class="link-menu__section-title">
                  <span>${escapeHtml(section.title || "Ссылки")}</span>
                  ${section.subtitle ? `<span class="link-menu__section-subtitle">${escapeHtml(section.subtitle)}</span>` : ""}
                </div>
                <div class="link-menu__section-items">${items}</div>
              </div>
            `;
          }).join("");
        };

        
        const pageAccessButton = document.getElementById("pageAccessButton");
        const pageDeleteButton = document.getElementById("pageDeleteButton");
        const pageAccessPanel = document.getElementById("pageAccessPanel");
        const pageAccessClose = document.getElementById("pageAccessClose");
        const pageAccessList = document.getElementById("pageAccessList");
        const pageAccessSave = document.getElementById("pageAccessSave");

        let pageAccessUsers = [];
        let pageAccessGroups = [];

        async function loadPageAccessDirectory() {
          try {
            const [usersResponse, groupsResponse] = await Promise.all([
              commentApiRequest("/api/users", { timeoutMs: 8000 }),
              commentApiRequest("/api/groups", { timeoutMs: 8000 })
            ]);
            pageAccessUsers = Array.isArray(usersResponse.users) ? usersResponse.users : [];
            pageAccessGroups = Array.isArray(groupsResponse.groups) ? groupsResponse.groups : [];
          } catch (error) {
            console.warn("Failed to load access directory, using fallback", error);
            pageAccessUsers = [
              { id: "ivan", name: "Иван Иванов", role: "Автор", team: "WikiLive" },
              { id: "sergei", name: "Сергей Иванов", role: "Редактор", team: "WikiLive" },
              { id: "anton", name: "Антон Серганов", role: "PM", team: "Release" },
              { id: "daria", name: "Дарья Смирнова", role: "Designer", team: "Design" },
              { id: "maxim", name: "Максим Карпов", role: "Backend", team: "Platform" },
            ];
            pageAccessGroups = [];
          }
        }

        function getCurrentPage() {
          return (commentPages || []).find((page) => page.pageId === commentPageId) || null;
        }

        function renderPageAccessPanel() {
          if (!pageAccessList) {
            return;
          }
          const page = getCurrentPage();
          if (!page) {
            pageAccessList.innerHTML = '<div class="page-access-item">Нет активной страницы</div>';
            return;
          }
          const ownerId = normalizeActorId(page.ownerId || "viewer");
          const sharedWith = Array.isArray(page.sharedWith) ? page.sharedWith : [];
          const groupItems = (pageAccessGroups || []).map((group) => {
            return `
              <label class="page-access-item">
                <input type="checkbox" data-group="${escapeHtml(group.id)}" />
                <span>
                  <div>${escapeHtml(group.name)}</div>
                  <div class="page-access-item__meta">Группа • ${escapeHtml(group.id)}</div>
                </span>
              </label>
            `;
          }).join("");

          const userItems = pageAccessUsers.map((user) => {
            const normalized = normalizeActorId(user.id);
            const isOwner = normalized === ownerId;
            const isChecked = isOwner || sharedWith.includes(normalized) || sharedWith.includes("*");
            return `
              <label class="page-access-item">
                <input type="checkbox" value="${normalized}" ${isChecked ? "checked" : ""} ${isOwner ? "disabled" : ""} />
                <span>
                  <div>${escapeHtml(user.name)}</div>
                  <div class="page-access-item__meta">${escapeHtml(user.role || "Участник")} • ${escapeHtml(user.team || "WikiLive")}</div>
                </span>
              </label>
            `;
          }).join("");

          pageAccessList.innerHTML = groupItems + userItems;
        }

        function openPageAccessPanel() {
          if (!pageAccessPanel) {
            return;
          }
          renderPageAccessPanel();
          pageAccessPanel.classList.add("is-open");
        }

        function closePageAccessPanel() {
          if (pageAccessPanel) {
            pageAccessPanel.classList.remove("is-open");
          }
        }

function initializePagesWorkspace() {
          const newPageButton = document.getElementById("newPageButton");
          const docHeaderTitleButton = document.getElementById("docHeaderTitleButton");

          ensurePagesWorkspaceStyles();
          loadPageAccessDirectory().finally(() => renderPagesSwitcher());
          renderPagePresence();

          if (pagesTrigger) {
            pagesTrigger.addEventListener("click", (event) => {
              event.stopPropagation();
              pagesSwitcher.classList.toggle("is-open");
            });
          }

          if (pageAccessButton) {
            pageAccessButton.addEventListener("click", (event) => {
              event.preventDefault();
              event.stopPropagation();
              openPageAccessPanel();
            });
          }

          if (pageAccessClose) {
            pageAccessClose.addEventListener("click", closePageAccessPanel);
          }

          if (pageAccessSave) {
            pageAccessSave.addEventListener("click", async () => {
              const page = getCurrentPage();
              if (!page) {
                closePageAccessPanel();
                return;
              }
              const ownerId = normalizeActorId(page.ownerId || "viewer");
              const selectedUsers = Array.from(pageAccessList.querySelectorAll('input[type="checkbox"][value]'))
                .filter((input) => input.checked)
                .map((input) => normalizeActorId(input.value))
                .filter((value) => value && value !== ownerId);
              const selectedGroups = Array.from(pageAccessList.querySelectorAll('input[type="checkbox"][data-group]'))
                .filter((input) => input.checked)
                .map((input) => input.dataset.group || "");

              const groupMembers = (pageAccessGroups || [])
                .filter((group) => selectedGroups.includes(group.id))
                .flatMap((group) => group.members || []);

              const selected = Array.from(new Set([...selectedUsers, ...groupMembers]))
                .filter((value) => value && value !== ownerId);
              const previousShared = Array.isArray(page.sharedWith) ? page.sharedWith.map((value) => normalizeActorId(value)) : [];
              const addedAccess = selected.filter((value) => !previousShared.includes(value));
              const removedAccess = previousShared.filter((value) => !selected.includes(value));
              const accessVersionLabel = addedAccess.length && !removedAccess.length
                ? "Добавлены участники к странице"
                : (!addedAccess.length && removedAccess.length
                  ? "Закрыт доступ к странице"
                  : "Обновление доступа");
              const payload = {
                ...serializeEditorDocument(),
                ownerId: page.ownerId || normalizeActorId(currentCommentActorId || "viewer"),
                ownerName: page.ownerName || getCurrentCommentActor().name || "Автор",
                sharedWith: selected,
                versionLabel: accessVersionLabel,
                versionAuthor: getCurrentCommentActor().id || "viewer",
              };
              try {
                const response = await commentApiRequest(`/api/pages/${encodeURIComponent(page.pageId)}`, {
                  method: "PUT",
                  body: JSON.stringify(payload),
                  timeoutMs: 30000,
                });
                const updated = response.item || response;
                if (updated && updated.pageId) {
                  upsertCommentPage(updated);
                  syncCurrentPageSnapshot({ sharedWith: selected });
                  renderPagesSwitcher();
                }
              } catch (error) {
                console.warn("Failed to save page access", error);
              }
              closePageAccessPanel();
            });
          }

          document.addEventListener("click", (event) => {
            if (pageAccessPanel && pageAccessPanel.classList.contains("is-open")) {
              if (!pageAccessPanel.contains(event.target) && !pageAccessButton.contains(event.target)) {
                closePageAccessPanel();
              }
            }
          });

          if (pageDeleteButton) {
            pageDeleteButton.addEventListener("click", async (event) => {
              event.preventDefault();
              event.stopPropagation();
              const page = getCurrentPage();
              if (!page) {
                return;
              }
              const ownerId = normalizeActorId(page.ownerId || "viewer");
              const actorId = normalizeActorId(currentCommentActorId || "viewer");
              if (ownerId !== actorId && !isCommentAdmin(actorId)) {
                return;
              }
              if (!window.confirm("Удалить страницу?")) {
                return;
              }
              try {
                await commentApiRequest(`/api/pages/${encodeURIComponent(page.pageId)}`, {
                  method: "DELETE",
                  timeoutMs: 15000,
                });
                commentPages = (commentPages || []).filter((item) => item.pageId !== page.pageId);
                renderPagesSwitcher();
                closePagesSwitcher();
                closePageAccessPanel();
                await ensureActorPage(true);
              } catch (error) {
                console.warn("Failed to delete page", error);
              }
            });
          }

          const createAndFocusPage = () => {
            createPageForCurrentActor().then(() => {
              closePagesSwitcher();
              window.setTimeout(() => focusTitleEditor(true), 80);
            }).catch((error) => console.warn("Failed to create page", error));
          };

          if (pagesCreateButton) {
            pagesCreateButton.addEventListener("click", (event) => {
              event.preventDefault();
              event.stopPropagation();
              createAndFocusPage();
            });
          }

          if (newPageButton) {
            newPageButton.addEventListener("click", (event) => {
              event.preventDefault();
              event.stopPropagation();
              createAndFocusPage();
            });
          }

          if (docHeaderTitleButton) {
            docHeaderTitleButton.addEventListener("click", (event) => {
              event.preventDefault();
              event.stopPropagation();
              focusTitleEditor(true);
            });
          }

          if (pagesList) {
            pagesList.addEventListener("click", (event) => {
              const pageButton = event.target.closest("[data-page-id]");
              if (!pageButton) {
                return;
              }
              switchCommentPage(pageButton.dataset.pageId || "", { persist: true }).then(() => {
                closePagesSwitcher();
              }).catch((error) => console.warn("Failed to switch page", error));
            });
          }

          if (titleEditor) {
            titleEditor.addEventListener("keydown", (event) => {
              if (event.key === "Enter") {
                event.preventDefault();
              }
            });

            titleEditor.addEventListener("input", () => {
              syncHeaderTitleFromEditor();
              scheduleCommentDocumentSave("Изменено название страницы", getCurrentCommentActor().id);
            });

            titleEditor.addEventListener("blur", () => {
              const normalizedTitle = normalizePageTitleText(titleEditor.textContent);
              titleEditor.textContent = normalizedTitle;
              syncHeaderTitleFromEditor();
            });
          }

          document.addEventListener("click", (event) => {
            if (pagesSwitcher && !pagesSwitcher.contains(event.target)) {
              closePagesSwitcher();
            }
          });
        }

        initializePagesWorkspace();
        """
    ).strip()
