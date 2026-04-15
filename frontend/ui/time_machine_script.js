﻿console.error("TIME MACHINE SCRIPT VERSION 2 LOADED");
const timeMachineTrigger = document.getElementById("timeMachineTrigger");
const timeMachinePanel = document.getElementById("timeMachinePanel");
const timeMachineClose = document.getElementById("timeMachineClose");
const timeMachineFilters = document.getElementById("timeMachineFilters");
const timeMachineLoading = document.getElementById("timeMachineLoading");
const timeMachineEmpty = document.getElementById("timeMachineEmpty");
const timeMachineError = document.getElementById("timeMachineError");
const timeMachineErrorMessage = document.getElementById("timeMachineErrorMessage");
const timeMachineRetry = document.getElementById("timeMachineRetry");
const timeMachineScroll = document.getElementById("timeMachineScroll");
const timeMachineList = document.getElementById("timeMachineList");
const timeMachineBuild = document.getElementById("timeMachineBuild");
const timeMachinePreview = document.getElementById("timeMachinePreview");
const timeMachinePreviewTitle = document.getElementById("timeMachinePreviewTitle");
const timeMachinePreviewMeta = document.getElementById("timeMachinePreviewMeta");
const timeMachinePreviewChips = document.getElementById("timeMachinePreviewChips");
const timeMachinePreviewBody = document.getElementById("timeMachinePreviewBody");
const timeMachineRestore = document.getElementById("timeMachineRestore");
const timeMachineClear = document.getElementById("timeMachineClear");

let timeMachineVersions = [];
let timeMachineState = "idle";
let timeMachinePreviewState = "idle";
let timeMachineSelectedVersionId = "";
let timeMachineLoadingPromise = null;
let timeMachineRequestToken = 0;
let timeMachinePreviewToken = 0;
let timeMachineFilter = "all";
let timeMachinePreviewError = "";
let timeMachineErrorText = "";
let timeMachineWatchdogId = 0;
let timeMachinePreviewWatchdogId = 0;
let lastMeaningfulVersionSignature = "";
const timeMachineVersionDetails = new Map();
const timeMachineVersionDetailPromises = new Map();
const TIME_MACHINE_WATCHDOG_MS = 10000;

function tmEscape(value) {
  if (typeof escapeHtml === "function") {
    return escapeHtml(value);
  }
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function tmText(value) {
  return String(value || "").replace(/\u200B/g, "").replace(/\s+/g, " ").trim();
}

function buildMeaningfulVersionSignature(version) {
  if (!version) return "";

  const title = tmText(version.title || "");
  const description = tmText(version.description || "");
  const content = tmText(version.content || "");
  const sharedWith = Array.isArray(version.sharedWith)
    ? [...version.sharedWith].map((item) => String(item || "").trim()).sort().join("|")
    : "";
  const commentAccessMode = tmText(version.commentAccessMode || "all_users");

  return [title, description, content, sharedWith, commentAccessMode].join("::");
}

function filterMeaningfulVersions(items = []) {
  let previousSignature = "";
  const result = [];

  for (const item of items) {
    const signature = buildMeaningfulVersionSignature(item);
    if (!signature) continue;

    if (signature === previousSignature) {
      continue;
    }

    result.push(item);
    previousSignature = signature;
  }

  return result;
}

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

function pluralizeRu(count, one, few, many) {
  const value = Math.abs(Number(count) || 0);
  const mod10 = value % 10;
  const mod100 = value % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few;
  return many;
}

function getTimeMachineAuthor(author) {
  if (typeof getCommentUser === "function") {
    return getCommentUser(author || "system");
  }
  if (typeof pageAccessUsers !== "undefined" && Array.isArray(pageAccessUsers)) {
    const matched = pageAccessUsers.find((item) => String(item.id || "").toLowerCase() === String(author || "").toLowerCase());
    if (matched) {
      return {
        name: matched.name || author || "system",
        short: String(matched.name || author || "i").trim().charAt(0).toUpperCase() || "I",
        color: matched.color || "#59c4ff"
      };
    }
  }
  return { name: author || "system", short: "I", color: "#59c4ff" };
}

function resolveActorName(actorId) {
  return getTimeMachineAuthor(actorId || "viewer").name || String(actorId || "Участник");
}

function resolveSharedNames(ids = []) {
  return ids.map((id) => resolveActorName(id));
}

function formatAccessMode(mode) {
  return mode === "owner_only" ? "только создатель страницы" : "все пользователи";
}

function classifyVersionKind(label) {
  const normalized = tmText(label).toLowerCase();
  if (normalized.includes("изображ") || normalized.includes("медиа") || normalized.includes("объект")) return { key: "media", badge: "Медиа", filterKey: "media" };
  if (normalized.includes("таблиц") || normalized.includes("данн") || normalized.includes("mws")) return { key: "data", badge: "MWS", filterKey: "mws" };
  if (normalized.includes("ссыл")) return { key: "link", badge: "Ссылка", filterKey: "text" };
  if (normalized.includes("обсужд") || normalized.includes("коммент") || normalized.includes("пауз") || normalized.includes("реш")) return { key: "discussion", badge: "Обсуждение", filterKey: "discussion" };
  if (normalized.includes("доступ") || normalized.includes("участник")) return { key: "access", badge: "Доступ", filterKey: "access" };
  if (normalized.includes("восстанов") || normalized.includes("верс")) return { key: "restore", badge: "Версия", filterKey: "text" };
  return { key: "text", badge: "Текст", filterKey: "text" };
}

function isBackendUnavailableError(error) {
  const message = String((error && error.message) || error || "").toLowerCase();
  return message.includes("failed to fetch") ||
    message.includes("connection refused") ||
    message.includes("networkerror");
}

function formatTimeMachineRequestError(error) {
  if (isBackendUnavailableError(error)) {
    return "Backend на 127.0.0.1:3000 недоступен. Запусти сервер и нажми «Повторить».";
  }
  return error && error.message ? error.message : "Не удалось загрузить версии. Попробуйте еще раз.";
}

function getTimeMachineSummaryById(versionId) {
  return timeMachineVersions.find((item) => item.versionId === versionId) || null;
}

function getCurrentTimeMachineVersion() {
  return getTimeMachineSummaryById(timeMachineSelectedVersionId);
}

function getFilteredTimeMachineVersions() {
  return timeMachineFilter === "all"
    ? timeMachineVersions
    : timeMachineVersions.filter((item) => ((item.kind && item.kind.filterKey) || "text") === timeMachineFilter);
}

function limitItems(items, count = 3) {
  return Array.isArray(items) ? items.slice(0, count) : [];
}

function clearTimeMachineWatchdog() {
  if (timeMachineWatchdogId) {
    window.clearTimeout(timeMachineWatchdogId);
    timeMachineWatchdogId = 0;
  }
}

function clearTimeMachinePreviewWatchdog() {
  if (timeMachinePreviewWatchdogId) {
    window.clearTimeout(timeMachinePreviewWatchdogId);
    timeMachinePreviewWatchdogId = 0;
  }
}

function setTimeMachineErrorState(message) {
  timeMachineErrorText = message || "Не удалось загрузить версии. Попробуйте еще раз.";
  timeMachineState = "error";
  renderTimeMachinePanel();
}

function hardResetTimeMachineState() {
  clearTimeMachineWatchdog();
  clearTimeMachinePreviewWatchdog();
  timeMachineLoadingPromise = null;
  timeMachineRequestToken += 1;
  timeMachinePreviewToken += 1;
  timeMachineState = "idle";
  timeMachinePreviewState = "idle";
  timeMachinePreviewError = "";
  timeMachineErrorText = "";
  timeMachineSelectedVersionId = "";
  timeMachineVersions = [];
  timeMachineVersionDetails.clear();
  timeMachineVersionDetailPromises.clear();
  if (timeMachineList) {
    timeMachineList.innerHTML = "";
  }
}

function syncTimeMachineSelection() {
  const filtered = getFilteredTimeMachineVersions();
  if (!filtered.length) {
    timeMachineSelectedVersionId = "";
    return;
  }
  if (!filtered.some((item) => item.versionId === timeMachineSelectedVersionId)) {
    timeMachineSelectedVersionId = filtered[0].versionId;
  }
}

function getTimeMachineSnapshot(version) {
  if (!version) {
    return { title: "", description: "", contentHtml: "", contentParagraphs: [], contentLines: [], linkCount: 0, imageCount: 0, fileCount: 0, dataCount: 0 };
  }
  if (typeof window.wikiliveBuildVersionSnapshot === "function") {
    return window.wikiliveBuildVersionSnapshot({ title: version.title || "", description: version.description || "", content: version.content || "" });
  }
  return { title: tmText(version.title), description: tmText(version.description), contentHtml: version.content || "", contentParagraphs: [], contentLines: tmText(version.content || "").split(/\n+/).filter(Boolean), linkCount: 0, imageCount: 0, fileCount: 0, dataCount: 0 };
}

function buildTimeMachineSequenceDiff(beforeItems = [], afterItems = []) {
  const left = Array.isArray(beforeItems) ? beforeItems : [];
  const right = Array.isArray(afterItems) ? afterItems : [];
  const dp = Array.from({ length: left.length + 1 }, () => Array(right.length + 1).fill(0));

  for (let leftIndex = left.length - 1; leftIndex >= 0; leftIndex -= 1) {
    for (let rightIndex = right.length - 1; rightIndex >= 0; rightIndex -= 1) {
      dp[leftIndex][rightIndex] = left[leftIndex] === right[rightIndex]
        ? dp[leftIndex + 1][rightIndex + 1] + 1
        : Math.max(dp[leftIndex + 1][rightIndex], dp[leftIndex][rightIndex + 1]);
    }
  }

  const operations = [];
  let leftIndex = 0;
  let rightIndex = 0;
  while (leftIndex < left.length && rightIndex < right.length) {
    if (left[leftIndex] === right[rightIndex]) {
      operations.push({ type: "equal", value: left[leftIndex] });
      leftIndex += 1;
      rightIndex += 1;
      continue;
    }
    if (dp[leftIndex + 1][rightIndex] >= dp[leftIndex][rightIndex + 1]) {
      operations.push({ type: "removed", value: left[leftIndex] });
      leftIndex += 1;
    } else {
      operations.push({ type: "added", value: right[rightIndex] });
      rightIndex += 1;
    }
  }

  while (leftIndex < left.length) {
    operations.push({ type: "removed", value: left[leftIndex] });
    leftIndex += 1;
  }
  while (rightIndex < right.length) {
    operations.push({ type: "added", value: right[rightIndex] });
    rightIndex += 1;
  }

  return operations;
}

function splitTimeMachineOperations(operations = []) {
  const changed = [];
  const added = [];
  const removed = [];
  let pendingAdded = [];
  let pendingRemoved = [];

  const flushPending = () => {
    const pairCount = Math.min(pendingAdded.length, pendingRemoved.length);
    for (let index = 0; index < pairCount; index += 1) {
      changed.push({
        before: pendingRemoved[index],
        after: pendingAdded[index]
      });
    }
    if (pendingRemoved.length > pairCount) {
      removed.push(...pendingRemoved.slice(pairCount));
    }
    if (pendingAdded.length > pairCount) {
      added.push(...pendingAdded.slice(pairCount));
    }
    pendingAdded = [];
    pendingRemoved = [];
  };

  operations.forEach((operation) => {
    if (!operation || operation.type === "equal") {
      flushPending();
      return;
    }
    if (operation.type === "added") {
      pendingAdded.push(operation.value);
      return;
    }
    if (operation.type === "removed") {
      pendingRemoved.push(operation.value);
    }
  });
  flushPending();

  return { changed, added, removed };
}

function computeTimeMachineLineDiff(beforeLines = [], afterLines = []) {
  const operations = buildTimeMachineSequenceDiff(beforeLines, afterLines);
  return {
    added: operations.filter((operation) => operation.type === "added").map((operation) => operation.value),
    removed: operations.filter((operation) => operation.type === "removed").map((operation) => operation.value)
  };
}

function computeTimeMachineParagraphDiff(beforeParagraphs = [], afterParagraphs = []) {
  return splitTimeMachineOperations(buildTimeMachineSequenceDiff(beforeParagraphs, afterParagraphs));
}

function decorateTimeMachineVersions(items) {
  const sorted = (items || []).slice().sort((left, right) => String(right.createdAt || "").localeCompare(String(left.createdAt || "")));
  return sorted.map((version, index) => {
    const previousVersion = sorted[index + 1] || null;
    const kind = classifyVersionKind(version.label || "");
    const threadDelta = Number(version.threadCount || 0) - Number(previousVersion && previousVersion.threadCount || 0);
    const commentDelta = Number(version.commentCount || 0) - Number(previousVersion && previousVersion.commentCount || 0);
    const currentShared = Array.isArray(version.sharedWith) ? version.sharedWith : [];
    const previousShared = Array.isArray(previousVersion && previousVersion.sharedWith) ? previousVersion.sharedWith : [];
    const addedShared = currentShared.filter((item) => !previousShared.includes(item)).length;
    const removedShared = previousShared.filter((item) => !currentShared.includes(item)).length;
    const accessModeChanged = Boolean(previousVersion) && (version.commentAccessMode || "all_users") !== (previousVersion.commentAccessMode || "all_users");
    let summary = "Изменены абзацы, заголовок или описание страницы";
    if (kind.filterKey === "access") {
      const parts = [];
      if (addedShared) parts.push(`+${addedShared} ${pluralizeRu(addedShared, "участник", "участника", "участников")}`);
      if (removedShared) parts.push(`-${removedShared} ${pluralizeRu(removedShared, "участник", "участника", "участников")}`);
      if (accessModeChanged) parts.push("режим комментариев");
      summary = parts.length ? parts.join(" • ") : "Изменены права доступа к странице";
    } else if (kind.filterKey === "discussion") {
      const parts = [];
      if (threadDelta > 0) parts.push(`+${threadDelta} ${pluralizeRu(threadDelta, "ветка", "ветки", "веток")}`);
      if (commentDelta > 0) parts.push(`+${commentDelta} ${pluralizeRu(commentDelta, "комментарий", "комментария", "комментариев")}`);
      summary = parts.length ? parts.join(" • ") : "Изменены обсуждения и комментарии";
    } else if (kind.filterKey === "media") {
      summary = "Изменены изображения, файлы или медиаблоки";
    } else if (kind.filterKey === "mws") {
      summary = "Обновлены данные и подстановки MWS";
    } else if (kind.key === "restore") {
      summary = "Страница восстановлена из истории версий";
    } else if (kind.key === "link") {
      summary = "Обновлены ссылки внутри документа";
    }
    return { ...version, kind, previousVersionId: previousVersion ? previousVersion.versionId : "", summary };
  });
}

function buildTimeMachineDetailView(summaryVersion, currentDetail, previousDetail) {
  const snapshot = getTimeMachineSnapshot(currentDetail);
  const previousSnapshot = getTimeMachineSnapshot(previousDetail);
  const paragraphDiff = computeTimeMachineParagraphDiff(previousSnapshot.contentParagraphs || previousSnapshot.contentLines || [], snapshot.contentParagraphs || snapshot.contentLines || []);
  const lineDiff = computeTimeMachineLineDiff(previousSnapshot.contentLines || [], snapshot.contentLines || []);
  const currentShared = Array.isArray(currentDetail.sharedWith) ? currentDetail.sharedWith : [];
  const previousShared = Array.isArray(previousDetail && previousDetail.sharedWith) ? previousDetail.sharedWith : [];
  const addedShared = currentShared.filter((item) => !previousShared.includes(item));
  const removedShared = previousShared.filter((item) => !currentShared.includes(item));
  const accessModeChanged = Boolean(previousDetail) && (currentDetail.commentAccessMode || "all_users") !== (previousDetail.commentAccessMode || "all_users");
  const threadDelta = Number(currentDetail.threadCount || 0) - Number(previousDetail && previousDetail.threadCount || 0);
  const commentDelta = Number(currentDetail.commentCount || 0) - Number(previousDetail && previousDetail.commentCount || 0);
  const imageDelta = Number(snapshot.imageCount || 0) - Number(previousSnapshot.imageCount || 0);
  const dataDelta = Number(snapshot.dataCount || 0) - Number(previousSnapshot.dataCount || 0);
  const linkDelta = Number(snapshot.linkCount || 0) - Number(previousSnapshot.linkCount || 0);

  const keyActions = [];
  if (summaryVersion.summary) keyActions.push(summaryVersion.summary);
  if (imageDelta > 0) keyActions.push(`Добавлено ${imageDelta} ${pluralizeRu(imageDelta, "изображение", "изображения", "изображений")}`);
  if (dataDelta > 0) keyActions.push(`Добавлено ${dataDelta} ${pluralizeRu(dataDelta, "блок MWS", "блока MWS", "блоков MWS")}`);
  if (linkDelta > 0) keyActions.push(`Добавлено ${linkDelta} ${pluralizeRu(linkDelta, "ссылка", "ссылки", "ссылок")}`);
  if (threadDelta > 0) keyActions.push(`Открыто ${threadDelta} ${pluralizeRu(threadDelta, "обсуждение", "обсуждения", "обсуждений")}`);
  if (commentDelta > 0) keyActions.push(`Добавлено ${commentDelta} ${pluralizeRu(commentDelta, "комментарий", "комментария", "комментариев")}`);

  const metadataChanges = [];
  if (previousDetail && previousSnapshot.title !== snapshot.title) metadataChanges.push(`Заголовок: «${snapshot.title || "Без названия"}»`);
  if (previousDetail && previousSnapshot.description !== snapshot.description) metadataChanges.push("Изменено описание страницы");
  if (addedShared.length) metadataChanges.push(`Добавлен доступ: ${resolveSharedNames(addedShared).join(", ")}`);
  if (removedShared.length) metadataChanges.push(`Закрыт доступ: ${resolveSharedNames(removedShared).join(", ")}`);
  if (accessModeChanged) metadataChanges.push(`Комментарии: ${formatAccessMode(previousDetail.commentAccessMode)} → ${formatAccessMode(currentDetail.commentAccessMode)}`);

  return {
    title: currentDetail.label || "Действие",
    meta: `${formatVersionDate(currentDetail.createdAt)} • ${resolveActorName(currentDetail.author || "system")}`,
    chips: [
      summaryVersion.kind.badge,
      ...(paragraphDiff.changed.length ? [`Изменено абзацев: ${paragraphDiff.changed.length}`] : []),
      ...(paragraphDiff.added.length ? [`Новых абзацев: ${paragraphDiff.added.length}`] : []),
      ...(paragraphDiff.removed.length ? [`Удалено абзацев: ${paragraphDiff.removed.length}`] : []),
      ...(currentDetail.threadCount ? [`${currentDetail.threadCount} ${pluralizeRu(currentDetail.threadCount, "ветка", "ветки", "веток")}`] : []),
      ...(currentDetail.commentCount ? [`${currentDetail.commentCount} ${pluralizeRu(currentDetail.commentCount, "комментарий", "комментария", "комментариев")}`] : [])
    ],
    keyActions: Array.from(new Set(keyActions.filter(Boolean))),
    metadataChanges,
    paragraphDiff,
    lineDiff
  };
}

function buildPreviewSection(title, innerHtml) {
  return `<section class="time-machine-preview__section"><div class="time-machine-preview__section-title">${tmEscape(title)}</div>${innerHtml}</section>`;
}

function renderPreviewList(items) {
  if (!items || !items.length) {
    return '<div class="time-machine-preview__empty">Изменений в этом блоке нет.</div>';
  }
  return `<div class="time-machine-preview__list">${items.map((item) => `<div class="time-machine-preview__list-item">${tmEscape(item)}</div>`).join("")}</div>`;
}

function renderParagraphCard(label, text, modifier) {
  return `<div class="time-machine-preview__paragraph-card time-machine-preview__paragraph-card--${modifier}"><div class="time-machine-preview__paragraph-label">${tmEscape(label)}</div><div class="time-machine-preview__paragraph-text">${tmEscape(text || "—")}</div></div>`;
}

function renderParagraphDiff(detailView) {
  const blocks = [];
  limitItems(detailView.paragraphDiff.changed, 3).forEach((pair) => {
    blocks.push(`<div class="time-machine-preview__paragraph-pair">${renderParagraphCard("Было", pair.before, "before")}${renderParagraphCard("Стало", pair.after, "after")}</div>`);
  });
  limitItems(detailView.paragraphDiff.added, 2).forEach((paragraph) => blocks.push(renderParagraphCard("Добавлен абзац", paragraph, "added")));
  limitItems(detailView.paragraphDiff.removed, 2).forEach((paragraph) => blocks.push(renderParagraphCard("Удален абзац", paragraph, "removed")));
  if (blocks.length) {
    return `<div class="time-machine-preview__paragraph-stack">${blocks.join("")}</div>`;
  }
  const fallbackLines = [];
  limitItems(detailView.lineDiff.added, 3).forEach((line) => fallbackLines.push(`<span class="time-machine-preview__line time-machine-preview__line--added">+ ${tmEscape(line)}</span>`));
  limitItems(detailView.lineDiff.removed, 3).forEach((line) => fallbackLines.push(`<span class="time-machine-preview__line time-machine-preview__line--removed">- ${tmEscape(line)}</span>`));
  return fallbackLines.length ? fallbackLines.join("") : '<div class="time-machine-preview__empty">В этой версии нет заметных изменений по абзацам.</div>';
}

function renderTimeMachineFilters() {
  if (!timeMachineFilters) return;
  timeMachineFilters.querySelectorAll("[data-time-machine-filter]").forEach((button) => {
    button.classList.toggle("is-active", (button.dataset.timeMachineFilter || "all") === timeMachineFilter);
  });
}

function renderTimeMachineList() {
  if (!timeMachineList) return;

  try {
    const versions = getFilteredTimeMachineVersions();

    timeMachineList.innerHTML = versions.map((version) => {
      const author = getTimeMachineAuthor(version.author || "system");
      const isActive = version.versionId === timeMachineSelectedVersionId;
      const stats = [];

      if (version.threadCount) {
        stats.push(
          `<span class="time-machine-item__stat">${version.threadCount} ${pluralizeRu(version.threadCount, "ветка", "ветки", "веток")}</span>`
        );
      }

      if (version.commentCount) {
        stats.push(
          `<span class="time-machine-item__stat">${version.commentCount} ${pluralizeRu(version.commentCount, "комментарий", "комментария", "комментариев")}</span>`
        );
      }

      return `
        <button class="time-machine-item${isActive ? " is-active" : ""}" data-time-machine-version="${version.versionId}" type="button">
          <div class="time-machine-item__top">
            <div class="time-machine-item__title">${tmEscape(version.label || "Действие")}</div>
            <span class="time-machine-item__badge">${tmEscape((version.kind && version.kind.badge) || "Версия")}</span>
          </div>
          <div class="time-machine-item__summary">${tmEscape(version.summary || "")}</div>
          <div class="time-machine-item__meta">
            <span>${tmEscape(formatVersionDate(version.createdAt))}</span>
            <span class="time-machine-item__author">
              <span class="time-machine-item__author-name">${tmEscape(author.name || version.author || "system")}</span>
              <span class="time-machine-panel__info">
                <svg viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 2.3a5.7 5.7 0 1 1 0 11.4A5.7 5.7 0 0 1 8 2.3Zm.1 2.4a.95.95 0 1 0 0 1.9.95.95 0 0 0 0-1.9Zm-.9 3v3.7h1.8V7.7H7.2Z"></path>
                </svg>
              </span>
            </span>
          </div>
          ${stats.length ? `<div class="time-machine-item__stats">${stats.join("")}</div>` : ""}
        </button>
      `;
    }).join("");
  } catch (error) {
    console.error("renderTimeMachineList failed", error);
    setTimeMachineErrorState("Ошибка отрисовки списка версий");
  }
}

function forceShowTimeMachineList() {
  if (!timeMachineList || !timeMachineScroll) return;

  renderTimeMachineList();

  timeMachineState = "list";

  if (timeMachineLoading) {
    timeMachineLoading.hidden = true;
    timeMachineLoading.style.display = "none";
  }

  if (timeMachineError) {
    timeMachineError.hidden = true;
    timeMachineError.style.display = "none";
  }

  if (timeMachineEmpty) {
    timeMachineEmpty.hidden = true;
    timeMachineEmpty.style.display = "none";
  }

  timeMachineScroll.hidden = false;
  timeMachineScroll.style.display = "";
  timeMachineScroll.style.visibility = "visible";
  timeMachineScroll.style.opacity = "1";

  timeMachineList.hidden = false;
  timeMachineList.style.display = "";
  timeMachineList.style.visibility = "visible";
  timeMachineList.style.opacity = "1";

  console.error("forceShowTimeMachineList done", {
    versions: timeMachineVersions.length,
    htmlLength: timeMachineList.innerHTML.length
  });
}

function renderTimeMachinePreview() {
  if (
    !timeMachinePreview ||
    !timeMachinePreviewTitle ||
    !timeMachinePreviewMeta ||
    !timeMachinePreviewChips ||
    !timeMachinePreviewBody ||
    !timeMachineRestore
  ) {
    console.error("Time machine preview DOM is missing");
    return;
  }

  const currentVersion = getCurrentTimeMachineVersion();
  const previewVisible =
    Boolean(currentVersion) &&
    timeMachinePanel &&
    timeMachinePanel.classList.contains("is-open");

  timeMachinePreview.classList.toggle("is-visible", previewVisible);
  timeMachineRestore.disabled = !previewVisible || timeMachinePreviewState === "loading";

  if (!currentVersion) {
    timeMachinePreviewTitle.textContent = "Предварительный просмотр";
    timeMachinePreviewMeta.textContent = "Версия не выбрана";
    timeMachinePreviewChips.innerHTML = "";
    timeMachinePreviewBody.innerHTML =
      '<div class="time-machine-preview__empty">Выберите действие справа, чтобы увидеть, что именно изменилось.</div>';
    return;
  }

  if (timeMachinePreviewState === "loading") {
    timeMachinePreviewTitle.textContent = currentVersion.label || "Предварительный просмотр";
    timeMachinePreviewMeta.textContent = `${formatVersionDate(currentVersion.createdAt)} • загружаю детали версии`;
    timeMachinePreviewChips.innerHTML =
      `<span class="time-machine-preview__chip">${tmEscape((currentVersion.kind && currentVersion.kind.badge) || "Версия")}</span>`;
    timeMachinePreviewBody.innerHTML =
      '<section class="time-machine-preview__section"><div class="time-machine-panel__state"><div class="time-machine-panel__spinner" aria-hidden="true"></div></div></section>';
    return;
  }

  if (timeMachinePreviewState === "error") {
    timeMachinePreviewTitle.textContent = currentVersion.label || "Предварительный просмотр";
    timeMachinePreviewMeta.textContent = `${formatVersionDate(currentVersion.createdAt)} • детали версии недоступны`;
    timeMachinePreviewChips.innerHTML =
      `<span class="time-machine-preview__chip">${tmEscape((currentVersion.kind && currentVersion.kind.badge) || "Версия")}</span>`;
    timeMachinePreviewBody.innerHTML =
      `<section class="time-machine-preview__section"><div class="time-machine-preview__empty">${tmEscape(timeMachinePreviewError || "Не удалось загрузить детали версии.")}</div></section>`;
    return;
  }

  const detailView = currentVersion.detailView;

  timeMachinePreviewTitle.textContent =
    detailView ? detailView.title : (currentVersion.label || "Предварительный просмотр");
  timeMachinePreviewMeta.textContent =
    detailView ? detailView.meta : `${formatVersionDate(currentVersion.createdAt)} • ${resolveActorName(currentVersion.author || "system")}`;
  timeMachinePreviewChips.innerHTML = detailView
    ? detailView.chips.map((chip) => `<span class="time-machine-preview__chip">${tmEscape(chip)}</span>`).join("")
    : `<span class="time-machine-preview__chip">${tmEscape((currentVersion.kind && currentVersion.kind.badge) || "Версия")}</span>`;

  if (!detailView) {
    timeMachinePreviewBody.innerHTML =
      '<div class="time-machine-preview__empty">Выберите действие справа, чтобы увидеть изменения.</div>';
    return;
  }

  const sections = [
    buildPreviewSection("Ключевые действия", renderPreviewList(detailView.keyActions)),
    buildPreviewSection("Diff по абзацам", renderParagraphDiff(detailView))
  ];

  if (detailView.metadataChanges.length) {
    sections.push(buildPreviewSection("Метаданные и доступ", renderPreviewList(detailView.metadataChanges)));
  }

  timeMachinePreviewBody.innerHTML = sections.join("");
}

function renderTimeMachinePanel() {
  if (!timeMachinePanel) return;

  renderTimeMachineFilters();

  const isOpen = timeMachinePanel.classList.contains("is-open");
  const filtered = getFilteredTimeMachineVersions();

  if (timeMachineLoading) timeMachineLoading.hidden = true;
  if (timeMachineError) timeMachineError.hidden = true;
  if (timeMachineEmpty) timeMachineEmpty.hidden = true;
  if (timeMachineScroll) timeMachineScroll.hidden = true;

  if (timeMachineErrorMessage) {
    timeMachineErrorMessage.textContent =
      timeMachineErrorText || "Не удалось загрузить версии. Попробуйте еще раз";
  }

  if (timeMachineState === "loading") {
    if (timeMachineLoading) timeMachineLoading.hidden = false;
  } else if (timeMachineState === "error") {
    if (timeMachineError) timeMachineError.hidden = false;
  } else if (timeMachineState === "empty") {
    if (timeMachineEmpty) {
      timeMachineEmpty.hidden = false;
      if (isOpen) {
        timeMachineEmpty.textContent = "История действий пока пуста";
      }
    }
    if (timeMachineList) timeMachineList.innerHTML = "";
  } else if (timeMachineState === "list") {
    renderTimeMachineList();

    if (!filtered.length) {
      if (timeMachineEmpty) {
        timeMachineEmpty.hidden = false;
        timeMachineEmpty.textContent = "По выбранному фильтру пока нет версий";
      }
      if (timeMachineScroll) timeMachineScroll.hidden = true;
    } else {
      if (timeMachineScroll) timeMachineScroll.hidden = false;
      if (timeMachineEmpty) {
        timeMachineEmpty.hidden = true;
        timeMachineEmpty.textContent = "История действий пока пуста";
      }
    }
  }

  renderTimeMachinePreview();
}

function setTimeMachinePreviewState(nextState, errorMessage = "") {
  timeMachinePreviewState = nextState;
  timeMachinePreviewError = errorMessage;
  if (nextState !== "loading") {
    clearTimeMachinePreviewWatchdog();
  }
}

async function ensureTimeMachineVersionDetails(versionId, force = false) {
  if (!versionId || !commentPageId) return null;
  if (!force && timeMachineVersionDetails.has(versionId)) return timeMachineVersionDetails.get(versionId);
  if (!force && timeMachineVersionDetailPromises.has(versionId)) return timeMachineVersionDetailPromises.get(versionId);
  const promise = commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/versions/${encodeURIComponent(versionId)}`, { timeoutMs: 30000 })
    .then((payload) => {
      const detail = payload.item || payload || null;
      if (detail) timeMachineVersionDetails.set(versionId, detail);
      return detail;
    })
    .finally(() => {
      timeMachineVersionDetailPromises.delete(versionId);
    });
  timeMachineVersionDetailPromises.set(versionId, promise);
  return promise;
}

async function loadTimeMachinePreview(versionId, force = false, options = {}) {
  const summaryVersion = getTimeMachineSummaryById(versionId);
  if (!summaryVersion || !commentPageId) {
    setTimeMachinePreviewState("idle");
    renderTimeMachinePanel();
    return null;
  }
  const silent = Boolean(options.silent);
  const previewToken = ++timeMachinePreviewToken;

  if (silent && summaryVersion.detailView) {
    return summaryVersion.detailView;
  }

  setTimeMachinePreviewState("loading");
  renderTimeMachinePanel();
  clearTimeMachinePreviewWatchdog();
  timeMachinePreviewWatchdogId = window.setTimeout(() => {
    if (previewToken !== timeMachinePreviewToken) return;
    if (!timeMachinePanel || !timeMachinePanel.classList.contains("is-open")) return;
    if (timeMachinePreviewState !== "loading") return;
    setTimeMachinePreviewState(
      "error",
      "Детали версии не загрузились за 3 секунды. Скорее всего открыт старый iframe. Нажмите Ctrl+F5."
    );
    renderTimeMachinePanel();
  }, TIME_MACHINE_WATCHDOG_MS);

  try {
    const previousSummary = summaryVersion.previousVersionId ? getTimeMachineSummaryById(summaryVersion.previousVersionId) : null;
    const [currentDetail, previousDetail] = await Promise.all([
      ensureTimeMachineVersionDetails(summaryVersion.versionId, force),
      previousSummary ? ensureTimeMachineVersionDetails(previousSummary.versionId, force) : Promise.resolve(null)
    ]);
    if (previewToken !== timeMachinePreviewToken) return null;
    summaryVersion.detailView = buildTimeMachineDetailView(summaryVersion, currentDetail || summaryVersion, previousDetail || null);
    setTimeMachinePreviewState("ready");
    renderTimeMachinePanel();
    return summaryVersion.detailView;
  } catch (error) {
    if (previewToken !== timeMachinePreviewToken) return null;
    console.warn("Failed to load time machine preview", error);
    console.error("TIME MACHINE PREVIEW ERROR:", error);
    setTimeMachinePreviewState(
      "error",
      error && error.message ? error.message : "Не удалось загрузить детали версии."
    );
    renderTimeMachinePanel();
    return null;
  } finally {
    clearTimeMachinePreviewWatchdog();

    if (timeMachinePreviewState === "loading") {
      setTimeMachinePreviewState("error", "Предпросмотр версии завис.");
      renderTimeMachinePanel();
    }
  }
}

async function loadTimeMachineVersions(force = false, options = {}) {
  console.error("loadTimeMachineVersions called", { force, options });

  const requestToken = ++timeMachineRequestToken;
  const silent = Boolean(options && options.silent);

  try {
    if (!commentPageId && typeof ensureCommentPage === "function") {
      console.error("commentPageId empty, calling ensureCommentPage()");
      await ensureCommentPage();
      console.error("commentPageId after ensure =", commentPageId);
    }

    if (!commentPageId) {
      console.error("No commentPageId");
      setTimeMachineErrorState("Не удалось определить текущую страницу для истории изменений.");
      renderTimeMachinePanel();
      return [];
    }

    if (timeMachineLoadingPromise && !force) {
      console.error("Returning existing timeMachineLoadingPromise");
      return timeMachineLoadingPromise;
    }

    if (!silent || !timeMachineVersions.length) {
      timeMachineState = "loading";
      timeMachineErrorText = "";
      renderTimeMachinePanel();
      clearTimeMachineWatchdog();

      timeMachineWatchdogId = window.setTimeout(() => {
        if (requestToken !== timeMachineRequestToken) return;
        if (!timeMachinePanel || !timeMachinePanel.classList.contains("is-open")) return;
        if (timeMachineState !== "loading") return;

        setTimeMachineErrorState(
          "Список версий не загрузился за 10 секунд. Нажмите Ctrl+F5 или кнопку «Повторить»."
        );
      }, TIME_MACHINE_WATCHDOG_MS);
    }

    console.error("Starting commentApiRequest for versions");

    timeMachineLoadingPromise = commentApiRequest(
      `/api/pages/${encodeURIComponent(commentPageId)}/versions`,
      { timeoutMs: 30000 }
    )
      .then((payload) => {
        console.error("versions payload =", payload);

        if (requestToken !== timeMachineRequestToken) {
          console.error("Request token mismatch");
          return timeMachineVersions;
        }

        clearTimeMachineWatchdog();

        const rawItems = Array.isArray(payload?.items)
          ? payload.items
          : Array.isArray(payload)
            ? payload
            : [];

        console.error("versions items =", rawItems);

        const items = filterMeaningfulVersions(rawItems);

        timeMachineVersions = decorateTimeMachineVersions(items);
        console.error("decorated versions =", timeMachineVersions);

        lastMeaningfulVersionSignature = items.length
          ? buildMeaningfulVersionSignature(items[0])
          : "";

        syncTimeMachineSelection();
        console.error("selected version =", timeMachineSelectedVersionId);

        if (!timeMachineVersions.length) {
          timeMachineState = "empty";
          renderTimeMachinePanel();
          return timeMachineVersions;
        }

        timeMachineState = "list";
        console.error("timeMachineState set to list");
        renderTimeMachinePanel();
        forceShowTimeMachineList();
        console.error("versions render done");

        if (timeMachineSelectedVersionId) {
          loadTimeMachinePreview(timeMachineSelectedVersionId, force, { silent: true }).catch((error) => {
            console.error("silent preview preload failed", error);
          });
        }

        return timeMachineVersions;
      })
      .catch((error) => {
        console.error("loadTimeMachineVersions error", error);
        if (requestToken !== timeMachineRequestToken) {
          return timeMachineVersions;
        }
        clearTimeMachineWatchdog();
        setTimeMachineErrorState(formatTimeMachineRequestError(error));
        renderTimeMachinePanel();
        throw error;
      })
      .finally(() => {
        console.error("loadTimeMachineVersions finally");
        if (requestToken === timeMachineRequestToken) {
          timeMachineLoadingPromise = null;
        }
      });

    return await timeMachineLoadingPromise;
  } catch (error) {
    console.error("loadTimeMachineVersions outer error", error);
    if (requestToken === timeMachineRequestToken) {
      clearTimeMachineWatchdog();
      setTimeMachineErrorState(formatTimeMachineRequestError(error));
      renderTimeMachinePanel();
    }
    return [];
  }
}

async function restoreTimeMachineVersion() {
  const version = getCurrentTimeMachineVersion();
  if (!version || !commentPageId) return;

  console.error("[wikilive][tm] restore:start", {
    pageId: commentPageId,
    versionId: version.versionId,
    label: version.label
  });

  try {
    if (timeMachineRestore) {
      timeMachineRestore.disabled = true;
    }

    const restored = await commentApiRequest(
      `/api/pages/${encodeURIComponent(commentPageId)}/versions/${encodeURIComponent(version.versionId)}/restore`,
      { method: "POST", timeoutMs: 30000 }
    );

    const restoredPage = restored.item || restored;
    console.error("[wikilive][tm] restore:response", restoredPage);

    if (!restoredPage || !restoredPage.pageId) {
      throw new Error("Backend не вернул восстановленную страницу");
    }

    if (typeof upsertCommentPage === "function") {
      upsertCommentPage(restoredPage);
    }

    if (typeof syncCurrentPageSnapshot === "function") {
      syncCurrentPageSnapshot({
        pageId: restoredPage.pageId,
        projectId: restoredPage.projectId || "",
        title: restoredPage.title || "",
        description: restoredPage.description || "",
        content: restoredPage.content || "",
        sharedWith: Array.isArray(restoredPage.sharedWith) ? restoredPage.sharedWith : [],
        access: restoredPage.access || { public: false, users: [], groups: [], roles: [] },
        updatedAt: restoredPage.updatedAt || ""
      });
    }

    if (typeof applyEditorDocument === "function") {
      applyEditorDocument(restoredPage);
    }

    if (typeof syncHeaderTitleFromEditor === "function") {
      syncHeaderTitleFromEditor();
    }

    if (typeof renderPagesSwitcher === "function") {
      renderPagesSwitcher();
    }

    if (typeof renderOutline === "function") {
      renderOutline();
    }

    if (typeof renderPageAccessPanel === "function") {
      renderPageAccessPanel();
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

    timeMachineVersionDetails.clear();
    await loadTimeMachineVersions(true);

    console.error("[wikilive][tm] restore:done", {
      pageId: restoredPage.pageId,
      versionId: version.versionId
    });
  } catch (error) {
    console.error("[wikilive][tm] restore:error", error);
    setTimeMachinePreviewState(
      "error",
      error && error.message ? error.message : "Не удалось восстановить версию."
    );
    renderTimeMachinePanel();
  } finally {
    if (timeMachineRestore) {
      timeMachineRestore.disabled = false;
    }
  }
}

function clearTimeMachinePreviewSelection() {
  timeMachineSelectedVersionId = "";
  setTimeMachinePreviewState("idle");
  renderTimeMachinePanel();
}

function selectTimeMachineVersion(versionId) {
  if (!versionId || timeMachineSelectedVersionId === versionId) return;
  timeMachineSelectedVersionId = versionId;
  renderTimeMachinePanel();
  loadTimeMachinePreview(versionId, false).catch((error) => {
    console.error("Failed to select time machine version", error);
  });
}

function handleTimeMachineFilterClick(filterKey) {
  const nextFilter = filterKey || "all";
  if (timeMachineFilter === nextFilter) return;
  timeMachineFilter = nextFilter;
  syncTimeMachineSelection();
  renderTimeMachinePanel();
  if (timeMachineSelectedVersionId) {
    loadTimeMachinePreview(timeMachineSelectedVersionId, false, { silent: true }).catch((error) => {
      console.error("Failed to refresh filtered preview", error);
    });
  }
}

function openTimeMachinePanel() {
  if (!timeMachinePanel) return;
  timeMachinePanel.classList.add("is-open");
  if (timeMachineTrigger) {
    timeMachineTrigger.classList.add("is-active");
  }
  renderTimeMachinePanel();
  loadTimeMachineVersions(true).catch((error) => {
    console.error("Failed to open time machine panel", error);
  });
}

function closeTimeMachinePanel() {
  if (!timeMachinePanel) return;
  timeMachinePanel.classList.remove("is-open");
  if (timeMachineTrigger) {
    timeMachineTrigger.classList.remove("is-active");
  }
  renderTimeMachinePanel();
}

function toggleTimeMachinePanel() {
  if (!timeMachinePanel) return;
  if (timeMachinePanel.classList.contains("is-open")) {
    closeTimeMachinePanel();
  } else {
    openTimeMachinePanel();
  }
}

if (timeMachineTrigger) {
  timeMachineTrigger.addEventListener("click", () => {
    toggleTimeMachinePanel();
  });
}

if (timeMachineClose) {
  timeMachineClose.addEventListener("click", () => {
    closeTimeMachinePanel();
  });
}

if (timeMachineRetry) {
  timeMachineRetry.addEventListener("click", () => {
    loadTimeMachineVersions(true).catch((error) => {
      console.error("Retry loadTimeMachineVersions failed", error);
    });
  });
}

if (timeMachineRestore) {
  timeMachineRestore.addEventListener("click", () => {
    restoreTimeMachineVersion();
  });
}

if (timeMachineClear) {
  timeMachineClear.addEventListener("click", () => {
    clearTimeMachinePreviewSelection();
  });
}

if (timeMachineFilters) {
  timeMachineFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-time-machine-filter]");
    if (!button) return;
    handleTimeMachineFilterClick(button.dataset.timeMachineFilter || "all");
  });
}

if (timeMachineList) {
  timeMachineList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-time-machine-version]");
    if (!button) return;
    selectTimeMachineVersion(button.dataset.timeMachineVersion || "");
  });
}

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && timeMachinePanel && timeMachinePanel.classList.contains("is-open")) {
    closeTimeMachinePanel();
  }
});

window.wikiliveRefreshTimeMachine = function wikiliveRefreshTimeMachine(options = {}) {
  const force = Boolean(options.force);
  return loadTimeMachineVersions(force, { silent: !force });
};
