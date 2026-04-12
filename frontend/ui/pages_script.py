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

        function getActorPageStorageKey(actorId = currentCommentActorId) {
          return `${commentPageStorageKey}:${normalizeActorId(actorId || "viewer")}`;
        }

        function getCurrentPageSnapshot() {
          return {
            pageId: commentPageId,
            title: titleEditor.textContent.replace(/\u200B/g, "").trim() || "Новая страница",
            description: typeof getDocumentDescriptionText === "function" ? getDocumentDescriptionText() : "",
            content: bodyEditor.innerHTML || "",
            ownerId: normalizeActorId(currentCommentActorId || "viewer"),
            ownerName: getCurrentCommentActor().name || "Гость",
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
            return ownerId === normalizedActorId || sharedWith.includes(normalizedActorId) || sharedWith.includes("*") || true;
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
            const meta = isSharedView
              ? `Автор: ${ownerName}`
              : (headingCount ? `${headingCount} заголовков` : "Без разделов");
            return `
              <button class="pages-switcher__item${isActive ? " is-active" : ""}" data-page-id="${page.pageId}" type="button">
                <span class="pages-switcher__item-title">${escapeHtml(page.title || "Без названия")}</span>
                <span class="pages-switcher__item-meta">${escapeHtml(meta)}</span>
              </button>
            `;
          };

          const sections = [];
          if (ownedPages.length) {
            sections.push(`
              <div class="pages-switcher__section">
                <div class="pages-switcher__section-label">Мои страницы</div>
                ${ownedPages.map((page) => renderPageItem(page, false)).join("")}
              </div>
            `);
          }
          if (sharedPages.length) {
            sections.push(`
              <div class="pages-switcher__section">
                <div class="pages-switcher__section-label">Доступные мне</div>
                ${sharedPages.map((page) => renderPageItem(page, true)).join("")}
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
            const payload = {
              ...serializeEditorDocument(),
              ownerId: normalizeActorId(currentCommentActorId || "viewer"),
              ownerName: getCurrentCommentActor().name || "Гость",
              versionLabel: commentPendingVersionLabel || label || "Изменение текста",
              versionAuthor: commentPendingVersionAuthor || author || "editor",
            };
            const response = await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}`, {
              method: "PUT",
              body: JSON.stringify(payload),
              timeoutMs: 20000
            });
            const savedPage = response.item || {
              pageId: commentPageId,
              ...payload,
              updatedAt: new Date().toISOString(),
            };
            upsertCommentPage(savedPage);
            updateDocumentHeader(savedPage);
            renderPagesSwitcher();
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
          }, 900);
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
          const created = await commentApiRequest("/api/pages", {
            method: "POST",
            body: JSON.stringify({
              title: "Новая страница",
              content: "",
              ownerId: normalizeActorId(currentCommentActorId || "viewer"),
              ownerName: actor.name || "Гость",
              versionLabel: "Создана страница",
              versionAuthor: actor.id || "viewer",
            }),
            timeoutMs: 20000
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
          const ownedPages = getOwnedPagesForActor();
          const accessiblePages = getAccessiblePagesForActor();
          const savedPageId = window.localStorage.getItem(getActorPageStorageKey()) || "";
          const candidatePageId = savedPageId || (ownedPages[0] && ownedPages[0].pageId) || (accessiblePages[0] && accessiblePages[0].pageId) || "";
          if (!candidatePageId) {
            return createPageForCurrentActor(workspaceToken);
          }
          const page = commentPages.find((item) => item.pageId === candidatePageId) || ownedPages[0] || accessiblePages[0];
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

        function initializePagesWorkspace() {
          const newPageButton = document.getElementById("newPageButton");
          const docHeaderTitleButton = document.getElementById("docHeaderTitleButton");

          ensurePagesWorkspaceStyles();
          renderPagesSwitcher();
          renderPagePresence();

          if (pagesTrigger) {
            pagesTrigger.addEventListener("click", (event) => {
              event.stopPropagation();
              pagesSwitcher.classList.toggle("is-open");
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
