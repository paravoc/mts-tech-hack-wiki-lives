const commentAnchorLayer = document.getElementById("commentAnchorLayer");
const commentsPanel = document.getElementById("commentsPanel");
const commentsPanelContext = document.getElementById("commentsPanelContext");
const commentsPanelStatus = document.getElementById("commentsPanelStatus");
const commentsPanelList = document.getElementById("commentsPanelList");
const commentsPanelScroll = document.getElementById("commentsPanelScroll");
const commentsPanelPlaceholder = document.getElementById("commentsPanelPlaceholder");
const commentsPanelLoading = document.getElementById("commentsPanelLoading");
const commentsPanelError = document.getElementById("commentsPanelError");
const commentsRetryButton = document.getElementById("commentsRetryButton");
const commentsCloseButton = document.getElementById("commentsCloseButton");
const commentsResolveButton = document.getElementById("commentsResolveButton");
const commentsComposerInput = document.getElementById("commentsComposerInput");
const commentsComposerSend = document.getElementById("commentsComposerSend");
const commentsActorSelect = document.getElementById("commentsActorSelect");
const commentsActorNote = document.getElementById("commentsActorNote");
const commentsGroupHints = document.getElementById("commentsGroupHints");
const commentsReplyPill = document.getElementById("commentsReplyPill");
const commentsReplyText = document.getElementById("commentsReplyText");
const commentsReplyCancel = document.getElementById("commentsReplyCancel");
const commentsMentionDropdown = document.getElementById("commentsMentionDropdown");
const commentsTopbar = document.getElementById("commentsTopbar");
const commentsTopTrigger = document.getElementById("commentsTopTrigger");
const commentsTopDropdown = document.getElementById("commentsTopDropdown");
const commentsHistoryButton = document.getElementById("commentsHistoryButton");
const commentsAccessButton = document.getElementById("commentsAccessButton");
const commentsAccessPopup = document.getElementById("commentsAccessPopup");
const commentsHistoryModal = document.getElementById("commentsHistoryModal");
const commentsHistoryBody = document.getElementById("commentsHistoryBody");
const commentsHistoryFooter = document.getElementById("commentsHistoryFooter");
const commentsHistoryClose = document.getElementById("commentsHistoryClose");

const commentUsers = [
  { id: "ivan", name: "Иван Иванов", handle: "ivan", short: "И", color: "#59c4ff", nick: "@ivan", role: "Редактор знаний", team: "Wiki editors" },
  { id: "sergei", name: "Сергей Иванов", handle: "sergei", short: "С", color: "#7b68ee", nick: "@sergei", role: "Backend", team: "Platform" },
  { id: "anna", name: "Анна Ивлева", handle: "anna", short: "А", color: "#4f83ff", nick: "@anna", role: "Дизайнер", team: "Design system" },
  { id: "anton", name: "Антон Серганов", handle: "anton", short: "А", color: "#ffc83d", nick: "@anton", role: "Релиз-менеджер", team: "Release" },
  { id: "maxim", name: "Максим Карпов", handle: "maxim", short: "М", color: "#5f79ff", nick: "@maxim", role: "Frontend", team: "Editor" },
  { id: "maria", name: "Мария Волкова", handle: "maria", short: "М", color: "#39c785", nick: "@maria", role: "Аналитик", team: "Data ops" }
];
const commentUserMap = new Map(commentUsers.map((user) => [user.id, user]));
const commentGroups = [
  { id: "group-release", name: "Команда релиза", handle: "release", short: "RL", color: "#8b7cff", meta: "Релиз, QA, владельцы запуска" },
  { id: "group-design", name: "Дизайн-ревью", handle: "design", short: "DS", color: "#ac8dff", meta: "UX, UI и контент" },
  { id: "group-backend", name: "Backend core", handle: "backend", short: "BE", color: "#6958f2", meta: "API, интеграции, storage" },
  { id: "group-wiki", name: "Wiki editors", handle: "wiki", short: "WK", color: "#9a7dff", meta: "Редакторы и knowledge owners" }
];
const commentGroupMap = new Map(commentGroups.map((group) => [group.id, group]));

const commentsDemoParagraphs = [
  "Порой кажется, что наша жизнь — это бесконечное плавание против течения, в мутной воде повседневных забот. Мы, как упрямые лососи, стремимся к своим целям, преодолевая пороги трудностей и обходя сети сомнений. И в этой вечной суете так легко забыть, что самое главное — не просто плыть по течению, а найти свою собственную, уникальную глубинную струю, которая выведет к чистой воде и простору настоящих достижений.",
  "Но стоит лишь на мгновение остановиться и прислушаться к тихому плеску мыслей, как становится ясно: каждый из нас — это целый океан возможностей. Наше сознание — не мелкий пруд, а бездонный морской шельф, где таятся неисследованные коралловые рифы идей и жемчужины озарений. Порой нужно просто дать себе свободу нырнуть в эту пучину, чтобы обнаружить сокровища, о которых мы и не подозревали, глядя лишь на рябь на поверхности.",
  "И потому, оказавшись в водовороте событий, не позволяй себе опускаться на дно. Расправь паруса своей мечты и лови попутный ветер перемен. Помни, что даже самая крупная рыба когда-то была мальком, а великие открытия часто рождаются не в штиль, а в самую бурю. Доверяй своему внутреннему компасу, и ты обязательно найдешь ту самую бухту, где море спокойно, а улов богат."
];

const historySeed = [
  {
    id: "hist-1",
    userId: "ivan",
    date: "27.10.25 в 18:03",
    statusText: "Удалена 29.10.25 в 13:32",
    preview: "Но стоит лишь на мгновение остановиться и прислушаться к тихому плеску мыслей, как ста...",
    text: "Думаю этот параграф стоит переписать, слишком сложно, тут же весь смысл в простоте донесения мысли. Читатель не поймет, если мы будет говорить как Достоевский, нужно как Фейс",
    toggleLabel: "Показать 20 комментариев ветки",
    thread: [
      { userId: "ivan", date: "27.10.25 в 18:03", text: "Этот текст тяжело воспринимать. Давайте сделаем его проще и понятнее для читателя." },
      { userId: "ivan", date: "27.10.25 в 18:03", text: "Слишком сложно написано. Нужно, чтобы читатель понимал все с первого раза, как будто с другом говоришь." }
    ]
  },
  {
    id: "hist-2",
    userId: "sergei",
    date: "27.10.25 в 18:03",
    statusText: "Решена 29.10.25 в 13:32",
    preview: "Порой кажется, что наша жизнь — это бесконечное плавание в мутной воде повседневных...",
    text: "Мое предложение вообще ничего не делать. Потому что лень.",
    toggleLabel: "Показать 2 комментария ветки",
    thread: [
      { userId: "ivan", date: "27.10.25 в 18:03", text: "Этот текст тяжело воспринимать. Давайте сделаем его проще и понятнее для читателя." },
      { userId: "ivan", date: "27.10.25 в 18:03", text: "Слишком сложно написано. Нужно, чтобы читатель понимал все с первого раза, как будто с другом говоришь." }
    ]
  },
  {
    id: "hist-3",
    userId: "ivan",
    date: "27.10.25 в 18:03",
    statusText: "Решена 29.10.25 в 13:32",
    preview: "",
    text: "@sergei заменить картинку",
    thumb: true,
    likes: 4,
    toggleLabel: "Показать 1 комментарий ветки",
    thread: [
      { userId: "sergei", date: "27.10.25 в 18:03", text: "Ок, заменю на более спокойный кадр." }
    ]
  }
];

let commentTargetCounter = 0;
let commentThreads = new Map();
let commentHistoryItems = [];
let commentHistoryExpanded = new Set();
let commentHistoryPage = 1;
let commentHistoryMode = "list";
let commentInitDone = false;
let commentOpenTargetId = null;
let commentPanelMode = "empty";
let commentReplyTo = null;
let commentEditingId = null;
let commentMenuOpenId = null;
let commentMentionCandidates = [];
let commentMentionIndex = 0;
let commentLoadToken = 0;
let commentObserver = null;
let commentFrame = null;
const commentApiBase = "http://127.0.0.1:3000";
const commentPageStorageKey = "wikilive-comment-page-id";
let commentPageId = "";
let commentAccessMode = "all_users";
let commentBootstrapPromise = null;
let commentSaveTimer = null;
let commentSyncTimer = null;
let commentSocket = null;
let commentSocketPageId = "";
let commentSocketReconnectTimer = null;
const commentActorStorageKey = "wikilive-comment-actor-id";
let currentCommentActorId = window.localStorage.getItem(commentActorStorageKey) || "ivan";

function commentIconSvg() {
  return '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 3.5h11v7h-7l-2.8 2V10.5H2.5z"></path><path d="M5.2 6.2h5.6M5.2 8.2h3.4"></path></svg>';
}

function getCurrentCommentActor() {
  return getCommentUser(currentCommentActorId || "ivan");
}

function getMentionEntity(entityId) {
  if (commentUserMap.has(entityId)) {
    return { ...commentUserMap.get(entityId), type: "user" };
  }
  if (commentGroupMap.has(entityId)) {
    return { ...commentGroupMap.get(entityId), type: "group" };
  }

  const normalized = String(entityId || "").trim().toLowerCase();
  const foundUser = commentUsers.find((user) => user.handle.toLowerCase() === normalized || user.id === normalized);
  if (foundUser) {
    return { ...foundUser, type: "user" };
  }
  const foundGroup = commentGroups.find((group) => group.handle.toLowerCase() === normalized || group.id === normalized);
  if (foundGroup) {
    return { ...foundGroup, type: "group" };
  }
  return null;
}

function renderActorPicker() {
  if (!commentsActorSelect) {
    return;
  }

  commentsActorSelect.innerHTML = commentUsers.map((user) => {
    const selected = user.id === currentCommentActorId ? " selected" : "";
    return `<option value="${user.id}"${selected}>${escapeHtml(user.name)} · ${escapeHtml(user.role)}</option>`;
  }).join("");

  const actor = getCurrentCommentActor();
  if (commentsActorNote) {
    commentsActorNote.textContent = `${actor.team} · ${actor.nick}`;
  }
  if (commentsGroupHints) {
    commentsGroupHints.innerHTML = commentGroups.slice(0, 3).map((group) => `<span class="comments-panel__group-hint">@${escapeHtml(group.handle)}</span>`).join("");
  }
}

function thumbsUpSvg() {
  return '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6.4 7V4.7c0-1.4.8-2.6 2.1-3.2l.2-.1v4h4c.7 0 1.2.6 1.1 1.3l-.6 4.8c-.1.6-.6 1.1-1.2 1.1H6.4M4.2 7h2.2v5.9H4.2z"></path></svg>';
}

function replySvg() {
  return '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6.2 4.1 3 7.4l3.2 3.2"></path><path d="M3.5 7.4H9c2.1 0 3.5 1 4 3"></path></svg>';
}

function menuSvg() {
  return '<svg viewBox="0 0 16 16" fill="currentColor"><circle cx="3.2" cy="8" r="1.2"></circle><circle cx="8" cy="8" r="1.2"></circle><circle cx="12.8" cy="8" r="1.2"></circle></svg>';
}

function escapeHtml(value) {
  return String(value || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\\"/g, "&quot;").replace(/'/g, "&#39;");
}

function formatCommentText(text) {
  const safe = escapeHtml(text).replace(/\\n/g, "<br>");
  return safe.replace(/(^|\\s)(@[a-zA-Zа-яА-Я0-9._-]+)/g, (match, prefix, mention) => prefix + '<span class="comment-mention">' + mention + "</span>");
}

function getCommentUser(userId) {
  if (commentUserMap.has(userId)) {
    return commentUserMap.get(userId);
  }
  const normalized = String(userId || "").trim().toLowerCase();
  const byHandle = commentUsers.find((user) => user.handle.toLowerCase() === normalized || user.name.toLowerCase() === normalized);
  if (byHandle) {
    return byHandle;
  }
  const label = String(userId || "Пользователь").trim() || "Пользователь";
  return {
    id: normalized || "viewer",
    name: label,
    handle: normalized || "viewer",
    short: label.charAt(0).toUpperCase(),
    color: "#59c4ff",
    nick: "@viewer",
    role: "Участник",
    team: "WikiLive"
  };
}

function createComment(id, userId, date, text, extra = {}) {
  return {
    id,
    userId,
    date,
    text,
    likes: extra.likes || 0,
    replyTo: extra.replyTo || null,
    editable: extra.editable !== false,
    attachmentType: extra.attachmentType || "",
    attachmentLabel: extra.attachmentLabel || "",
    targetPreview: extra.targetPreview || "",
    targetType: extra.targetType || ""
  };
}

function createThread(id, targetId, options = {}) {
  return {
    id,
    targetId,
    badgeCount: options.badgeCount || 0,
    status: options.status || "open",
    demoState: options.demoState || "ready",
    preview: options.preview || "",
    comments: options.comments || [],
    iconOnly: Boolean(options.iconOnly),
    targetType: options.targetType || "",
    targetLabel: options.targetLabel || ""
  };
}

async function commentApiRequest(path, options = {}) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 4200);
  let response;
  try {
    response = await fetch(commentApiBase + path, {
      headers: {
        "Content-Type": "application/json"
      },
      ...options,
      signal: controller.signal
    });
  } catch (error) {
    clearTimeout(timeoutId);
    if (error && error.name === "AbortError") {
      throw new Error("Comment request timed out");
    }
    throw error;
  }
  clearTimeout(timeoutId);

  let payload = {};
  try {
    payload = await response.json();
  } catch (error) {
    payload = {};
  }

  if (!response.ok || payload.success === false) {
    const message = payload && payload.error && payload.error.message ? payload.error.message : `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return payload.data || {};
}

function getCommentSocketUrl() {
  if (commentApiBase.startsWith("https://")) {
    return commentApiBase.replace("https://", "wss://") + "/ws";
  }
  return commentApiBase.replace("http://", "ws://") + "/ws";
}

function getThreadTargetLabel(targetType) {
  switch (targetType) {
    case "image":
      return "Изображение";
    case "file":
      return "Файл";
    case "table":
      return "Таблица";
    case "data":
      return "Живые данные";
    case "paragraph":
    case "p":
      return "Абзац";
    default:
      return "Фрагмент";
  }
}

function inferAttachmentForThread(targetType, preview) {
  if (targetType === "image") {
    return { attachmentType: "image", attachmentLabel: preview || "Изображение" };
  }
  if (targetType === "file") {
    return { attachmentType: "file", attachmentLabel: preview || "Файл" };
  }
  if (targetType === "table" || targetType === "data") {
    return { attachmentType: "data", attachmentLabel: preview || "Живые данные" };
  }
  return { attachmentType: "", attachmentLabel: "" };
}

function renderAttachmentPreview(type, label) {
  if (!type) {
    return "";
  }
  if (type === "image") {
    return `<div class="comment-card__attachment comment-card__attachment--image"><div class="comment-card__attachment-thumb"></div><span>${escapeHtml(label)}</span></div>`;
  }
  if (type === "file") {
    return `<div class="comment-card__attachment comment-card__attachment--file"><span class="comment-card__attachment-icon">↗</span><span>${escapeHtml(label)}</span></div>`;
  }
  return `<div class="comment-card__attachment comment-card__attachment--data"><span class="comment-card__attachment-icon">#</span><span>${escapeHtml(label)}</span></div>`;
}

function getReplyPreview(thread, comment) {
  if (!comment.replyTo) {
    return "";
  }
  const replied = getComment(thread, comment.replyTo);
  if (!replied) {
    return "";
  }
  const repliedUser = getCommentUser(replied.userId);
  return `<div class="comment-card__quote"><div class="comment-card__quote-label">Ответ @${escapeHtml(repliedUser.handle)}</div><div class="comment-card__quote-text">${escapeHtml(replied.text).slice(0, 88)}${replied.text.length > 88 ? "…" : ""}</div></div>`;
}

function renderTargetChip(thread, comment) {
  if (thread.comments[0] && thread.comments[0].id !== comment.id) {
    return "";
  }
  const label = thread.targetLabel || getThreadTargetLabel(thread.targetType);
  const preview = comment.targetPreview || thread.preview || "";
  return `<div class="comment-card__target"><span class="comment-card__target-type">${escapeHtml(label)}</span><span class="comment-card__target-preview">${escapeHtml(preview)}</span></div>`;
}

async function refreshCommentsFromServer() {
  if (!commentPageId) {
    return;
  }
  await syncThreadsFromServer();
  if (commentOpenTargetId) {
    const activeThread = getThread(commentOpenTargetId);
    commentPanelMode = activeThread && activeThread.comments.length ? "list" : "empty";
    renderCommentsPanel();
  }
  if (commentsHistoryModal && commentsHistoryModal.classList.contains("is-open") && commentHistoryMode !== "error") {
    renderHistoryModal();
  }
  scheduleCommentAnchors();
}

function subscribeCommentSocketToPage() {
  if (!commentSocket || commentSocket.readyState !== WebSocket.OPEN || !commentPageId || commentSocketPageId === commentPageId) {
    return;
  }
  commentSocket.send(JSON.stringify({ action: "subscribe", pageId: commentPageId }));
  commentSocketPageId = commentPageId;
}

function ensureCommentSocket() {
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
  commentSocket.addEventListener("open", () => {
    subscribeCommentSocketToPage();
  });
  commentSocket.addEventListener("message", (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (!payload || payload.pageId !== commentPageId) {
        return;
      }
      if (payload.event === "comments.changed" || payload.event === "comments.access.changed" || payload.event === "page.updated") {
        refreshCommentsFromServer().catch((error) => console.warn("Failed to refresh comments from socket", error));
      }
    } catch (error) {
      console.warn("Failed to parse comment socket payload", error);
    }
  });
  commentSocket.addEventListener("close", () => {
    commentSocket = null;
    commentSocketPageId = "";
    if (commentSocketReconnectTimer) {
      clearTimeout(commentSocketReconnectTimer);
    }
    commentSocketReconnectTimer = window.setTimeout(() => {
      ensureCommentSocket();
    }, 1800);
  });
  commentSocket.addEventListener("error", () => {
    if (commentSocket) {
      commentSocket.close();
    }
  });
}

function inferTargetType(target) {
  if (!target) {
    return "paragraph";
  }
  if (target.classList.contains("embedded-image-block")) {
    return "image";
  }
  if (target.classList.contains("embedded-file-chip")) {
    return "file";
  }
  if (target.tagName === "TABLE") {
    return "table";
  }
  if (target.dataset.liveToken || target.dataset.liveValue || target.classList.contains("formula-chip")) {
    return "data";
  }
  return target.tagName.toLowerCase();
}

function formatThreadDate(isoValue) {
  if (!isoValue) {
    return "";
  }
  const parsed = new Date(isoValue);
  if (Number.isNaN(parsed.getTime())) {
    return isoValue;
  }
  return parsed.toLocaleDateString("ru-RU") + " в " + parsed.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
}

function serializeEditorDocument() {
  return {
    title: titleEditor.textContent.replace(/\u200B/g, "").trim() || "Страница для комментирования",
    content: bodyEditor.innerHTML
  };
}

async function seedServerDemoThreadsIfNeeded(pageId) {
  const targets = getCommentableTargets();
  targets.forEach((target) => ensureTargetId(target));
  if (!targets.length) {
    return;
  }

  const firstTarget = targets[0];
  await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments`, {
    method: "POST",
    body: JSON.stringify({
      author: "ivan",
      body: "Думаю этот абзац стоит переписать: сейчас мысль правильная, но для onboarding-текста она слишком плотная.",
      selectionLabel: getTargetPreview(firstTarget),
      targetId: ensureTargetId(firstTarget),
      targetType: inferTargetType(firstTarget),
      targetPreview: getTargetPreview(firstTarget)
    })
  });

  const mainThreads = await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments`);
  const mainThread = (mainThreads.items || []).find((item) => item.targetId === ensureTargetId(firstTarget));
  if (mainThread) {
    await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments/${encodeURIComponent(mainThread.threadId)}/replies`, {
      method: "POST",
      body: JSON.stringify({ author: "sergei", body: "Согласен. Я бы упростил формулировки и оставил один главный тезис." })
    });
    await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments/${encodeURIComponent(mainThread.threadId)}/replies`, {
      method: "POST",
      body: JSON.stringify({ author: "anna", body: "@design давайте потом еще проверим визуальный ритм этого блока." })
    });
  }

  if (targets[2]) {
    const thirdTarget = targets[2];
    await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments`, {
      method: "POST",
      body: JSON.stringify({
        author: "maxim",
        body: "Этот блок уже согласовали. Оставляем как есть и закрываем ветку.",
        selectionLabel: getTargetPreview(thirdTarget),
        targetId: ensureTargetId(thirdTarget),
        targetType: inferTargetType(thirdTarget),
        targetPreview: getTargetPreview(thirdTarget)
      })
    });
    const resolvedThreads = await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments`);
    const resolvedThread = (resolvedThreads.items || []).find((item) => item.targetId === ensureTargetId(thirdTarget));
    if (resolvedThread) {
      await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments/${encodeURIComponent(resolvedThread.threadId)}/resolve`, {
        method: "POST",
        body: JSON.stringify({ resolved: true })
      });
    }
  }
}

function applyEditorDocument(page) {
  if (!page) {
    return;
  }
  titleEditor.textContent = page.title || "Страница для комментирования";
  bodyEditor.innerHTML = page.content && page.content.trim() ? page.content : commentsDemoParagraphs.map((paragraph) => `<p>${paragraph}</p>`).join("");
  renderOutline();
}

function scheduleCommentDocumentSave() {
  if (!commentPageId) {
    return;
  }
  if (commentSaveTimer) {
    clearTimeout(commentSaveTimer);
  }
  commentSaveTimer = window.setTimeout(async () => {
    try {
      const documentPayload = serializeEditorDocument();
      await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}`, {
        method: "PUT",
        body: JSON.stringify(documentPayload)
      });
    } catch (error) {
      console.warn("Failed to save comment page", error);
    }
  }, 650);
}

function mapThreadFromApi(item) {
  const resolvedTargetId = findResolvedTargetId(item);
  const threadAttachment = inferAttachmentForThread(item.targetType || "", item.targetPreview || item.selectionLabel || "");
  const comments = (item.messages || []).map((message, index) => createComment(
    message.messageId,
    message.author || "viewer",
    formatThreadDate(message.updatedAt || message.createdAt),
    message.body || "",
    {
      likes: 0,
      replyTo: message.replyToMessageId || null,
      attachmentType: index === 0 ? threadAttachment.attachmentType : "",
      attachmentLabel: index === 0 ? threadAttachment.attachmentLabel : "",
      targetPreview: item.targetPreview || item.selectionLabel || "",
      targetType: item.targetType || ""
    }
  ));
  if (comments.length) {
    comments[comments.length - 1].likes = item.likeCount || 0;
  }
  return createThread(item.threadId, resolvedTargetId, {
    badgeCount: item.messages ? item.messages.length : 0,
    status: item.resolved ? "resolved" : "open",
    preview: item.targetPreview || item.selectionLabel || "",
    comments,
    iconOnly: !(item.messages || []).length,
    targetType: item.targetType || "",
    targetLabel: getThreadTargetLabel(item.targetType || "")
  });
}

async function syncThreadsFromServer() {
  if (!commentPageId) {
    return;
  }

  const [threadsData, historyData, accessData] = await Promise.all([
    commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments`),
    commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/history`),
    commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comment-access`)
  ]);

  const nextThreads = new Map();
  (threadsData.items || []).forEach((item) => {
    const mappedThread = mapThreadFromApi(item);
    const existingThread = nextThreads.get(mappedThread.targetId);
    if (!existingThread) {
      nextThreads.set(mappedThread.targetId, mappedThread);
      return;
    }

    const existingScore =
      (existingThread.status === "resolved" ? 0 : 1000) +
      ((existingThread.comments || []).length * 100) +
      normalizePreviewText(existingThread.preview || "").length;
    const incomingScore =
      (mappedThread.status === "resolved" ? 0 : 1000) +
      ((mappedThread.comments || []).length * 100) +
      normalizePreviewText(mappedThread.preview || "").length;

    nextThreads.set(
      mappedThread.targetId,
      incomingScore >= existingScore ? mappedThread : existingThread
    );
  });
  commentThreads = nextThreads;

  commentHistoryItems = (historyData.items || []).map((item) => ({
    id: item.threadId,
    userId: item.messages && item.messages[0] ? item.messages[0].author : "ivan",
    date: formatThreadDate(item.createdAt),
    statusText: item.deleted
      ? `Удалена ${formatThreadDate(item.deletedAt)}`
      : `Решена ${formatThreadDate(item.resolvedAt)}`,
    preview: item.targetPreview || item.selectionLabel || "",
    text: item.messages && item.messages[0] ? item.messages[0].body : "",
    likes: item.likeCount || 0,
    thumb: item.targetType === "image",
    targetType: item.targetType || "",
    thread: (item.messages || []).slice(1).map((message) => ({
      userId: message.author,
      date: formatThreadDate(message.updatedAt || message.createdAt),
      text: message.body
    })),
    toggleLabel: `Показать ${Math.max((item.messages || []).length - 1, 1)} комментария ветки`
  }));

  commentAccessMode = accessData.mode || "all_users";
  commentInitDone = true;
  document.querySelectorAll('input[name="commentAccess"]').forEach((input) => {
    input.checked = input.value === (commentAccessMode === "owner_only" ? "author" : "all");
  });
}

async function ensureCommentPage() {
  if (commentBootstrapPromise) {
    return commentBootstrapPromise;
  }

  commentBootstrapPromise = (async () => {
    seedCommentsDemoDocumentIfNeeded();
    const savedPageId = window.localStorage.getItem(commentPageStorageKey) || "";
    const pagesData = await commentApiRequest("/api/pages");
    const items = pagesData.items || [];
    let page = null;

    if (savedPageId) {
      page = items.find((item) => item.pageId === savedPageId) || null;
    }

    if (!page) {
      page = items.find((item) => item.title === "Страница для комментирования") || null;
    }

    if (!page) {
      getCommentableTargets().forEach((target) => ensureTargetId(target));
      const created = await commentApiRequest("/api/pages", {
        method: "POST",
        body: JSON.stringify(serializeEditorDocument())
      });
      page = created.item;
      await seedServerDemoThreadsIfNeeded(page.pageId);
    } else {
      const loaded = await commentApiRequest(`/api/pages/${encodeURIComponent(page.pageId)}`);
      page = loaded.item;
      applyEditorDocument(page);
    }

    commentPageId = page.pageId;
    window.localStorage.setItem(commentPageStorageKey, commentPageId);
    await ensurePersistedCommentTargets();
    await syncThreadsFromServer();
    if (!commentThreads.size && !commentHistoryItems.length) {
      await seedServerDemoThreadsIfNeeded(commentPageId);
      await syncThreadsFromServer();
    }
    ensureCommentSocket();
    subscribeCommentSocketToPage();
    scheduleCommentAnchors();
    renderCommentsPanel();
    return page;
  })().catch((error) => {
    console.warn("Failed to bootstrap comment page", error);
    commentBootstrapPromise = null;
    return null;
  });

  return commentBootstrapPromise;
}

function seedCommentsDemoDocumentIfNeeded() {
  if (!hasPlaceholder()) {
    return;
  }
  titleEditor.textContent = "Страница для комментирования";
  bodyEditor.innerHTML = commentsDemoParagraphs.map((paragraph) => `<p>${paragraph}</p>`).join("");
  renderOutline();
}

function getCommentableTargets() {
  const directBlocks = Array.from(bodyEditor.children).filter((node) => {
    return node instanceof HTMLElement && !node.classList.contains("body-placeholder") && ["P", "H1", "H2", "H3", "UL", "OL", "BLOCKQUOTE", "PRE"].includes(node.tagName);
  });
  const objectBlocks = Array.from(bodyEditor.querySelectorAll(
    ".embedded-image-block, .embedded-file-chip, table, [data-comment-object='1'], [data-live-token], [data-live-value], .live-data-chip, .formula-chip, .table-value-chip"
  ));
  const result = [];
  const seen = new Set();
  [...directBlocks, ...objectBlocks].forEach((node) => {
    if (!seen.has(node)) {
      seen.add(node);
      result.push(node);
    }
  });
  return result;
}

function ensureTargetId(target) {
  if (target.dataset.blockId) {
    target.dataset.commentTargetId = target.dataset.blockId;
    return target.dataset.commentTargetId;
  }
  if (!target.dataset.commentTargetId) {
    commentTargetCounter += 1;
    target.dataset.commentTargetId = "block-" + commentTargetCounter;
    target.dataset.blockId = target.dataset.commentTargetId;
  }
  return target.dataset.commentTargetId;
}

function getTargetPreview(target) {
  if (!target) {
    return "Нет выбранного блока";
  }
  if (target.classList.contains("embedded-image-block")) {
    const img = target.querySelector("img");
    return img && img.getAttribute("alt") ? "Изображение • " + img.getAttribute("alt") : "Изображение";
  }
  if (target.classList.contains("embedded-file-chip")) {
    return "Файл • " + target.textContent.replace(/\s+/g, " ").trim();
  }
  return target.textContent.replace(/\s+/g, " ").trim() || "Пустой блок";
}

function normalizePreviewText(value) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function findResolvedTargetId(item) {
  const directTarget = document.querySelector(`[data-comment-target-id="${item.targetId}"]`);
  if (directTarget) {
    return item.targetId;
  }

  const expectedPreview = normalizePreviewText(item.targetPreview || item.selectionLabel || "");
  const expectedType = item.targetType || "";
  const targets = getCommentableTargets();
  let bestMatch = null;

  targets.forEach((target) => {
    const targetId = ensureTargetId(target);
    const targetPreview = normalizePreviewText(getTargetPreview(target));
    const targetType = inferTargetType(target);
    if (expectedPreview && targetPreview === expectedPreview && (!expectedType || targetType === expectedType)) {
      bestMatch = targetId;
    }
  });

  return bestMatch || item.targetId;
}

async function ensurePersistedCommentTargets() {
  const targets = getCommentableTargets();
  let changed = false;
  targets.forEach((target) => {
    if (!target.dataset.blockId) {
      changed = true;
    }
    ensureTargetId(target);
  });

  if (changed && commentPageId) {
    try {
      await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}`, {
        method: "PUT",
        body: JSON.stringify(serializeEditorDocument())
      });
    } catch (error) {
      console.warn("Failed to persist comment target ids", error);
    }
  }
}

function collectHistoryItems(pageItems, page, totalPages) {
  const footer = [];
  if (totalPages <= 1) {
    return "";
  }
  const visiblePages = [];
  const headPages = Math.min(3, totalPages);
  for (let pageNumber = 1; pageNumber <= headPages; pageNumber += 1) {
    visiblePages.push(pageNumber);
  }
  if (!visiblePages.includes(totalPages)) {
    visiblePages.push("ellipsis");
    visiblePages.push(totalPages);
  }
  visiblePages.forEach((entry) => {
    if (entry === "ellipsis") {
      footer.push('<span class="comments-history-modal__ellipsis">…</span>');
      return;
    }
    footer.push(`<button class="comments-history-modal__page${entry === page ? " is-active" : ""}" data-history-action="page" data-history-page="${entry}" type="button">${entry}</button>`);
  });
  if (page < totalPages) {
    footer.push('<button class="comments-history-modal__next" data-history-action="next" type="button" aria-label="Следующая страница">›</button>');
  }
  return footer.join("");
}

function seedThreads(targets) {
  if (commentInitDone || !targets.length) {
    return;
  }
  if (targets[0]) {
    const id = ensureTargetId(targets[0]);
    const targetType = inferTargetType(targets[0]);
    commentThreads.set(id, createThread("thread-main", id, {
      badgeCount: 4,
      preview: getTargetPreview(targets[0]),
      targetType,
      targetLabel: getThreadTargetLabel(targetType),
      comments: [
        createComment("comment-1", "ivan", "27.10.25 в 18:03", "Думаю этот параграф стоит переписать: читатель спотыкается уже в первой строке.", { targetPreview: getTargetPreview(targets[0]), targetType }),
        createComment("comment-2", "sergei", "27.10.25 в 18:03", "Я бы сократил его почти вдвое и вынес детали ниже отдельным блоком."),
        createComment("comment-3", "anna", "27.10.25 в 18:03", "@design можно еще проверить визуальный акцент на первом предложении.", { likes: 2 }),
        createComment("comment-4", "maria", "27.10.25 в 18:03", "@release если этот текст пойдет в демо, лучше сделать его проще для первого показа.", { likes: 4 })
      ]
    }));
  }
  if (targets[1]) {
    const id = ensureTargetId(targets[1]);
    const targetType = inferTargetType(targets[1]);
    commentThreads.set(id, createThread("thread-empty", id, {
      preview: getTargetPreview(targets[1]),
      targetType,
      targetLabel: getThreadTargetLabel(targetType),
      comments: [],
      iconOnly: true,
      demoState: "error"
    }));
  }
  if (targets[2]) {
    const id = ensureTargetId(targets[2]);
    const targetType = inferTargetType(targets[2]);
    commentThreads.set(id, createThread("thread-resolved", id, {
      badgeCount: 1,
      preview: getTargetPreview(targets[2]),
      status: "resolved",
      targetType,
      targetLabel: getThreadTargetLabel(targetType),
      comments: [
        createComment("comment-5", "maxim", "27.10.25 в 18:03", "Этот блок уже согласован. Оставляем формулировку и помечаем ветку как решенную.", { likes: 3, targetPreview: getTargetPreview(targets[2]), targetType })
      ]
    }));
  }
  commentInitDone = true;
}

function ensureHistorySeed() {
  if (commentHistoryItems.length) {
    return;
  }
  const items = [];
  for (let page = 0; page < 10; page += 1) {
    historySeed.forEach((item, index) => items.push({ ...item, id: item.id + "-" + page + "-" + index }));
  }
  commentHistoryItems = items;
}

function getThread(targetId) {
  return commentThreads.get(targetId) || null;
}

function getOrCreateThread(targetId) {
  let thread = getThread(targetId);
  if (!thread) {
    thread = createThread("thread-" + targetId, targetId, {
      preview: getTargetPreview(document.querySelector(`[data-comment-target-id="${targetId}"]`)),
      targetType: inferTargetType(document.querySelector(`[data-comment-target-id="${targetId}"]`)),
      targetLabel: getThreadTargetLabel(inferTargetType(document.querySelector(`[data-comment-target-id="${targetId}"]`)))
    });
    commentThreads.set(targetId, thread);
  }
  return thread;
}

function getComment(thread, commentId) {
  return (thread.comments || []).find((item) => item.id === commentId) || null;
}

function highlightActiveTarget() {
  document.querySelectorAll(".comment-target--active").forEach((node) => node.classList.remove("comment-target--active"));
  if (!commentOpenTargetId) {
    return;
  }
  const target = document.querySelector(`[data-comment-target-id="${commentOpenTargetId}"]`);
  if (target) {
    target.classList.add("comment-target--active");
  }
}

function scheduleCommentAnchors() {
  if (commentFrame) {
    cancelAnimationFrame(commentFrame);
  }
  commentFrame = requestAnimationFrame(renderCommentAnchors);
}

function renderCommentAnchors() {
  commentFrame = null;
  if (!commentAnchorLayer) {
    return;
  }
  const targets = getCommentableTargets();
  targets.forEach((target) => ensureTargetId(target));
  seedThreads(targets);
  highlightActiveTarget();
  const canvasRect = editorCanvas.getBoundingClientRect();
  const panelVisible = commentsPanel.classList.contains("is-open");
  const reserve = panelVisible ? 392 : 84;
  const html = [];

  targets.forEach((target) => {
    const targetId = target.dataset.commentTargetId;
    const rect = target.getBoundingClientRect();
    if (!rect.width || !rect.height) {
      return;
    }
    const thread = getThread(targetId);
    const count = thread ? (thread.badgeCount || thread.comments.length || 0) : 0;
    const tooltip = count > 0 ? `Показать ${count} комментария` : "Начать обсуждение";
    const top = rect.top - canvasRect.top + editorCanvas.scrollTop;
    const left = Math.max(18, Math.min(rect.right - canvasRect.left + 12, editorCanvas.clientWidth - reserve));
    const isActive = commentOpenTargetId === targetId;
    html.push(
      `<div class="comment-anchor" style="top:${top}px;left:${left}px;">` +
        `${isActive ? `<span class="comment-anchor__line" style="height:${Math.max(rect.height, 52)}px"></span>` : ""}` +
        `<button class="comment-anchor__button${count ? "" : " is-empty"}${isActive ? " is-active" : ""}" data-comment-target="${targetId}" data-comment-tooltip="${escapeHtml(tooltip)}" type="button">` +
          `<span class="comment-anchor__icon">${commentIconSvg()}</span>` +
          `${count ? `<span class="comment-anchor__badge">${count}</span>` : ""}` +
        `</button>` +
      `</div>`
    );
  });

  commentAnchorLayer.innerHTML = html.join("");
}

function renderReplyPill(thread) {
  if (!thread || !commentReplyTo) {
    commentsReplyPill.classList.remove("is-visible");
    commentsReplyText.textContent = "";
    return;
  }
  const comment = getComment(thread, commentReplyTo);
  if (!comment) {
    commentsReplyPill.classList.remove("is-visible");
    return;
  }
  const user = getCommentUser(comment.userId);
  commentsReplyText.innerHTML = `Ответ <span class="comment-mention">@${escapeHtml(user.handle)}</span>: ${escapeHtml(comment.text).slice(0, 52)}${comment.text.length > 52 ? "…" : ""}`;
  commentsReplyPill.classList.add("is-visible");
}

function updateComposerState() {
  commentsComposerSend.disabled = !commentOpenTargetId || !commentsComposerInput.value.trim();
}

function renderMentionDropdown() {
  const value = commentsComposerInput.value;
  const match = value.match(/@([a-zA-Zа-яА-Я0-9._-]*)$/);
  if (!match) {
    commentMentionCandidates = [];
    commentsMentionDropdown.classList.remove("is-open");
    commentsMentionDropdown.innerHTML = "";
    return;
  }
  const query = (match[1] || "").toLowerCase();
  const userMatches = commentUsers
    .filter((user) => !query || `${user.name} ${user.handle} ${user.team} ${user.role}`.toLowerCase().includes(query))
    .slice(0, 4)
    .map((user) => ({ ...user, type: "user" }));
  const groupMatches = commentGroups
    .filter((group) => !query || `${group.name} ${group.handle} ${group.meta}`.toLowerCase().includes(query))
    .slice(0, 3)
    .map((group) => ({ ...group, type: "group" }));
  commentMentionCandidates = [...userMatches, ...groupMatches];
  if (!commentMentionCandidates.length) {
    commentsMentionDropdown.classList.remove("is-open");
    commentsMentionDropdown.innerHTML = "";
    return;
  }
  commentMentionIndex = Math.min(commentMentionIndex, Math.max(commentMentionCandidates.length - 1, 0));
  const renderEntity = (entity, index) => {
    const avatar = entity.type === "group"
      ? `<span class="comments-mentions__group-badge">${escapeHtml(entity.short)}</span>`
      : `<span class="comment-card__avatar" style="background:${entity.color};width:30px;height:30px;font-size:16px;">${entity.short}</span>`;
    const meta = entity.type === "group" ? entity.meta : `${entity.role} · ${entity.team}`;
    return `<button class="comments-mentions__item${index === commentMentionIndex ? " is-active" : ""}" data-mention-user="${entity.id}" type="button">${avatar}<span><span class="comments-mentions__name">${escapeHtml(entity.name)}</span><span class="comments-mentions__nick">@${escapeHtml(entity.handle)}</span><span class="comments-mentions__meta">${escapeHtml(meta)}</span></span></button>`;
  };

  const sections = [];
  if (userMatches.length) {
    sections.push('<div class="comments-mentions__section">Пользователи</div>');
    sections.push(userMatches.map((user, index) => renderEntity(user, index)).join(""));
  }
  if (groupMatches.length) {
    sections.push('<div class="comments-mentions__section">Группы</div>');
    sections.push(groupMatches.map((group, index) => renderEntity(group, userMatches.length + index)).join(""));
  }

  commentsMentionDropdown.innerHTML = sections.join("") + '<div class="comments-mentions__more">Можно упоминать людей и команды проекта</div>';
  commentsMentionDropdown.classList.add("is-open");
}

function applyMention(userId) {
  const entity = getMentionEntity(userId);
  if (!entity) {
    return;
  }
  commentsComposerInput.value = commentsComposerInput.value.replace(/@([a-zA-Zа-яА-Я0-9._-]*)$/, `@${entity.handle} `);
  commentsMentionDropdown.classList.remove("is-open");
  commentsMentionDropdown.innerHTML = "";
  commentsComposerInput.focus();
  updateComposerState();
}

function renderCommentCard(thread, comment) {
  const user = getCommentUser(comment.userId);
  const isEditing = commentEditingId === comment.id;
  const menuOpen = commentMenuOpenId === comment.id;
  const isReplyTarget = commentReplyTo === comment.id;
  const textValue = comment.text || "";
  const replyPreview = getReplyPreview(thread, comment);
  const targetChip = renderTargetChip(thread, comment);
  const attachmentPreview = renderAttachmentPreview(comment.attachmentType, comment.attachmentLabel);
  return `
    <article class="comment-card${isReplyTarget ? " is-focused" : ""}${menuOpen ? " is-menu-open" : ""}${isEditing ? " is-editing" : ""}" data-comment-id="${comment.id}">
      <span class="comment-card__avatar" style="background:${user.color}">${user.short}</span>
      <div class="comment-card__body">
        <div class="comment-card__top">
          <div>
            <div class="comment-card__name">${escapeHtml(user.name)}</div>
            <div class="comment-card__meta-line">
              <div class="comment-card__date">${escapeHtml(comment.date)}</div>
              <span class="comment-card__role">${escapeHtml(user.role || user.team || "Участник")}</span>
            </div>
          </div>
          <div class="comment-card__actions">
            <button class="comment-action" data-comment-action="like" data-comment-id="${comment.id}" type="button" aria-label="Лайк">
              ${thumbsUpSvg()}
              ${comment.likes ? `<span class="comment-action__count">${comment.likes}</span>` : ""}
            </button>
            <button class="comment-action" data-comment-action="reply" data-comment-id="${comment.id}" type="button" aria-label="Ответить" data-comment-tooltip="Ответить">
              ${replySvg()}
            </button>
            <div class="comment-card__menu-wrap">
              <button class="comment-action" data-comment-action="menu" data-comment-id="${comment.id}" type="button" aria-label="Меню">
                ${menuSvg()}
              </button>
              <div class="comment-card__menu${menuOpen ? " is-open" : ""}">
                <button class="comment-card__menu-item" data-comment-action="edit" data-comment-id="${comment.id}" type="button">Редактировать</button>
                <button class="comment-card__menu-item is-danger" data-comment-action="delete" data-comment-id="${comment.id}" type="button">Удалить</button>
              </div>
            </div>
          </div>
        </div>
        ${targetChip}
        ${replyPreview}
        ${attachmentPreview}
        ${isEditing ? `
          <div class="comment-card__editor">
            <textarea data-comment-edit-input="${comment.id}">${escapeHtml(textValue)}</textarea>
            <button class="comment-card__save" data-comment-action="save-edit" data-comment-id="${comment.id}" type="button">Сохранить</button>
          </div>
        ` : `<div class="comment-card__text">${formatCommentText(textValue)}</div>`}
      </div>
    </article>
  `;
}

function renderCommentsPanel() {
  const isOpen = Boolean(commentOpenTargetId);
  commentsPanel.classList.toggle("is-open", isOpen);
  commentsResolveButton.disabled = !isOpen;

  if (!isOpen) {
    commentsPanelStatus.hidden = true;
    commentsPanelList.innerHTML = "";
    commentsPanelPlaceholder.hidden = false;
    commentsPanelScroll.hidden = true;
    commentsPanelLoading.hidden = true;
    commentsPanelError.hidden = true;
    commentsPanelContext.textContent = "Нет выбранного блока";
    renderReplyPill(null);
    updateComposerState();
    return;
  }

  const thread = getOrCreateThread(commentOpenTargetId);
  const target = document.querySelector(`[data-comment-target-id="${commentOpenTargetId}"]`);
  thread.preview = getTargetPreview(target);
  commentsPanelContext.textContent = thread.preview;
  commentsPanelStatus.hidden = thread.status !== "resolved";
  commentsPanelStatus.textContent = thread.status === "resolved" ? "Решена" : "";

  commentsPanelLoading.hidden = commentPanelMode !== "loading";
  commentsPanelError.hidden = commentPanelMode !== "error";
  commentsPanelPlaceholder.hidden = commentPanelMode !== "empty";
  commentsPanelScroll.hidden = commentPanelMode !== "list";

  if (commentPanelMode === "list") {
    commentsPanelList.innerHTML = thread.comments.map((comment) => renderCommentCard(thread, comment)).join("");
  } else {
    commentsPanelList.innerHTML = "";
  }

  renderReplyPill(thread);
  renderMentionDropdown();
  updateComposerState();
}

async function openThreadForTarget(targetId, instant = false) {
  if (!targetId) {
    return;
  }
  commentOpenTargetId = targetId;
  commentReplyTo = null;
  commentEditingId = null;
  commentMenuOpenId = null;
  commentPanelMode = "loading";
  commentLoadToken += 1;
  renderCommentsPanel();
  scheduleCommentAnchors();

  const token = commentLoadToken;
  let syncFailed = false;
  if (commentPageId) {
    try {
      await syncThreadsFromServer();
    } catch (error) {
      syncFailed = true;
      console.warn("Failed to sync comment threads", error);
    }
  }
  const thread = getOrCreateThread(targetId);
  const applyMode = () => {
    if (token !== commentLoadToken) {
      return;
    }
    if (thread.demoState === "error") {
      commentPanelMode = "error";
    } else if (syncFailed && !thread.comments.length) {
      commentPanelMode = "error";
    } else if (!thread.comments.length) {
      commentPanelMode = "empty";
    } else {
      commentPanelMode = "list";
    }
    renderCommentsPanel();
    scheduleCommentAnchors();
    if (commentPanelMode === "list") {
      requestAnimationFrame(() => {
        commentsPanelScroll.scrollTop = commentsPanelScroll.scrollHeight;
      });
    }
  };

  if (instant) {
    applyMode();
  } else {
    window.setTimeout(applyMode, 260);
  }
}

function closeCommentsPanel() {
  commentOpenTargetId = null;
  commentReplyTo = null;
  commentEditingId = null;
  commentMenuOpenId = null;
  commentPanelMode = "empty";
  commentsComposerInput.value = "";
  commentsMentionDropdown.classList.remove("is-open");
  commentsMentionDropdown.innerHTML = "";
  renderCommentsPanel();
  scheduleCommentAnchors();
}

function addHistorySnapshot(thread, statusText, focusComment = null) {
  const baseComment = focusComment || thread.comments[thread.comments.length - 1];
  if (!baseComment) {
    return;
  }
  const target = document.querySelector(`[data-comment-target-id="${thread.targetId}"]`);
  commentHistoryItems.unshift({
    id: `hist-runtime-${Date.now()}-${Math.random().toString(16).slice(2, 6)}`,
    userId: baseComment.userId,
    date: baseComment.date,
    statusText,
    preview: getTargetPreview(target).slice(0, 120),
    text: baseComment.text,
    likes: baseComment.likes || 0,
    thread: thread.comments.map((item) => ({ userId: item.userId, date: item.date, text: item.text })),
    toggleLabel: `Показать ${Math.max(thread.comments.length - 1, 1)} комментария ветки`
  });
}

async function toggleResolvedThread() {
  if (!commentOpenTargetId) {
    return;
  }
  const thread = getOrCreateThread(commentOpenTargetId);
  const nextResolved = thread.status !== "resolved";
  if (commentPageId) {
    await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/resolve`, {
      method: "POST",
      body: JSON.stringify({ resolved: nextResolved })
    });
    await syncThreadsFromServer();
  } else {
    thread.status = nextResolved ? "resolved" : "open";
    if (thread.status === "resolved") {
      addHistorySnapshot(thread, "Решена " + new Date().toLocaleDateString("ru-RU") + " в " + new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }));
    }
  }
  renderCommentsPanel();
  scheduleCommentAnchors();
}

async function addCommentToThread() {
  if (!commentOpenTargetId) {
    return;
  }
  const raw = commentsComposerInput.value.trim();
  if (!raw) {
    updateComposerState();
    return;
  }
  const thread = getOrCreateThread(commentOpenTargetId);
  let text = raw;
  const targetElement = document.querySelector(`[data-comment-target-id="${commentOpenTargetId}"]`);
  if (commentReplyTo) {
    const targetComment = getComment(thread, commentReplyTo);
    if (targetComment) {
      const replyUser = getCommentUser(targetComment.userId);
      if (!text.includes("@" + replyUser.handle)) {
        text = "@" + replyUser.handle + " " + text;
      }
    }
  }

  if (commentPageId) {
    if (!thread.comments.length) {
      await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments`, {
        method: "POST",
        body: JSON.stringify({
          author: getCurrentCommentActor().id,
          body: text,
          selectionLabel: getTargetPreview(targetElement),
          targetId: commentOpenTargetId,
          targetType: inferTargetType(targetElement),
          targetPreview: getTargetPreview(targetElement)
        })
      });
    } else {
      await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/replies`, {
        method: "POST",
        body: JSON.stringify({
          author: getCurrentCommentActor().id,
          body: text,
          replyToMessageId: commentReplyTo || ""
        })
      });
    }
    await syncThreadsFromServer();
  } else {
    const now = new Date();
    const dateLabel = now.toLocaleDateString("ru-RU") + " в " + now.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
    thread.comments.push(createComment(`comment-${Date.now()}`, getCurrentCommentActor().id, dateLabel, text));
    thread.badgeCount = Math.max(thread.badgeCount + 1, thread.comments.length);
    thread.demoState = "ready";
    thread.status = "open";
  }

  commentReplyTo = null;
  commentEditingId = null;
  commentMenuOpenId = null;
  commentsComposerInput.value = "";
  commentPanelMode = getOrCreateThread(commentOpenTargetId).comments.length ? "list" : "empty";
  renderCommentsPanel();
  scheduleCommentAnchors();
  requestAnimationFrame(() => {
    commentsPanelScroll.scrollTop = commentsPanelScroll.scrollHeight;
    commentsComposerInput.focus();
  });
}

function renderHistoryModal() {
  if (!commentsHistoryModal.classList.contains("is-open")) {
    return;
  }
  if (commentHistoryMode === "error") {
    commentsHistoryBody.innerHTML = `
      <div class="comments-history-modal__error">
        <div class="comments-history-modal__error-inner">
          <div>Не удалось загрузить комментарии.<br>Попробуйте еще раз</div>
          <button class="comments-panel__retry" data-history-action="retry" type="button">Загрузить повторно</button>
        </div>
      </div>
    `;
    commentsHistoryFooter.innerHTML = "";
    return;
  }

  const itemsPerPage = 3;
  const totalPages = Math.max(1, Math.max(Math.ceil(commentHistoryItems.length / itemsPerPage), 10));
  const page = Math.min(Math.max(commentHistoryPage, 1), totalPages);
  const start = (page - 1) * itemsPerPage;
  const pageItems = commentHistoryItems.slice(start, start + itemsPerPage);

  commentsHistoryBody.innerHTML = pageItems.map((item) => {
    const user = getCommentUser(item.userId);
    const expanded = commentHistoryExpanded.has(item.id);
    const actions = item.likes ? `<div class="comments-history-item__actions"><span>${item.likes}</span><span>${thumbsUpSvg()}</span></div>` : "";
    const nested = expanded
      ? `<div class="comments-history-item__thread">${(item.thread || []).map((entry) => {
          const nestedUser = getCommentUser(entry.userId);
          return `
            <div class="comments-history-item__nested">
              <div class="comments-history-item__head">
                <span class="comment-card__avatar" style="background:${nestedUser.color}">${nestedUser.short}</span>
                <div>
                  <div class="comments-history-item__name">${escapeHtml(nestedUser.name)}</div>
                  <div class="comments-history-item__date">${escapeHtml(entry.date)}</div>
                </div>
              </div>
              <div class="comments-history-item__text">${formatCommentText(entry.text)}</div>
            </div>
          `;
        }).join("")}</div>`
      : "";
    return `
      <article class="comments-history-item" data-history-id="${item.id}">
        <div class="comments-history-item__head">
          <span class="comment-card__avatar" style="background:${user.color}">${user.short}</span>
          <div>
            <div class="comments-history-item__name">${escapeHtml(user.name)}</div>
            <div class="comments-history-item__date">${escapeHtml(item.date)}</div>
          </div>
          <span class="comments-history-item__status">${escapeHtml(item.statusText || "")}</span>
        </div>
        ${item.preview ? `<div class="comments-history-item__preview">${escapeHtml(item.preview)}</div>` : ""}
        ${item.thumb ? `<div class="comments-history-item__thumb"><img src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=240&auto=format&fit=crop&q=80" alt="История комментария"></div>` : ""}
        <div class="comments-history-item__text">${formatCommentText(item.text || "")}</div>
        ${actions}
        ${(item.thread || []).length ? `<button class="comments-history-item__toggle" data-history-action="toggle-thread" data-history-id="${item.id}" type="button">${expanded ? "Скрыть ветку" : escapeHtml(item.toggleLabel || "Показать ветку")}</button>` : ""}
        ${nested}
      </article>
    `;
  }).join("");

  commentsHistoryFooter.innerHTML = collectHistoryItems(pageItems, page, totalPages);
}

async function openHistoryModal(mode = "list") {
  ensureHistorySeed();
  commentHistoryMode = mode;
  if (mode === "list" && commentPageId) {
    try {
      await syncThreadsFromServer();
    } catch (error) {
      console.warn("Failed to load comment history", error);
      commentHistoryMode = "error";
    }
  }
  commentsHistoryModal.classList.add("is-open");
  renderHistoryModal();
}

function closeHistoryModal() {
  commentsHistoryModal.classList.remove("is-open");
}

function initializeCommentsSystem() {
  if (!commentAnchorLayer || !commentsPanel || !bodyEditor) {
    return;
  }

  seedCommentsDemoDocumentIfNeeded();
  ensureHistorySeed();
  renderActorPicker();
  renderCommentsPanel();
  scheduleCommentAnchors();
  ensureCommentPage().catch((error) => console.warn("Failed to ensure comment page", error));

  if (commentsActorSelect) {
    commentsActorSelect.addEventListener("change", () => {
      currentCommentActorId = commentsActorSelect.value || "ivan";
      window.localStorage.setItem(commentActorStorageKey, currentCommentActorId);
      renderActorPicker();
      renderCommentsPanel();
    });
  }

  if (commentObserver) {
    commentObserver.disconnect();
  }
  commentObserver = new MutationObserver(() => {
    if (commentOpenTargetId) {
      const thread = getThread(commentOpenTargetId);
      if (thread) {
        const target = document.querySelector(`[data-comment-target-id="${commentOpenTargetId}"]`);
        thread.preview = getTargetPreview(target);
      }
    }
    scheduleCommentAnchors();
    renderCommentsPanel();
  });
  commentObserver.observe(bodyEditor, { childList: true, subtree: true, characterData: true });

  commentAnchorLayer.addEventListener("click", (event) => {
    const button = event.target.closest("[data-comment-target]");
    if (!button) {
      return;
    }
    openThreadForTarget(button.dataset.commentTarget, true);
  });

  commentsCloseButton.addEventListener("click", closeCommentsPanel);
  commentsResolveButton.addEventListener("click", () => {
    toggleResolvedThread().catch((error) => console.warn("Failed to toggle resolved state", error));
  });
  commentsRetryButton.addEventListener("click", () => {
    if (!commentOpenTargetId) {
      return;
    }
    const thread = getOrCreateThread(commentOpenTargetId);
    thread.demoState = "ready";
    openThreadForTarget(commentOpenTargetId, true);
  });
  commentsReplyCancel.addEventListener("click", () => {
    commentReplyTo = null;
    renderCommentsPanel();
  });

  commentsComposerInput.addEventListener("input", () => {
    renderMentionDropdown();
    updateComposerState();
  });
  commentsComposerInput.addEventListener("keydown", (event) => {
    if (commentsMentionDropdown.classList.contains("is-open")) {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        commentMentionIndex = (commentMentionIndex + 1) % commentMentionCandidates.length;
        renderMentionDropdown();
        return;
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        commentMentionIndex = (commentMentionIndex - 1 + commentMentionCandidates.length) % commentMentionCandidates.length;
        renderMentionDropdown();
        return;
      }
      if (event.key === "Enter" && commentMentionCandidates[commentMentionIndex]) {
        event.preventDefault();
        applyMention(commentMentionCandidates[commentMentionIndex].id);
        return;
      }
    }
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      addCommentToThread();
    }
  });
  commentsComposerSend.addEventListener("click", () => {
    addCommentToThread().catch((error) => console.warn("Failed to add comment", error));
  });

  commentsMentionDropdown.addEventListener("mousedown", (event) => event.preventDefault());
  commentsMentionDropdown.addEventListener("click", (event) => {
    const button = event.target.closest("[data-mention-user]");
    if (!button) {
      return;
    }
    applyMention(button.dataset.mentionUser);
  });

  commentsPanelList.addEventListener("click", (event) => {
    const actionTarget = event.target.closest("[data-comment-action]");
    if (!actionTarget || !commentOpenTargetId) {
      return;
    }
    const thread = getOrCreateThread(commentOpenTargetId);
    const commentId = actionTarget.dataset.commentId;
    const comment = getComment(thread, commentId);
    const action = actionTarget.dataset.commentAction;

    if (action === "like" && comment) {
      if (commentPageId) {
        commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/like`, {
          method: "POST",
          body: JSON.stringify({ author: getCurrentCommentActor().id })
        }).then(async () => {
          await syncThreadsFromServer();
          renderCommentsPanel();
          scheduleCommentAnchors();
        }).catch((error) => console.warn("Failed to toggle like", error));
      } else {
        comment.likes = (comment.likes || 0) + 1;
        renderCommentsPanel();
      }
      return;
    }
    if (action === "reply" && comment) {
      commentReplyTo = comment.id;
      renderCommentsPanel();
      commentsComposerInput.focus();
      return;
    }
    if (action === "menu") {
      commentMenuOpenId = commentMenuOpenId === commentId ? null : commentId;
      renderCommentsPanel();
      return;
    }
    if (action === "edit" && comment) {
      commentEditingId = comment.id;
      commentMenuOpenId = null;
      renderCommentsPanel();
      requestAnimationFrame(() => {
        const input = commentsPanelList.querySelector(`[data-comment-edit-input="${comment.id}"]`);
        if (input) {
          input.focus();
          input.setSelectionRange(input.value.length, input.value.length);
        }
      });
      return;
    }
    if (action === "delete" && comment) {
      const isRootMessage = thread.comments[0] && thread.comments[0].id === comment.id;
      const request = commentPageId
        ? (
            isRootMessage
              ? commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}`, {
                  method: "DELETE",
                  body: JSON.stringify({ author: getCurrentCommentActor().id })
                })
              : commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/messages/${encodeURIComponent(comment.id)}`, {
                  method: "DELETE",
                  body: JSON.stringify({ author: getCurrentCommentActor().id })
                })
          )
        : Promise.resolve().then(() => {
            thread.comments = thread.comments.filter((item) => item.id !== comment.id);
            thread.badgeCount = Math.max(thread.comments.length, thread.badgeCount ? thread.badgeCount - 1 : 0);
            addHistorySnapshot(thread, "Удалена " + new Date().toLocaleDateString("ru-RU") + " в " + new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }), comment);
          });
      request.then(async () => {
        if (commentPageId) {
          await syncThreadsFromServer();
        }
        commentMenuOpenId = null;
        commentEditingId = null;
        commentReplyTo = null;
        const nextThread = getThread(commentOpenTargetId);
        commentPanelMode = nextThread && nextThread.comments.length ? "list" : "empty";
        renderCommentsPanel();
        scheduleCommentAnchors();
      }).catch((error) => console.warn("Failed to delete comment", error));
      return;
    }
    if (action === "save-edit" && comment) {
      const input = commentsPanelList.querySelector(`[data-comment-edit-input="${comment.id}"]`);
      const nextValue = input ? input.value.trim() : "";
      if (!nextValue) {
        return;
      }
      const request = commentPageId
        ? commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/messages/${encodeURIComponent(comment.id)}`, {
            method: "PUT",
            body: JSON.stringify({ body: nextValue })
          })
        : Promise.resolve().then(() => {
            comment.text = nextValue;
          });
      request.then(async () => {
        if (commentPageId) {
          await syncThreadsFromServer();
        }
        commentEditingId = null;
        renderCommentsPanel();
      }).catch((error) => console.warn("Failed to save comment edit", error));
    }
  });

  commentsTopTrigger.addEventListener("click", (event) => {
    event.stopPropagation();
    commentsTopDropdown.classList.toggle("is-open");
    commentsAccessPopup.classList.remove("is-open");
  });
  commentsHistoryButton.addEventListener("click", (event) => {
    event.stopPropagation();
    commentsTopDropdown.classList.remove("is-open");
    openHistoryModal(event.shiftKey ? "error" : "list").catch((error) => console.warn("Failed to open history", error));
  });
  commentsAccessButton.addEventListener("click", (event) => {
    event.stopPropagation();
    commentsAccessPopup.classList.toggle("is-open");
  });
  commentsHistoryClose.addEventListener("click", closeHistoryModal);
  commentsHistoryModal.addEventListener("click", (event) => {
    if (event.target === commentsHistoryModal) {
      closeHistoryModal();
      return;
    }
    const actionNode = event.target.closest("[data-history-action]");
    if (!actionNode) {
      return;
    }
    const action = actionNode.dataset.historyAction;
    if (action === "toggle-thread") {
      const historyId = actionNode.dataset.historyId;
      if (commentHistoryExpanded.has(historyId)) {
        commentHistoryExpanded.delete(historyId);
      } else {
        commentHistoryExpanded.add(historyId);
      }
      renderHistoryModal();
      return;
    }
    if (action === "page") {
      commentHistoryPage = Number(actionNode.dataset.historyPage || 1);
      renderHistoryModal();
      return;
    }
    if (action === "next") {
      commentHistoryPage = Math.min(commentHistoryPage + 1, 10);
      renderHistoryModal();
      return;
    }
    if (action === "retry") {
      commentHistoryMode = "list";
      renderHistoryModal();
    }
  });

  document.addEventListener("click", (event) => {
    if (!commentsTopbar.contains(event.target)) {
      commentsTopDropdown.classList.remove("is-open");
      commentsAccessPopup.classList.remove("is-open");
    }
    if (!commentsPanel.contains(event.target)) {
      commentMenuOpenId = null;
      if (commentEditingId && !commentsPanel.contains(event.target)) {
        commentEditingId = null;
      }
      renderCommentsPanel();
    }
  });

  editorCanvas.addEventListener("scroll", scheduleCommentAnchors, { passive: true });
  window.addEventListener("resize", scheduleCommentAnchors);
  document.addEventListener("mouseup", scheduleCommentAnchors);
  bodyEditor.addEventListener("input", scheduleCommentAnchors);
  bodyEditor.addEventListener("keyup", scheduleCommentAnchors);
  bodyEditor.addEventListener("mouseup", scheduleCommentAnchors);
  bodyEditor.addEventListener("input", scheduleCommentDocumentSave);
  titleEditor.addEventListener("input", scheduleCommentDocumentSave);
  titleEditor.addEventListener("keyup", scheduleCommentDocumentSave);

  document.querySelectorAll('input[name="commentAccess"]').forEach((input) => {
    input.addEventListener("change", async () => {
      const nextMode = input.value === "author" ? "owner_only" : "all_users";
      commentAccessMode = nextMode;
      if (commentPageId) {
        try {
          await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comment-access`, {
            method: "PUT",
            body: JSON.stringify({ mode: nextMode })
          });
        } catch (error) {
          console.warn("Failed to save comment access", error);
        }
      }
    });
  });

  window.setTimeout(scheduleCommentAnchors, 420);
  window.setTimeout(scheduleCommentAnchors, 980);
  window.setTimeout(scheduleCommentAnchors, 1400);
  ensureCommentSocket();
  commentSyncTimer = window.setInterval(() => {
    if (!commentPageId || !commentsPanel.classList.contains("is-open")) {
      return;
    }
    syncThreadsFromServer().then(() => {
      renderCommentsPanel();
      scheduleCommentAnchors();
    }).catch(() => {});
  }, 6000);
  window.addEventListener("beforeunload", () => {
    if (commentSocketReconnectTimer) {
      clearTimeout(commentSocketReconnectTimer);
    }
    if (commentSocket && commentSocket.readyState === WebSocket.OPEN) {
      commentSocket.close();
    }
  });
}

window.initializeCommentsSystem = initializeCommentsSystem;
