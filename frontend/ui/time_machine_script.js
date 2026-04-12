const timeMachineTrigger = document.getElementById("timeMachineTrigger");
const timeMachinePanel = document.getElementById("timeMachinePanel");
const timeMachineClose = document.getElementById("timeMachineClose");
const timeMachineLoading = document.getElementById("timeMachineLoading");
const timeMachineEmpty = document.getElementById("timeMachineEmpty");
const timeMachineError = document.getElementById("timeMachineError");
const timeMachineScroll = document.getElementById("timeMachineScroll");
const timeMachineList = document.getElementById("timeMachineList");
const timeMachinePreview = document.getElementById("timeMachinePreview");
const timeMachinePreviewMeta = document.getElementById("timeMachinePreviewMeta");
const timeMachineRestore = document.getElementById("timeMachineRestore");

let timeMachineVersions = [];
let timeMachineState = "idle";
let timeMachineSelectedVersionId = "";
let timeMachineLoadingPromise = null;
let timeMachineRequestToken = 0;

function formatVersionDate(value) {
  if (!value) {
    return "Без даты";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("ru-RU", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

function getTimeMachineAuthor(author) {
  if (typeof getCommentUser === "function") {
    return getCommentUser(author || "system");
  }
  return {
    name: author || "system",
    short: "i",
    color: "#59c4ff"
  };
}

function getCurrentTimeMachineVersion() {
  return timeMachineVersions.find((item) => item.versionId === timeMachineSelectedVersionId) || null;
}

function renderTimeMachinePanel() {
  if (!timeMachinePanel) {
    return;
  }

  const isOpen = timeMachinePanel.classList.contains("is-open");
  timeMachineLoading.hidden = timeMachineState !== "loading";
  timeMachineError.hidden = timeMachineState !== "error";
  timeMachineEmpty.hidden = !(timeMachineState === "empty" && isOpen);
  timeMachineScroll.hidden = timeMachineState !== "list";

  if (timeMachineState !== "list") {
    timeMachineList.innerHTML = "";
  } else {
    timeMachineList.innerHTML = timeMachineVersions.map((version) => {
      const author = getTimeMachineAuthor(version.author || "system");
      const isActive = version.versionId === timeMachineSelectedVersionId;
      const stats = [];
      if (version.threadCount) {
        stats.push(`<span class="time-machine-item__stat">${version.threadCount} веток</span>`);
      }
      if (version.commentCount) {
        stats.push(`<span class="time-machine-item__stat">${version.commentCount} сообщений</span>`);
      }
      return `
        <button class="time-machine-item${isActive ? " is-active" : ""}" data-time-machine-version="${version.versionId}" type="button">
          <div class="time-machine-item__title">${escapeHtml(version.label || "Действие")}</div>
          <div class="time-machine-item__meta">
            <span>${escapeHtml(formatVersionDate(version.createdAt))}</span>
            <span class="time-machine-item__author">
              <span class="time-machine-item__author-name">${escapeHtml(author.name || version.author || "system")}</span>
              <span class="time-machine-panel__info">
                <svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 2.3a5.7 5.7 0 1 1 0 11.4A5.7 5.7 0 0 1 8 2.3Zm.1 2.4a.95.95 0 1 0 0 1.9.95.95 0 0 0 0-1.9Zm-.9 3v3.7h1.8V7.7H7.2Z"></path></svg>
              </span>
            </span>
          </div>
          ${stats.length ? `<div class="time-machine-item__stats">${stats.join("")}</div>` : ""}
        </button>
      `;
    }).join("");
  }

  const currentVersion = getCurrentTimeMachineVersion();
  const previewVisible = Boolean(currentVersion) && isOpen;
  timeMachinePreview.classList.toggle("is-visible", previewVisible);
  timeMachineRestore.disabled = !previewVisible;
  timeMachinePreviewMeta.textContent = currentVersion
    ? `${currentVersion.label || "Действие"} · ${formatVersionDate(currentVersion.createdAt)}`
    : "Версия не выбрана";
}

async function loadTimeMachineVersions(force = false) {
  const requestToken = ++timeMachineRequestToken;
  if (!commentPageId) {
    if (typeof ensureCommentPage === "function") {
      await ensureCommentPage();
    }
  }
  if (!commentPageId) {
    timeMachineState = "empty";
    renderTimeMachinePanel();
    return [];
  }

  if (timeMachineLoadingPromise && !force) {
    return timeMachineLoadingPromise;
  }

  timeMachineState = "loading";
  renderTimeMachinePanel();

  window.setTimeout(() => {
    if (requestToken === timeMachineRequestToken && timeMachineState === "loading") {
      timeMachineState = "error";
      renderTimeMachinePanel();
    }
  }, 20000);

  timeMachineLoadingPromise = commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/versions`, {
    timeoutMs: 20000
  })
    .then((payload) => {
      timeMachineVersions = (payload.items || []).slice().sort((left, right) => {
        return String(right.createdAt || "").localeCompare(String(left.createdAt || ""));
      });
      if (!timeMachineVersions.length) {
        timeMachineSelectedVersionId = "";
        timeMachineState = "empty";
      } else {
        if (!timeMachineVersions.some((item) => item.versionId === timeMachineSelectedVersionId)) {
          timeMachineSelectedVersionId = timeMachineVersions[0].versionId;
        }
        timeMachineState = "list";
      }
      renderTimeMachinePanel();
      return timeMachineVersions;
    })
    .catch((error) => {
      console.warn("Failed to load time machine versions", error);
      timeMachineState = "error";
      renderTimeMachinePanel();
      return [];
    })
    .finally(() => {
      timeMachineLoadingPromise = null;
    });

  return timeMachineLoadingPromise;
}

async function restoreTimeMachineVersion() {
  const version = getCurrentTimeMachineVersion();
  if (!version || !commentPageId) {
    return;
  }

  try {
    const restored = await commentApiRequest(
      `/api/pages/${encodeURIComponent(commentPageId)}/versions/${encodeURIComponent(version.versionId)}/restore`,
      { method: "POST" }
    );
    const restoredPage = restored.item || restored;
    if (typeof applyEditorDocument === "function") {
      applyEditorDocument(restoredPage);
    }
    if (typeof renderOutline === "function") {
      renderOutline();
    }
    if (typeof syncThreadsFromServer === "function") {
      await syncThreadsFromServer();
    }
    if (typeof renderCommentsPanel === "function") {
      renderCommentsPanel();
    }
    if (typeof scheduleCommentAnchors === "function") {
      scheduleCommentAnchors();
    }
    await loadTimeMachineVersions(true);
  } catch (error) {
    console.warn("Failed to restore version", error);
    timeMachineState = "error";
    renderTimeMachinePanel();
  }
}

function openTimeMachinePanel() {
  if (!timeMachinePanel) {
    return;
  }
  timeMachinePanel.classList.add("is-open");
  if (typeof closeCommentsPanel === "function") {
    closeCommentsPanel();
  }
  if (commentsTopDropdown) {
    commentsTopDropdown.classList.remove("is-open");
  }
  if (commentsAccessPopup) {
    commentsAccessPopup.classList.remove("is-open");
  }
  loadTimeMachineVersions(true).catch(() => {});
}

function closeTimeMachinePanel() {
  if (!timeMachinePanel) {
    return;
  }
  timeMachinePanel.classList.remove("is-open");
  timeMachinePreview.classList.remove("is-visible");
}

function initializeTimeMachine() {
  if (!timeMachineTrigger || !timeMachinePanel) {
    return;
  }

  timeMachineTrigger.addEventListener("click", (event) => {
    event.stopPropagation();
    if (timeMachinePanel.classList.contains("is-open")) {
      closeTimeMachinePanel();
      return;
    }
    openTimeMachinePanel();
  });

  timeMachineClose.addEventListener("click", closeTimeMachinePanel);
  timeMachineRestore.addEventListener("click", () => {
    restoreTimeMachineVersion().catch((error) => console.warn("Failed to restore selected version", error));
  });

  timeMachineList.addEventListener("click", (event) => {
    const item = event.target.closest("[data-time-machine-version]");
    if (!item) {
      return;
    }
    timeMachineSelectedVersionId = item.dataset.timeMachineVersion || "";
    renderTimeMachinePanel();
  });

  document.addEventListener("click", (event) => {
    if (
      timeMachinePanel.classList.contains("is-open") &&
      !timeMachinePanel.contains(event.target) &&
      !timeMachineTrigger.contains(event.target) &&
      !timeMachinePreview.contains(event.target)
    ) {
      closeTimeMachinePanel();
    }
  });

  document.addEventListener("wikilive:page-ready", () => {
    if (timeMachinePanel.classList.contains("is-open")) {
      loadTimeMachineVersions(true).catch(() => {});
    }
  });

  window.refreshTimeMachinePanel = () => {
    if (!timeMachinePanel.classList.contains("is-open")) {
      return Promise.resolve(timeMachineVersions);
    }
    return loadTimeMachineVersions(true);
  };
}

window.initializeTimeMachine = initializeTimeMachine;
