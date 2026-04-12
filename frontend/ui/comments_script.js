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
const commentsPauseButton = document.getElementById("commentsPauseButton");
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
const commentsHistoryPageSelect = document.getElementById("commentsHistoryPageSelect");
const commentsHistoryThreadSelect = document.getElementById("commentsHistoryThreadSelect");
const accountSwitcher = document.getElementById("accountSwitcher");
const accountTrigger = document.getElementById("accountTrigger");
const accountMenu = document.getElementById("accountMenu");
const accountAvatar = document.getElementById("accountAvatar");
const pagesSwitcher = document.getElementById("pagesSwitcher");
const pagesTrigger = document.getElementById("pagesTrigger");
const pagesMenu = document.getElementById("pagesMenu");
const pagesList = document.getElementById("pagesList");
const pagesCreateButton = document.getElementById("pagesCreateButton");
const pagesCount = document.getElementById("pagesCount");
const pagePresence = document.getElementById("pagePresence");
const pagePresenceAvatars = document.getElementById("pagePresenceAvatars");
const pagePresenceCount = document.getElementById("pagePresenceCount");
const docHeaderTitle = document.getElementById("docHeaderTitle");
const docHeaderSubtitle = document.getElementById("docHeaderSubtitle");

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
let commentHistorySelectedPageId = "";
let commentHistorySelectedThreadId = "";
let commentHistoryThreadOptions = [];
let commentHistoryLoadedPageId = "";
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
const commentApiBase = (() => {
  try {
    const host = window.parent && window.parent.location && window.parent.location.hostname
      ? window.parent.location.hostname
      : (window.location.hostname || "127.0.0.1");
    const protocol = window.parent && window.parent.location && window.parent.location.protocol === "https:"
      ? "https://"
      : "http://";
    return `${protocol}${host}:3000`;
  } catch (error) {
    return "http://127.0.0.1:3000";
  }
})();
const commentPageStorageKey = "wikilive-comment-page-id-v2";
let commentPageId = "";
let commentAccessMode = "all_users";
let commentBootstrapPromise = null;
let commentSaveTimer = null;
let commentSyncTimer = null;
let commentSocket = null;
let commentSocketPageId = "";
let commentHoverClearTimer = null;
let commentSocketReconnectTimer = null;
const commentActorStorageKey = "wikilive-comment-actor-id-v2";
let currentCommentActorId = window.localStorage.getItem(commentActorStorageKey) || "ivan";
let commentSelectionDraft = null;
let commentPendingVersionLabel = "";
let commentPendingVersionAuthor = "";
let commentSyncPromise = null;
let commentHistoryPromise = null;
let commentAccessPromise = null;
let commentPagesPromise = null;
let commentCleanupTimer = null;
let commentSaveInFlight = false;
let commentSaveQueued = false;
let commentHoveredTargetId = "";
let commentPages = [];
let commentPresencePeople = [];
let commentApplyingDocument = false;

function commentIconSvg() {
  return '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 3.5h11v7h-7l-2.8 2V10.5H2.5z"></path><path d="M5.2 6.2h5.6M5.2 8.2h3.4"></path></svg>';
}

function commentPlusSvg() {
  return '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3.2v9.6M3.2 8h9.6"></path></svg>';
}

function getCurrentCommentActor() {
  return getCommentUser(currentCommentActorId || "ivan");
}

function getCurrentCommentPageStorageKey(actorId = currentCommentActorId) {
  return `${commentPageStorageKey}:${normalizeActorId(actorId || "viewer")}`;
}

function isCurrentActorPage(page) {
  return normalizeActorId(page && page.ownerId ? page.ownerId : "viewer") === normalizeActorId(currentCommentActorId || "viewer");
}

function upsertCommentPage(page) {
  if (!page || !page.pageId) {
    return;
  }
  const nextPages = (commentPages || []).filter((item) => item.pageId !== page.pageId);
  nextPages.push(page);
  nextPages.sort((left, right) => String(right.updatedAt || "").localeCompare(String(left.updatedAt || "")));
  commentPages = nextPages;
}

function renderPagePresence() {
  if (!pagePresence || !pagePresenceAvatars || !pagePresenceCount) {
    return;
  }

  const people = Array.isArray(commentPresencePeople) ? commentPresencePeople : [];
  pagePresenceAvatars.innerHTML = people.slice(0, 4).map((person) => `
    <span
      class="page-presence__avatar"
      title="${escapeHtml(person.actorName || person.actorId || "Участник")}"
      style="background:${escapeHtml(person.actorColor || "#a6afbf")}"
    >${escapeHtml(person.actorShort || "?")}</span>
  `).join("");
  pagePresenceCount.textContent = String(people.length);
  pagePresence.classList.toggle("is-empty", people.length === 0);
}

function renderPagesSwitcher() {
  if (!pagesSwitcher || !pagesList || !pagesCount) {
    renderPagePresence();
    return;
  }

  const ownedPages = (commentPages || []).filter((page) => isCurrentActorPage(page));
  pagesCount.textContent = String(ownedPages.length);
  if (!ownedPages.length) {
    pagesList.innerHTML = '<div class="pages-switcher__empty">Пока нет страниц</div>';
    renderPagePresence();
    return;
  }

  pagesList.innerHTML = ownedPages.map((page) => {
    const isActive = page.pageId === commentPageId;
    const preview = String(page.title || "Без названия").trim() || "Без названия";
    const headingCount = extractPageHeadingTargets(page).length;
    return `
      <button class="pages-switcher__item${isActive ? " is-active" : ""}" data-page-id="${page.pageId}" type="button">
        <span class="pages-switcher__item-title">${escapeHtml(preview)}</span>
        <span class="pages-switcher__item-meta">${headingCount ? `${headingCount} заголовков` : "Без разделов"}</span>
      </button>
    `;
  }).join("");
  renderPagePresence();
}

function renderAccountSwitcher() {
  if (!accountSwitcher || !accountAvatar) {
    return;
  }
  const actor = getCurrentCommentActor();
  accountAvatar.textContent = actor.short || "Г";
  accountAvatar.style.background = actor.color || "#a6afbf";
  accountAvatar.style.color = "#ffffff";
  accountMenu.querySelectorAll("[data-account-user]").forEach((item) => {
    item.classList.toggle("is-active", item.dataset.accountUser === currentCommentActorId);
  });
}

function setCurrentCommentActor(actorId, persist = true) {
  currentCommentActorId = actorId || "viewer";
  if (persist) {
    window.localStorage.setItem(commentActorStorageKey, currentCommentActorId);
  }
  renderActorPicker();
  renderAccountSwitcher();
  renderCommentsPanel();
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
    renderAccountSwitcher();
    return;
  }

  const actorOptions = commentUsers.map((user) => {
    const selected = user.id === currentCommentActorId ? " selected" : "";
    return `<option value="${user.id}"${selected}>${escapeHtml(user.name)} · ${escapeHtml(user.role)}</option>`;
  });
  if (!commentUsers.some((user) => user.id === currentCommentActorId)) {
    actorOptions.unshift('<option value="viewer" selected>Гость · Наблюдатель</option>');
  }
  commentsActorSelect.innerHTML = actorOptions.join("");

  const actor = getCurrentCommentActor();
  if (commentsActorNote) {
    commentsActorNote.textContent = `${actor.team} · ${actor.nick}`;
  }
  if (commentsGroupHints) {
    commentsGroupHints.innerHTML = commentGroups.slice(0, 3).map((group) => `<span class="comments-panel__group-hint">@${escapeHtml(group.handle)}</span>`).join("");
  }
  renderAccountSwitcher();
}

function extractPageHeadingTargets(page) {
  if (!page || !page.pageId) {
    return [];
  }

  const container = document.createElement("div");
  container.innerHTML = page.content || "";
  const items = [];

  const title = String(page.title || "").trim();
  if (title) {
    items.push({
      kind: "page",
      pageId: page.pageId,
      label: title,
      level: "PAGE",
      href: `wikilive://page/${encodeURIComponent(page.pageId)}`,
    });
  }

  Array.from(container.querySelectorAll("h1, h2, h3")).forEach((heading, index) => {
    const label = heading.textContent.replace(/\u200B/g, "").trim();
    if (!label) {
      return;
    }
    items.push({
      kind: "heading",
      pageId: page.pageId,
      label,
      level: heading.tagName.toUpperCase(),
      anchorId: `heading-${index + 1}`,
      href: `wikilive://page/${encodeURIComponent(page.pageId)}#heading-${index + 1}`,
    });
  });

  return items;
}

function buildWikiLiveLinkSections() {
  const currentPage = {
    pageId: commentPageId,
    title: titleEditor.textContent.replace(/\u200B/g, "").trim() || "Новая страница",
    content: bodyEditor.innerHTML || "",
    ownerId: currentCommentActorId,
    ownerName: getCurrentCommentActor().name,
  };

  const sections = [];
  const currentItems = extractPageHeadingTargets(currentPage);
  sections.push({
    id: "current-page",
    title: "Текущая страница",
    open: true,
    items: currentItems,
  });

  const otherPages = (commentPages || []).filter((page) => page.pageId && page.pageId !== commentPageId);
  otherPages.forEach((page) => {
    sections.push({
      id: `page-${page.pageId}`,
      title: page.title || "Без названия",
      subtitle: page.ownerName || "",
      open: false,
      items: extractPageHeadingTargets(page),
    });
  });

  const discussionItems = Array.from(commentThreads.values())
    .filter((thread) => thread && thread.targetId && thread.preview)
    .map((thread) => ({
      kind: "discussion",
      pageId: commentPageId,
      label: thread.preview,
      level: "DISC",
      href: `wikilive://discussion/${encodeURIComponent(thread.targetId)}`,
    }));
  if (discussionItems.length) {
    sections.push({
      id: "discussions",
      title: "Обсуждения",
      open: false,
      items: discussionItems,
    });
  }

  return sections.filter((section) => Array.isArray(section.items) && section.items.length);
}

window.getWikiLiveLinkTargets = function getWikiLiveLinkTargets() {
  return buildWikiLiveLinkSections();
};

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

function resolveCommentPageLink(label) {
  const normalizedLabel = normalizePreviewText(label || "");
  if (!normalizedLabel) {
    return "";
  }
  const page = (commentPages || []).find((item) => normalizePreviewText(item.title || "") === normalizedLabel);
  if (!page || !page.pageId) {
    return "";
  }
  return `wikilive://page/${encodeURIComponent(page.pageId)}`;
}

function formatCommentText(text) {
  let safe = escapeHtml(text).replace(/\n/g, "<br>");
  safe = safe.replace(/\[\[([^\]]+)\]\]/g, (match, rawLabel) => {
    const label = String(rawLabel || "").trim();
    const href = resolveCommentPageLink(label);
    if (!href) {
      return `<span class="comment-mention">[[${escapeHtml(label)}]]</span>`;
    }
    return `<a href="${href}" data-comment-link="page">${escapeHtml(label)}</a>`;
  });
  safe = safe.replace(/(https?:\/\/[^\s<]+)/g, (match) => {
    return `<a href="${match}" target="_blank" rel="noopener noreferrer" data-comment-link="external">${match}</a>`;
  });
  return safe.replace(/(^|\s)(@[a-zA-Zа-яА-Я0-9._-]+)/g, (match, prefix, mention) => prefix + '<span class="comment-mention">' + mention + "</span>");
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
    likedBy: Array.isArray(extra.likedBy) ? [...extra.likedBy] : [],
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
    likedBy: options.likedBy || [],
    iconOnly: Boolean(options.iconOnly),
    targetType: options.targetType || "",
    targetLabel: options.targetLabel || ""
  };
}

function cloneCommentState(comment) {
  return createComment(comment.id, comment.userId, comment.date, comment.text, {
    likes: comment.likes || 0,
    likedBy: Array.isArray(comment.likedBy) ? [...comment.likedBy] : [],
    replyTo: comment.replyTo || null,
    editable: comment.editable !== false,
    attachmentType: comment.attachmentType || "",
    attachmentLabel: comment.attachmentLabel || "",
    targetPreview: comment.targetPreview || "",
    targetType: comment.targetType || ""
  });
}

function cloneThreadState(thread) {
  return createThread(thread.id, thread.targetId, {
    badgeCount: thread.badgeCount || 0,
    status: thread.status || "open",
    demoState: thread.demoState || "ready",
    preview: thread.preview || "",
    comments: (thread.comments || []).map((comment) => cloneCommentState(comment)),
    likedBy: Array.isArray(thread.likedBy) ? [...thread.likedBy] : [],
    iconOnly: Boolean(thread.iconOnly),
    targetType: thread.targetType || "",
    targetLabel: thread.targetLabel || ""
  });
}

async function commentApiRequest(path, options = {}) {
  const controller = new AbortController();
  const timeoutMs =
    typeof options.timeoutMs === "number" && Number.isFinite(options.timeoutMs)
      ? options.timeoutMs
      : 12000;
  const requestOptions = { ...options };
  delete requestOptions.timeoutMs;
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
  let response;
  try {
    response = await fetch(commentApiBase + path, {
      headers: {
        "Content-Type": "application/json"
      },
      ...requestOptions,
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

async function loadPagesCatalog(force = false) {
  if (commentPagesPromise && !force) {
    return commentPagesPromise;
  }

  commentPagesPromise = commentApiRequest("/api/pages", { timeoutMs: 12000 })
    .then((pagesData) => {
      commentPages = (pagesData.items || []).slice().sort((left, right) => {
        return String(right.updatedAt || "").localeCompare(String(left.updatedAt || ""));
      });
      renderPagesSwitcher();
      return commentPages;
    })
    .finally(() => {
      commentPagesPromise = null;
    });

  return commentPagesPromise;
}

function updateDocumentHeader(page) {
  if (docHeaderTitle) {
    docHeaderTitle.textContent = (page && page.title) || "Новая страница";
  }
  if (docHeaderSubtitle) {
    const nextDescription = String(page && page.description ? page.description : "").trim();
    docHeaderSubtitle.textContent = nextDescription || "Добавить описание";
    docHeaderSubtitle.classList.toggle("is-placeholder", !nextDescription);
  }
}

function getDocumentDescriptionText() {
  if (!docHeaderSubtitle) {
    return "";
  }
  const text = docHeaderSubtitle.textContent.replace(/\u200B/g, "").trim();
  if (!text || text === "Добавить описание") {
    return "";
  }
  return text;
}

function syncDocumentSubtitlePlaceholder(forcePlaceholder = false) {
  if (!docHeaderSubtitle) {
    return;
  }
  const text = docHeaderSubtitle.textContent.replace(/\u200B/g, "").trim();
  const shouldPlaceholder = forcePlaceholder || !text;
  docHeaderSubtitle.classList.toggle("is-placeholder", shouldPlaceholder);
  if (shouldPlaceholder) {
    docHeaderSubtitle.textContent = "Добавить описание";
  }
}

async function saveCommentDocumentNow(label = "Изменение текста", author = "editor") {
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
    const documentPayload = serializeEditorDocument();
    documentPayload.versionLabel = commentPendingVersionLabel || label || "Изменение текста";
    documentPayload.versionAuthor = commentPendingVersionAuthor || author || "editor";
    documentPayload.ownerId = normalizeActorId(currentCommentActorId || "viewer");
    documentPayload.ownerName = getCurrentCommentActor().name || "Гость";
    const response = await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}`, {
      method: "PUT",
      body: JSON.stringify(documentPayload),
      timeoutMs: 20000
    });
    const savedPage = response.item || {
      pageId: commentPageId,
      ...documentPayload,
      updatedAt: new Date().toISOString(),
    };
    upsertCommentPage(savedPage);
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
    description: getDocumentDescriptionText(),
    content: bodyEditor.innerHTML
  };
}

async function seedServerDemoThreadsIfNeeded(pageId) {
  return;
}

function applyEditorDocument(page) {
  if (!page) {
    return;
  }
  titleEditor.textContent = page.title || "Страница для комментирования";
  bodyEditor.innerHTML = page.content && page.content.trim() ? page.content : `<p class="body-placeholder">${emptyHint}</p>`;
  renderOutline();
}

function queueCommentVersionLabel(label, author = "editor") {
  if (!label) {
    return;
  }
  commentPendingVersionLabel = label;
  commentPendingVersionAuthor = author || "editor";
}

async function createCommentVersion(label, author = getCurrentCommentActor().id) {
  if (!commentPageId || !label) {
    return;
  }
  await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/versions`, {
    method: "POST",
    body: JSON.stringify({ label, author })
  });
  if (window.refreshTimeMachinePanel) {
    window.refreshTimeMachinePanel();
  }
}

function classifyMutationLabel(mutations) {
  let sawImageChange = false;
  let sawFileChange = false;
  let sawDataChange = false;
  let sawDeletion = false;

  mutations.forEach((mutation) => {
    if (mutation.type !== "childList") {
      return;
    }
    sawDeletion = sawDeletion || Boolean(mutation.removedNodes && mutation.removedNodes.length);
    Array.from(mutation.addedNodes || []).forEach((node) => {
      if (!(node instanceof HTMLElement)) {
        return;
      }
      if (node.classList.contains("comment-selection-target")) {
        return;
      }
      if (node.matches(".embedded-image-block") || node.querySelector(".embedded-image-block")) {
        sawImageChange = true;
      }
      if (node.matches(".embedded-file-chip") || node.querySelector(".embedded-file-chip")) {
        sawFileChange = true;
      }
      if (
        node.matches("[data-live-token], [data-live-value], .live-data-chip, .formula-chip, .table-value-chip, table") ||
        node.querySelector("[data-live-token], [data-live-value], .live-data-chip, .formula-chip, .table-value-chip, table")
      ) {
        sawDataChange = true;
      }
    });
  });

  if (sawImageChange) {
    return "Вставка медиа";
  }
  if (sawFileChange) {
    return "Вставка объекта";
  }
  if (sawDataChange) {
    return "Вставка данных из таблицы";
  }
  if (sawDeletion) {
    return "Удаление содержимого";
  }
  return "";
}

function scheduleCommentDocumentSave(label = "", author = "editor") {
  if (!commentPageId) {
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
    commentSaveInFlight = true;
    try {
      const documentPayload = serializeEditorDocument();
      documentPayload.versionLabel = commentPendingVersionLabel || label || "Изменение текста";
      documentPayload.versionAuthor = commentPendingVersionAuthor || author || "editor";
      await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}`, {
        method: "PUT",
        body: JSON.stringify(documentPayload),
        timeoutMs: 20000
      });
      commentPendingVersionLabel = "";
      commentPendingVersionAuthor = "";
      if (window.refreshTimeMachinePanel) {
        window.refreshTimeMachinePanel();
      }
    } catch (error) {
      console.warn("Failed to save comment page", error);
    } finally {
      commentSaveInFlight = false;
      if (commentSaveQueued) {
        commentSaveQueued = false;
        scheduleCommentDocumentSave(commentPendingVersionLabel || label, commentPendingVersionAuthor || author);
      }
    }
  }, 1100);
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
      likes: message.likeCount || 0,
      likedBy: Array.isArray(message.likedBy) ? message.likedBy : [],
      replyTo: message.replyToMessageId || null,
      attachmentType: index === 0 ? threadAttachment.attachmentType : "",
      attachmentLabel: index === 0 ? threadAttachment.attachmentLabel : "",
      targetPreview: item.targetPreview || item.selectionLabel || "",
      targetType: item.targetType || ""
    }
  ));
  return createThread(item.threadId, resolvedTargetId, {
    badgeCount: item.messages ? item.messages.length : 0,
    status: item.paused ? "paused" : (item.resolved ? "resolved" : "open"),
    preview: item.targetPreview || item.selectionLabel || "",
    comments,
    likedBy: Array.isArray(item.likedBy) ? item.likedBy : [],
    iconOnly: !(item.messages || []).length,
    targetType: item.targetType || "",
    targetLabel: getThreadTargetLabel(item.targetType || "")
  });
}

async function loadCommentHistoryFromServer(force = false, pageId = commentHistorySelectedPageId || commentPageId) {
  const historyPageId = pageId || commentPageId;
  if (!historyPageId) {
    return [];
  }
  if (commentHistoryPromise && !force && commentHistoryLoadedPageId === historyPageId) {
    return commentHistoryPromise;
  }
  commentHistoryLoadedPageId = historyPageId;
  commentHistoryPromise = commentApiRequest(`/api/pages/${encodeURIComponent(historyPageId)}/comments/history`, {
    timeoutMs: 14000
  })
    .then((historyData) => {
      commentHistoryItems = (historyData.items || []).map((item) => {
        const messages = item.messages || [];
        const rootMessage = messages.find((message) => !message.replyToMessageId) || messages[0] || null;
        const replies = rootMessage
          ? messages.filter((message) => message.messageId !== rootMessage.messageId)
          : messages;
        const preview = item.targetPreview || item.selectionLabel || "";
        const attachment = inferAttachmentForThread(item.targetType || "", preview);
        return {
          id: item.threadId,
          pageId: historyPageId,
          userId: rootMessage ? rootMessage.author : "ivan",
          date: formatThreadDate((rootMessage && (rootMessage.updatedAt || rootMessage.createdAt)) || item.createdAt),
          statusText: formatHistoryStatus(item),
          resolved: Boolean(item.resolved),
          resolvedAt: item.resolvedAt || "",
          paused: Boolean(item.paused),
          pausedAt: item.pausedAt || "",
          deleted: Boolean(item.deleted),
          deletedAt: item.deletedAt || "",
          preview,
          text: rootMessage ? rootMessage.body : preview,
          likes: rootMessage ? (rootMessage.likeCount || 0) : (item.likeCount || 0),
          thumb: attachment.attachmentType === "image",
          attachmentType: attachment.attachmentType || "",
          attachmentLabel: attachment.attachmentLabel || "",
          targetType: item.targetType || "",
          thread: replies.map((message) => ({
            userId: message.author,
            date: formatThreadDate(message.updatedAt || message.createdAt),
            text: message.body,
            deleted: Boolean(message.deleted)
          })),
          toggleLabel: formatThreadCommentsLabel(replies.length)
        };
      });
      return commentHistoryItems;
    })
    .finally(() => {
      commentHistoryPromise = null;
    });
  return commentHistoryPromise;
}

async function loadCommentAccessFromServer(force = false) {
  if (!commentPageId) {
    return "all_users";
  }
  if (commentAccessPromise && !force) {
    return commentAccessPromise;
  }
  commentAccessPromise = commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comment-access`, {
    timeoutMs: 10000
  })
    .then((accessData) => {
      commentAccessMode = accessData.mode || "all_users";
      document.querySelectorAll('input[name="commentAccess"]').forEach((input) => {
        input.checked = input.value === (commentAccessMode === "owner_only" ? "author" : "all");
      });
      return commentAccessMode;
    })
    .finally(() => {
      commentAccessPromise = null;
    });
  return commentAccessPromise;
}

async function loadHistoryThreadOptions(pageId, force = false) {
  const historyPageId = pageId || commentPageId;
  if (!historyPageId) {
    commentHistoryThreadOptions = [];
    return [];
  }

  const [activeData, historyData] = await Promise.all([
    commentApiRequest(`/api/pages/${encodeURIComponent(historyPageId)}/comments`, {
      timeoutMs: 12000
    }).catch(() => ({ items: [] })),
    commentApiRequest(`/api/pages/${encodeURIComponent(historyPageId)}/comments/history`, {
      timeoutMs: 12000
    }).catch(() => ({ items: [] }))
  ]);

  const threadMap = new Map();
  [...(activeData.items || []), ...(historyData.items || [])].forEach((item) => {
    if (!item || !item.threadId) {
      return;
    }
    if (!threadMap.has(item.threadId)) {
      threadMap.set(item.threadId, {
        threadId: item.threadId,
        preview: item.targetPreview || item.selectionLabel || "Без названия обсуждения",
        targetType: item.targetType || "",
        status: item.deleted ? "deleted" : (item.paused ? "paused" : (item.resolved ? "resolved" : "open"))
      });
    }
  });

  commentHistoryThreadOptions = Array.from(threadMap.values());
  return commentHistoryThreadOptions;
}

function renderHistoryFilters() {
  if (!commentsHistoryPageSelect || !commentsHistoryThreadSelect) {
    return;
  }

  const accessiblePages = getAccessiblePagesForActor();
  const selectedPageId = commentHistorySelectedPageId || commentPageId || (accessiblePages[0] && accessiblePages[0].pageId) || "";
  commentsHistoryPageSelect.innerHTML = accessiblePages.map((page) => `
    <option value="${page.pageId}"${page.pageId === selectedPageId ? " selected" : ""}>${escapeHtml(page.title || "Без названия")}</option>
  `).join("");

  const options = [{ threadId: "", preview: "Все обсуждения", status: "all" }, ...commentHistoryThreadOptions];
  commentsHistoryThreadSelect.innerHTML = options.map((thread) => {
    let suffix = "";
    if (thread.status === "paused") {
      suffix = " · на паузе";
    } else if (thread.status === "resolved") {
      suffix = " · решена";
    } else if (thread.status === "deleted") {
      suffix = " · удалена";
    }
    return `<option value="${thread.threadId}"${thread.threadId === (commentHistorySelectedThreadId || "") ? " selected" : ""}>${escapeHtml((thread.preview || "Без названия обсуждения") + suffix)}</option>`;
  }).join("");
}

async function syncThreadsFromServer(force = false) {
  if (!commentPageId) {
    return;
  }
  if (commentSyncPromise && !force) {
    return commentSyncPromise;
  }

  commentSyncPromise = commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments`, {
    timeoutMs: 14000
  })
    .then((threadsData) => {
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
      commentInitDone = true;
      return nextThreads;
    })
    .finally(() => {
      commentSyncPromise = null;
    });
  await commentSyncPromise;
  await loadCommentAccessFromServer(force);
}

async function ensureCommentPage() {
  if (commentBootstrapPromise) {
    return commentBootstrapPromise;
  }

  commentBootstrapPromise = (async () => {
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
      const created = await commentApiRequest("/api/pages", {
        method: "POST",
        body: JSON.stringify({
          ...serializeEditorDocument(),
          versionLabel: "Создана страница",
          versionAuthor: "system"
        })
      });
      page = created.item;
    } else {
      const loaded = await commentApiRequest(`/api/pages/${encodeURIComponent(page.pageId)}`);
      page = loaded.item;
      applyEditorDocument(page);
    }

    commentPageId = page.pageId;
    window.localStorage.setItem(commentPageStorageKey, commentPageId);
    await ensurePersistedCommentTargets();
    await syncThreadsFromServer();
    ensureCommentSocket();
    subscribeCommentSocketToPage();
    scheduleCommentAnchors();
    renderCommentsPanel();
    document.dispatchEvent(new CustomEvent("wikilive:page-ready", { detail: { pageId: commentPageId } }));
    return page;
  })().catch((error) => {
    console.warn("Failed to bootstrap comment page", error);
    commentBootstrapPromise = null;
    return null;
  });

  return commentBootstrapPromise;
}

function seedCommentsDemoDocumentIfNeeded() {
  return;
  if (!hasPlaceholder()) {
    return;
  }
  titleEditor.textContent = "Страница для комментирования";
  bodyEditor.innerHTML = commentsDemoParagraphs.map((paragraph) => `<p>${paragraph}</p>`).join("");
  renderOutline();
}

function getCommentableTargets() {
  const directTargets = Array.from(document.querySelectorAll("[data-comment-target-id]")).filter((node) => {
    return node instanceof HTMLElement && (bodyEditor.contains(node) || titleEditor.contains(node));
  });
  const result = [];
  const seen = new Set();
  directTargets.forEach((node) => {
    if (!seen.has(node)) {
      seen.add(node);
      result.push(node);
    }
  });
  return result;
}

function getCommentTargetPrefix(target) {
  if (!(target instanceof HTMLElement)) {
    return "comment-target";
  }
  if (target.classList.contains("comment-selection-target")) {
    return "comment-selection";
  }
  if (target.classList.contains("embedded-image-block")) {
    return "comment-image";
  }
  return "comment-object";
}

function generateCommentTargetId(prefix = "comment-target") {
  const sanitizedPrefix = String(prefix || "comment-target")
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "") || "comment-target";

  let candidate = "";
  do {
    commentTargetCounter += 1;
    const randomPart =
      typeof crypto !== "undefined" && crypto && typeof crypto.randomUUID === "function"
        ? crypto.randomUUID()
        : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}-${commentTargetCounter.toString(36)}`;
    candidate = `${sanitizedPrefix}-${randomPart}`;
  } while (document.querySelector(`[data-comment-target-id="${candidate}"]`));

  return candidate;
}

function ensureTargetId(target) {
  if (!(target instanceof HTMLElement)) {
    return "";
  }
  if (!target.dataset.commentTargetId) {
    target.dataset.commentTargetId = generateCommentTargetId(getCommentTargetPrefix(target));
  }
  return target.dataset.commentTargetId;
}

function normalizeCommentTargetIds() {
  const seenIds = new Set();
  getCommentableTargets().forEach((target) => {
    const currentId = String(target.dataset.commentTargetId || "").trim();
    if (!currentId || seenIds.has(currentId)) {
      target.dataset.commentTargetId = generateCommentTargetId(getCommentTargetPrefix(target));
    }
    seenIds.add(target.dataset.commentTargetId);
  });
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
  if (!expectedPreview) {
    return item.targetId;
  }
  const targets = getCommentableTargets();
  const matches = [];

  targets.forEach((target) => {
    const targetId = ensureTargetId(target);
    const targetPreview = normalizePreviewText(getTargetPreview(target));
    const targetType = inferTargetType(target);
    if (expectedPreview && targetPreview === expectedPreview && (!expectedType || targetType === expectedType)) {
      matches.push(targetId);
    }
  });

  return matches.length === 1 ? matches[0] : item.targetId;
}

async function ensurePersistedCommentTargets() {
  normalizeCommentTargetIds();
  const targets = getCommentableTargets();
  targets.forEach((target) => ensureTargetId(target));
}

function getCurrentSelectionRange() {
  const selection = window.getSelection();
  if (!selection || !selection.rangeCount || selection.isCollapsed) {
    return null;
  }
  const range = selection.getRangeAt(0);
  const text = selection.toString().replace(/\s+/g, " ").trim();
  if (!text) {
    return null;
  }
  if (!bodyEditor.contains(range.commonAncestorContainer) && !titleEditor.contains(range.commonAncestorContainer)) {
    return null;
  }
  const startBlock = typeof findEditableBlock === "function" ? findEditableBlock(range.startContainer) : null;
  const endBlock = typeof findEditableBlock === "function" ? findEditableBlock(range.endContainer) : null;
  if (startBlock && endBlock && startBlock !== endBlock) {
    return null;
  }
  return range.cloneRange();
}

function buildSelectionCommentDraft() {
  if (selectedImageBlock instanceof HTMLElement) {
    const rect = selectedImageBlock.getBoundingClientRect();
    if (rect.width && rect.height) {
      return {
        kind: "object",
        target: selectedImageBlock,
        rect,
        text: getTargetPreview(selectedImageBlock)
      };
    }
  }

  const range = getCurrentSelectionRange();
  if (!range) {
    return null;
  }

  const startContainer = range.startContainer instanceof HTMLElement ? range.startContainer : range.startContainer.parentElement;
  const existingTarget = startContainer ? startContainer.closest("[data-comment-target-id]") : null;
  if (existingTarget) {
    return null;
  }

  const rect = range.getBoundingClientRect();
  if (!rect.width && !rect.height) {
    return null;
  }

  return {
    kind: "text",
    range,
    rect,
    text: range.toString().replace(/\s+/g, " ").trim()
  };
}

function createTargetFromSelectionDraft() {
  if (!commentSelectionDraft) {
    return null;
  }

  if (commentSelectionDraft.kind === "object" && commentSelectionDraft.target instanceof HTMLElement) {
    commentSelectionDraft.target.dataset.commentObject = "1";
    return ensureTargetId(commentSelectionDraft.target);
  }

  if (commentSelectionDraft.kind !== "text" || !commentSelectionDraft.range) {
    return null;
  }

  const range = commentSelectionDraft.range.cloneRange();
  const wrapper = document.createElement("span");
  wrapper.className = "comment-selection-target";
  wrapper.contentEditable = "false";
  wrapper.dataset.commentLocked = "1";
  const targetId = ensureTargetId(wrapper);

  try {
    const content = range.extractContents();
    wrapper.appendChild(content);
    range.insertNode(wrapper);
  } catch (error) {
    console.warn("Failed to wrap selected text into a discussion target", error);
    return null;
  }

  const selection = window.getSelection();
  if (selection) {
    const nextRange = document.createRange();
    nextRange.selectNodeContents(wrapper);
    selection.removeAllRanges();
    selection.addRange(nextRange);
  }

  return targetId;
}

function unwrapCommentTarget(target) {
  if (!(target instanceof HTMLElement)) {
    return null;
  }
  const parent = target.parentNode;
  if (!parent) {
    return null;
  }
  while (target.firstChild) {
    parent.insertBefore(target.firstChild, target);
  }
  const nextFocus = parent;
  parent.removeChild(target);
  return nextFocus;
}

async function dissolveDiscussionTarget(targetId, reason = "Изменение обсуждаемого фрагмента") {
  if (!targetId) {
    return;
  }
  const target = document.querySelector(`[data-comment-target-id="${targetId}"]`);
  const persistedThreadId = await resolvePersistedThreadId(targetId);
  if (commentPageId && persistedThreadId) {
    try {
      await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(persistedThreadId)}`, {
        method: "DELETE",
        body: JSON.stringify({ author: getCurrentCommentActor().id }),
        timeoutMs: 14000
      });
      await createCommentVersion(reason, getCurrentCommentActor().id);
    } catch (error) {
      if (!/not found/i.test(String((error && error.message) || ""))) {
        console.warn("Failed to dissolve discussion target", error);
      }
    }
  }
  commentThreads.delete(targetId);
  if (target && target.classList.contains("comment-selection-target")) {
    unwrapCommentTarget(target);
  }
  if (commentOpenTargetId === targetId) {
    closeCommentsPanel();
  }
  scheduleCommentAnchors();
}

function scheduleOrphanThreadCleanup() {
  if (commentCleanupTimer) {
    clearTimeout(commentCleanupTimer);
  }
  commentCleanupTimer = window.setTimeout(async () => {
    const existingIds = new Set(
      getCommentableTargets().map((target) => ensureTargetId(target))
    );
    const orphanIds = [];
    commentThreads.forEach((thread, targetId) => {
      if (!existingIds.has(targetId)) {
        orphanIds.push(targetId);
      }
    });
    for (const targetId of orphanIds) {
      await dissolveDiscussionTarget(targetId, "Удалено обсуждаемое содержимое");
    }
  }, 260);
}

async function handleProtectedCommentInput(inputType, data) {
  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) {
    return false;
  }
  const selectionRange = selection.getRangeAt(0);
  let node = selection.anchorNode;
  if (node && node.nodeType === Node.TEXT_NODE) {
    node = node.parentElement;
  }
  let lockedTarget = node && node.closest
    ? node.closest(".comment-selection-target[data-comment-target-id]")
    : null;
  if (!lockedTarget && selectionRange) {
    const lockedTargets = Array.from(document.querySelectorAll(".comment-selection-target[data-comment-target-id]"));
    lockedTarget = lockedTargets.find((target) => {
      try {
        return selectionRange.intersectsNode(target);
      } catch (error) {
        return false;
      }
    }) || null;
  }
  if (!lockedTarget) {
    return false;
  }

  const approved = window.confirm("Это обсуждаемый фрагмент. Разорвать обсуждение и отредактировать текст?");
  if (!approved) {
    return true;
  }

  const targetId = lockedTarget.dataset.commentTargetId || "";
  const parent = lockedTarget.parentNode;
  const nextSibling = lockedTarget.nextSibling;
  await dissolveDiscussionTarget(targetId, "Разорвано обсуждение для редактирования");

  if (parent instanceof HTMLElement || parent instanceof HTMLDivElement || parent instanceof HTMLParagraphElement) {
    const range = document.createRange();
    const focusNode = nextSibling && nextSibling.parentNode === parent ? nextSibling : parent;
    range.setStart(focusNode, 0);
    range.collapse(true);
    selection.removeAllRanges();
    selection.addRange(range);
  }

  if (inputType === "insertText" && data) {
    document.execCommand("insertText", false, data);
  }
  return true;
}

window.handleProtectedCommentInput = handleProtectedCommentInput;

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

function ensureHistorySeed() {
  return;
  if (commentHistoryItems.length) {
    return;
  }
  const items = [];
  for (let page = 0; page < 10; page += 1) {
    historySeed.forEach((item, index) => items.push({ ...item, id: item.id + "-" + page + "-" + index }));
  }
  commentHistoryItems = items;
}

function seedThreads(targets) {
  commentInitDone = true;
  return;
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
      likedBy: ["ivan", "sergei"],
      comments: [
        createComment("comment-1", "ivan", "27.10.25 в 18:03", "Думаю этот параграф стоит переписать: читатель спотыкается уже в первой строке.", { targetPreview: getTargetPreview(targets[0]), targetType }),
        createComment("comment-2", "sergei", "27.10.25 в 18:03", "Я бы сократил его почти вдвое и вынес детали ниже отдельным блоком."),
        createComment("comment-3", "anna", "27.10.25 в 18:03", "@design можно еще проверить визуальный акцент на первом предложении."),
        createComment("comment-4", "maria", "27.10.25 в 18:03", "@release если этот текст пойдет в демо, лучше сделать его проще для первого показа.")
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
      likedBy: ["ivan", "maria", "anton"],
      comments: [
        createComment("comment-5", "maxim", "27.10.25 в 18:03", "Этот блок уже согласован. Оставляем формулировку и помечаем ветку как решенную.", { targetPreview: getTargetPreview(targets[2]), targetType })
      ]
    }));
  }
  commentInitDone = true;
}

function getThread(targetId) {
  return commentThreads.get(targetId) || null;
}

function getOrCreateThread(targetId) {
  let thread = getThread(targetId);
  if (!thread) {
    thread = createThread("thread-" + targetId, targetId, {
      preview: getTargetPreview(document.querySelector(`[data-comment-target-id="${targetId}"]`)),
      likedBy: [],
      targetType: inferTargetType(document.querySelector(`[data-comment-target-id="${targetId}"]`)),
      targetLabel: getThreadTargetLabel(inferTargetType(document.querySelector(`[data-comment-target-id="${targetId}"]`)))
    });
    commentThreads.set(targetId, thread);
  }
  return thread;
}

function isSyntheticThreadId(threadId, targetId) {
  return !threadId || threadId === `thread-${targetId}`;
}

async function resolvePersistedThreadId(targetId) {
  const currentThread = getThread(targetId);
  if (currentThread && !isSyntheticThreadId(currentThread.id, targetId)) {
    return currentThread.id;
  }
  if (!commentPageId) {
    return "";
  }
  try {
    await syncThreadsFromServer(true);
  } catch (error) {
    console.warn("Failed to refresh thread before destructive action", error);
  }
  const syncedThread = getThread(targetId);
  if (syncedThread && !isSyntheticThreadId(syncedThread.id, targetId)) {
    return syncedThread.id;
  }
  return "";
}

function getComment(thread, commentId) {
  return (thread.comments || []).find((item) => item.id === commentId) || null;
}

function normalizeActorId(value) {
  return String(value || "").trim().toLowerCase();
}

function isCommentAdmin(actorId = getCurrentCommentActor().id) {
  return ["admin", "anton", "ivan"].includes(normalizeActorId(actorId));
}

function hasThreadLikeFromCurrentActor(thread) {
  const currentActorId = normalizeActorId(getCurrentCommentActor().id);
  return Array.isArray(thread.likedBy) && thread.likedBy.some((actorId) => normalizeActorId(actorId) === currentActorId);
}

function hasCommentLikeFromCurrentActor(comment) {
  const currentActorId = normalizeActorId(getCurrentCommentActor().id);
  return Array.isArray(comment.likedBy) && comment.likedBy.some((actorId) => normalizeActorId(actorId) === currentActorId);
}

function getCommentLikeCount(comment) {
  if (Array.isArray(comment.likedBy) && comment.likedBy.length) {
    return comment.likedBy.length;
  }
  return Number(comment.likes) || 0;
}

function canManageComment(thread, comment) {
  const currentActorId = normalizeActorId(getCurrentCommentActor().id);
  if (isCommentAdmin(currentActorId)) {
    return true;
  }
  return normalizeActorId(comment.userId) === currentActorId;
}

function canDeleteThread(thread) {
  const currentActorId = normalizeActorId(getCurrentCommentActor().id);
  if (isCommentAdmin(currentActorId)) {
    return true;
  }
  const rootComment = thread.comments && thread.comments.length ? thread.comments[0] : null;
  return rootComment ? normalizeActorId(rootComment.userId) === currentActorId : false;
}

function canPauseThread(thread) {
  const currentActorId = normalizeActorId(getCurrentCommentActor().id);
  if (isCommentAdmin(currentActorId)) {
    return true;
  }
  const rootComment = thread.comments && thread.comments.length ? thread.comments[0] : null;
  return rootComment ? normalizeActorId(rootComment.userId) === currentActorId : false;
}

function formatThreadCommentsLabel(count) {
  const value = Math.max(Number(count) || 0, 0);
  const mod10 = value % 10;
  const mod100 = value % 100;
  if (mod10 === 1 && mod100 !== 11) {
    return "Показать " + value + " комментарий ветки";
  }
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
    return "Показать " + value + " комментария ветки";
  }
  return "Показать " + value + " комментариев ветки";
}

function formatHistoryStatus(item) {
  if (item.deleted) {
    return "Удалена " + formatThreadDate(item.deletedAt);
  }
  if (item.paused) {
    return "На паузе " + formatThreadDate(item.pausedAt);
  }
  if (item.resolved) {
    return "Решена " + formatThreadDate(item.resolvedAt);
  }
  return "";
}

function highlightActiveTarget() {
  document.querySelectorAll(".comment-target--active").forEach((node) => node.classList.remove("comment-target--active"));
  [commentOpenTargetId, commentHoveredTargetId].filter(Boolean).forEach((targetId) => {
    const target = document.querySelector(`[data-comment-target-id="${targetId}"]`);
    if (target) {
      target.classList.add("comment-target--active");
    }
  });
}

function setHoveredCommentTarget(targetId) {
  if (commentHoverClearTimer) {
    clearTimeout(commentHoverClearTimer);
    commentHoverClearTimer = null;
  }
  const nextValue = targetId || "";
  if (commentHoveredTargetId === nextValue) {
    return;
  }
  commentHoveredTargetId = nextValue;
  scheduleCommentAnchors();
}

function clearHoveredCommentTargetSoon(delayMs = 900) {
  if (commentHoverClearTimer) {
    clearTimeout(commentHoverClearTimer);
  }
  commentHoverClearTimer = window.setTimeout(() => {
    commentHoverClearTimer = null;
    if (!commentOpenTargetId) {
      setHoveredCommentTarget("");
    }
  }, delayMs);
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
  normalizeCommentTargetIds();
  const targets = getCommentableTargets();
  targets.forEach((target) => ensureTargetId(target));
  highlightActiveTarget();
  commentSelectionDraft = buildSelectionCommentDraft();
  const canvasRect = editorCanvas.getBoundingClientRect();
  const panelVisible = commentsPanel.classList.contains("is-open");
  const reserve = panelVisible ? 392 : 84;
  const html = [];

  targets.forEach((target) => {
    const targetId = target.dataset.commentTargetId;
    if (!targetId) {
      return;
    }
    const thread = getThread(targetId);
    if (!thread) {
      return;
    }
    const rect = target.getBoundingClientRect();
    if (!rect.width || !rect.height) {
      return;
    }
    const count = thread ? (thread.badgeCount || thread.comments.length || 0) : 0;
    const tooltip = count > 0 ? `Показать ${count} комментария` : "Начать обсуждение";
    const top = rect.top - canvasRect.top + editorCanvas.scrollTop;
    const left = Math.max(18, Math.min(rect.right - canvasRect.left + 12, editorCanvas.clientWidth - reserve));
    const isActive = commentOpenTargetId === targetId;
    const isHovered = commentHoveredTargetId === targetId;
    const isPaused = thread.status === "paused";
    if (!panelVisible && !isActive && !isHovered) {
      return;
    }
    html.push(
      `<div class="comment-anchor${isPaused ? " is-paused" : ""}" style="top:${top}px;left:${left}px;">` +
        `${isActive ? `<span class="comment-anchor__line" style="height:${Math.max(rect.height, 52)}px"></span>` : ""}` +
        `<button class="comment-anchor__button${count ? "" : " is-empty"}${isActive ? " is-active" : ""}${isPaused ? " is-paused" : ""}" data-comment-target="${targetId}" data-comment-tooltip="${escapeHtml(tooltip)}" type="button">` +
          `<span class="comment-anchor__icon">${commentIconSvg()}</span>` +
          `${count ? `<span class="comment-anchor__badge">${count}</span>` : ""}` +
        `</button>` +
      `</div>`
    );
  });

  if (commentSelectionDraft && commentSelectionDraft.rect) {
    const rect = commentSelectionDraft.rect;
    const top = rect.top - canvasRect.top + editorCanvas.scrollTop;
    const left = Math.max(18, Math.min(rect.right - canvasRect.left + 12, editorCanvas.clientWidth - reserve));
    html.push(
      `<div class="comment-anchor" style="top:${top}px;left:${left}px;">` +
        `<button class="comment-anchor__button is-empty is-create" data-comment-create="selection" data-comment-tooltip="Начать обсуждение" type="button">` +
          `<span class="comment-anchor__icon">${commentPlusSvg()}</span>` +
        `</button>` +
      `</div>`
    );
  }

  commentAnchorLayer.innerHTML = html.join("");
}

async function openDiscussionFromSelection() {
  await ensureCommentPage();
  const targetId = createTargetFromSelectionDraft();
  if (!targetId) {
    scheduleCommentAnchors();
    return;
  }

  commentSelectionDraft = null;
  scheduleCommentDocumentSave("Добавлено обсуждение", getCurrentCommentActor().id);
  await openThreadForTarget(targetId, true);
  requestAnimationFrame(() => {
    commentsComposerInput.focus();
  });
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
  const isRootComment = thread.comments[0] && thread.comments[0].id === comment.id;
  const canEdit = canManageComment(thread, comment);
  const canDelete = isRootComment ? canDeleteThread(thread) : canManageComment(thread, comment);
  const canOpenMenu = canEdit || canDelete;
  const isLiked = hasCommentLikeFromCurrentActor(comment);
  const likeCount = getCommentLikeCount(comment);
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
            <button class="comment-action${isLiked ? " is-active" : ""}" data-comment-action="like" data-comment-id="${comment.id}" type="button" aria-label="Нравится" data-comment-tooltip="${isLiked ? "Убрать лайк" : "Нравится"}">
              ${thumbsUpSvg()}
              ${likeCount ? `<span class="comment-action__count">${likeCount}</span>` : ""}
            </button>
            <button class="comment-action" data-comment-action="reply" data-comment-id="${comment.id}" type="button" aria-label="Ответить" data-comment-tooltip="Ответить">
              ${replySvg()}
            </button>
            <div class="comment-card__menu-wrap"${canOpenMenu ? "" : " hidden"}>
              <button class="comment-action" data-comment-action="menu" data-comment-id="${comment.id}" type="button" aria-label="Действия" data-comment-tooltip="Действия">
                ${menuSvg()}
              </button>
              <div class="comment-card__menu${menuOpen ? " is-open" : ""}">
                ${canEdit ? `<button class="comment-card__menu-item" data-comment-action="edit" data-comment-id="${comment.id}" type="button">Редактировать</button>` : ""}
                ${canDelete ? `<button class="comment-card__menu-item is-danger" data-comment-action="delete" data-comment-id="${comment.id}" type="button">Удалить</button>` : ""}
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
  if (commentsPauseButton) {
    commentsPauseButton.disabled = !isOpen;
  }

  if (!isOpen) {
    commentsPanelStatus.hidden = true;
    commentsPanelStatus.classList.remove("is-paused");
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
  commentsPanelStatus.hidden = !["resolved", "paused"].includes(thread.status);
  commentsPanelStatus.classList.toggle("is-paused", thread.status === "paused");
  commentsPanelStatus.textContent = thread.status === "resolved" ? "Решена" : (thread.status === "paused" ? "На паузе" : "");
  if (commentsPauseButton) {
    commentsPauseButton.dataset.commentTooltip = thread.status === "paused" ? "Продолжить обсуждение" : "Приостановить обсуждение";
    commentsPauseButton.classList.toggle("is-paused", thread.status === "paused");
    commentsPauseButton.classList.toggle("is-active", thread.status === "paused");
  }

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

  const canTogglePause = canPauseThread(thread);
  if (commentsPauseButton) {
    commentsPauseButton.disabled = !isOpen || !canTogglePause;
    commentsPauseButton.hidden = !canTogglePause;
  }
  if (commentsResolveButton) {
    commentsResolveButton.disabled = !isOpen || thread.status === "paused";
  }
  if (commentsComposerInput) {
    const paused = thread.status === "paused";
    commentsComposerInput.disabled = paused;
    commentsComposerInput.placeholder = paused ? "Обсуждение приостановлено" : "Новый комментарий";
  }
  if (commentsComposerSend) {
    commentsComposerSend.disabled = thread.status === "paused" || !commentsComposerInput.value.trim();
  }
}

async function openThreadForTarget(targetId, instant = false) {
  if (!targetId) {
    return;
  }
  commentOpenTargetId = targetId;
  commentHoveredTargetId = targetId;
  commentReplyTo = null;
  commentEditingId = null;
  commentMenuOpenId = null;
  commentLoadToken += 1;

  const token = commentLoadToken;
  let syncFailed = false;

  const applyThreadMode = (preferError = false) => {
    if (token !== commentLoadToken) {
      return;
    }
    const thread = getOrCreateThread(targetId);
    if (thread.demoState === "error") {
      commentPanelMode = "error";
    } else if (preferError && !thread.comments.length) {
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

  applyThreadMode(false);

  if (!commentPageId) {
    return;
  }

  try {
    await syncThreadsFromServer();
  } catch (error) {
    syncFailed = true;
    console.warn("Failed to sync comment threads", error);
  }

  if (instant) {
    applyThreadMode(syncFailed);
  } else {
    window.setTimeout(() => {
      applyThreadMode(syncFailed);
    }, 180);
  }
}

function closeCommentsPanel() {
  commentOpenTargetId = null;
  commentHoveredTargetId = "";
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
  const baseComment = focusComment || thread.comments[0] || thread.comments[thread.comments.length - 1];
  if (!baseComment) {
    return;
  }
  const target = document.querySelector(`[data-comment-target-id="${thread.targetId}"]`);
  const replies = (thread.comments || []).filter((item) => item.id !== baseComment.id);
  commentHistoryItems.unshift({
    id: `hist-runtime-${Date.now()}-${Math.random().toString(16).slice(2, 6)}`,
    userId: baseComment.userId,
    date: baseComment.date,
    statusText,
    preview: getTargetPreview(target).slice(0, 120),
    text: baseComment.text,
    likes: getCommentLikeCount(baseComment),
    thread: replies.map((item) => ({ userId: item.userId, date: item.date, text: item.text })),
    toggleLabel: formatThreadCommentsLabel(replies.length)
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
      body: JSON.stringify({ resolved: nextResolved, author: getCurrentCommentActor().id })
    });
    await syncThreadsFromServer(true);
    await createCommentVersion(
      nextResolved ? "Обсуждение отмечено как решенное" : "Обсждение возвращено в работу",
      getCurrentCommentActor().id
    );
  } else {
    thread.status = nextResolved ? "resolved" : "open";
    if (thread.status === "resolved") {
      addHistorySnapshot(thread, "Решена " + formatThreadDate(new Date().toISOString()));
    }
  }
  renderCommentsPanel();
  scheduleCommentAnchors();
}

async function togglePausedThread() {
  if (!commentOpenTargetId) {
    return;
  }
  const thread = getOrCreateThread(commentOpenTargetId);
  if (!canPauseThread(thread)) {
    return;
  }
  const nextPaused = thread.status !== "paused";
  if (commentPageId) {
    await commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/pause`, {
      method: "POST",
      body: JSON.stringify({ paused: nextPaused, author: getCurrentCommentActor().id })
    });
    await syncThreadsFromServer(true);
    await createCommentVersion(
      nextPaused ? "Обсуждение поставлено на паузу" : "Обсуждение возобновлено",
      getCurrentCommentActor().id
    );
  } else {
    thread.status = nextPaused ? "paused" : "open";
    if (thread.status === "paused") {
      addHistorySnapshot(thread, "На паузе " + formatThreadDate(new Date().toISOString()));
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
  if (thread.status === "paused") {
    updateComposerState();
    return;
  }
  const isNewDiscussion = !thread.comments.length;
  const versionLabel = isNewDiscussion
    ? "Добавлено обсуждение"
    : (commentReplyTo ? "Добавлен ответ в обсуждении" : "Добавлен комментарий в обсуждении");
  let text = raw;
  const targetElement = document.querySelector(`[data-comment-target-id="${commentOpenTargetId}"]`);
  const replyToMessageId = commentReplyTo || "";
  if (commentReplyTo) {
    const targetComment = getComment(thread, commentReplyTo);
    if (targetComment) {
      const replyUser = getCommentUser(targetComment.userId);
      if (!text.includes("@" + replyUser.handle)) {
        text = "@" + replyUser.handle + " " + text;
      }
    }
  }

  commentReplyTo = null;
  commentEditingId = null;
  commentMenuOpenId = null;
  commentsComposerInput.value = "";
  updateComposerState();
  const now = new Date();
  const dateLabel = now.toLocaleDateString("ru-RU") + " в " + now.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
  const optimisticCommentId = `comment-pending-${Date.now()}-${Math.random().toString(16).slice(2, 7)}`;
  const optimisticComment = createComment(
    optimisticCommentId,
    getCurrentCommentActor().id,
    dateLabel,
    text,
    {
      likedBy: [],
      likes: 0,
      replyTo: replyToMessageId || null,
      targetPreview: getTargetPreview(targetElement),
      targetType: inferTargetType(targetElement)
    }
  );
  thread.comments.push(optimisticComment);
  thread.badgeCount = Math.max(thread.badgeCount + 1, thread.comments.length);
  thread.demoState = "ready";
  thread.status = "open";

  if (commentPageId) {
    const request = isNewDiscussion
      ? commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments`, {
          method: "POST",
          body: JSON.stringify({
            author: getCurrentCommentActor().id,
            body: text,
            selectionLabel: getTargetPreview(targetElement),
            targetId: commentOpenTargetId,
            targetType: inferTargetType(targetElement),
            targetPreview: getTargetPreview(targetElement)
          })
        })
      : commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/replies`, {
          method: "POST",
          body: JSON.stringify({
            author: getCurrentCommentActor().id,
            body: text,
            replyToMessageId
          })
        });

    request.then(() => syncThreadsFromServer(true))
      .then(() => {
        commentPanelMode = getOrCreateThread(commentOpenTargetId).comments.length ? "list" : "empty";
        renderCommentsPanel();
        scheduleCommentAnchors();
      })
      .catch((error) => {
        thread.comments = thread.comments.filter((item) => item.id !== optimisticCommentId);
        thread.badgeCount = Math.max(thread.comments.length, 0);
        commentPanelMode = thread.comments.length ? "list" : "empty";
        renderCommentsPanel();
        scheduleCommentAnchors();
        console.warn("Failed to refresh thread after comment send", error);
      });
    createCommentVersion(versionLabel, getCurrentCommentActor().id).catch((error) => console.warn("Failed to create comment version", error));
  }

  commentPanelMode = thread.comments.length ? "list" : "empty";
  renderCommentsPanel();
  scheduleCommentAnchors();
  requestAnimationFrame(() => {
    commentsPanelScroll.scrollTop = commentsPanelScroll.scrollHeight;
    commentsComposerInput.focus();
  });
}

function getFilteredCommentHistoryItems() {
  const selectedPageId = commentHistorySelectedPageId || commentPageId || "";
  const selectedThreadId = commentHistorySelectedThreadId || "";
  return (commentHistoryItems || []).filter((item) => {
    if (selectedPageId && item.pageId !== selectedPageId) {
      return false;
    }
    if (selectedThreadId && item.id !== selectedThreadId) {
      return false;
    }
    return true;
  });
}

function renderHistoryModal() {
  if (!commentsHistoryModal.classList.contains("is-open")) {
    return;
  }

  renderHistoryFilters();

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

  const filteredItems = getFilteredCommentHistoryItems();
  if (!filteredItems.length) {
    const emptyMessage = commentHistorySelectedThreadId
      ? "Для выбранного обсуждения пока нет истории"
      : "История комментариев пока пуста";
    commentsHistoryBody.innerHTML = `<div class="comments-history-modal__error"><div class="comments-history-modal__error-inner"><div>${emptyMessage}</div></div></div>`;
    commentsHistoryFooter.innerHTML = "";
    return;
  }

  const itemsPerPage = 3;
  const totalPages = Math.max(1, Math.ceil(filteredItems.length / itemsPerPage));
  const page = Math.min(Math.max(commentHistoryPage, 1), totalPages);
  const start = (page - 1) * itemsPerPage;
  const pageItems = filteredItems.slice(start, start + itemsPerPage);

  commentsHistoryBody.innerHTML = pageItems.map((item) => {
    const user = getCommentUser(item.userId);
    const expanded = commentHistoryExpanded.has(item.id);
    const replies = item.thread || [];
    const hasReplies = replies.length > 0;
    const actions = item.likes ? `<div class="comments-history-item__actions"><span>${item.likes}</span><span>${thumbsUpSvg()}</span></div>` : "";
    const nested = expanded
      ? `<div class="comments-history-item__thread">${replies.map((entry) => {
          const nestedUser = getCommentUser(entry.userId);
          return `
            <div class="comments-history-item__nested${entry.deleted ? " is-deleted" : ""}">
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
    const attachment = item.thumb
      ? `<div class="comments-history-item__thumb"><div class="comments-history-item__thumb-image"></div><div class="comments-history-item__thumb-label">${escapeHtml(item.attachmentLabel || "Изображение")}</div></div>`
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
        ${attachment}
        <div class="comments-history-item__text">${formatCommentText(item.text || "")}</div>
        ${actions}
        ${hasReplies ? `<button class="comments-history-item__toggle" data-history-action="toggle-thread" data-history-id="${item.id}" type="button">${expanded ? "Скрыть ветку" : escapeHtml(item.toggleLabel || formatThreadCommentsLabel(replies.length))}</button>` : ""}
        ${nested}
      </article>
    `;
  }).join("");

  commentsHistoryFooter.innerHTML = collectHistoryItems(pageItems, page, totalPages);
}

async function openHistoryModal(mode = "list") {
  ensureHistorySeed();
  commentHistoryMode = mode;
  commentHistoryPage = 1;
  commentHistorySelectedPageId = commentPageId || commentHistorySelectedPageId || "";
  commentHistorySelectedThreadId = "";

  if (typeof loadPagesCatalog === "function") {
    try {
      await loadPagesCatalog(true);
    } catch (error) {
      console.warn("Failed to refresh pages catalog for history", error);
    }
  }

  if (mode === "list" && (commentHistorySelectedPageId || commentPageId)) {
    const historyPageId = commentHistorySelectedPageId || commentPageId;
    try {
      await loadHistoryThreadOptions(historyPageId, true);
      await loadCommentHistoryFromServer(true, historyPageId);
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
      setCurrentCommentActor(commentsActorSelect.value || "ivan");
    });
  }

  if (accountTrigger && accountSwitcher) {
    accountTrigger.addEventListener("click", (event) => {
      event.stopPropagation();
      accountSwitcher.classList.toggle("is-open");
    });
  }

  if (accountMenu) {
    accountMenu.addEventListener("click", (event) => {
      const userButton = event.target.closest("[data-account-user]");
      if (userButton) {
        setCurrentCommentActor(userButton.dataset.accountUser || "ivan");
        accountSwitcher.classList.remove("is-open");
        return;
      }
      const actionButton = event.target.closest("[data-account-action='logout']");
      if (actionButton) {
        window.localStorage.removeItem(commentActorStorageKey);
        setCurrentCommentActor("viewer", false);
        accountSwitcher.classList.remove("is-open");
      }
    });
  }

  if (docHeaderSubtitle) {
    docHeaderSubtitle.addEventListener("focus", () => {
      if (docHeaderSubtitle.classList.contains("is-placeholder")) {
        docHeaderSubtitle.textContent = "";
        docHeaderSubtitle.classList.remove("is-placeholder");
      }
    });
    docHeaderSubtitle.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
      }
    });
    docHeaderSubtitle.addEventListener("input", () => {
      const text = docHeaderSubtitle.textContent.replace(/\u200B/g, "").trim();
      docHeaderSubtitle.classList.toggle("is-placeholder", !text);
      scheduleCommentDocumentSave("Изменено описание", getCurrentCommentActor().id);
    });
    docHeaderSubtitle.addEventListener("blur", () => {
      const text = docHeaderSubtitle.textContent.replace(/\u200B/g, "").trim();
      if (!text) {
        syncDocumentSubtitlePlaceholder(true);
      }
    });
  }

  if (commentObserver) {
    commentObserver.disconnect();
  }
  commentObserver = new MutationObserver((mutations) => {
    if (commentOpenTargetId) {
      const thread = getThread(commentOpenTargetId);
      if (thread) {
        const target = document.querySelector(`[data-comment-target-id="${commentOpenTargetId}"]`);
        thread.preview = getTargetPreview(target);
      }
    }
    const mutationLabel = classifyMutationLabel(mutations);
    if (mutationLabel) {
      scheduleCommentDocumentSave(mutationLabel, getCurrentCommentActor().id);
    }
    scheduleCommentAnchors();
    scheduleOrphanThreadCleanup();
    renderCommentsPanel();
  });
  commentObserver.observe(bodyEditor, { childList: true, subtree: true, characterData: true });

  commentAnchorLayer.addEventListener("click", (event) => {
    const createButton = event.target.closest("[data-comment-create='selection']");
    if (createButton) {
      openDiscussionFromSelection().catch((error) => console.warn("Failed to create discussion from selection", error));
      return;
    }
    const button = event.target.closest("[data-comment-target]");
    if (!button) {
      return;
    }
    openThreadForTarget(button.dataset.commentTarget, true);
  });

  commentAnchorLayer.addEventListener("mouseover", (event) => {
    const button = event.target && event.target.closest
      ? event.target.closest("[data-comment-target]")
      : null;
    if (button) {
      setHoveredCommentTarget(button.dataset.commentTarget || "");
      return;
    }
    const createButton = event.target && event.target.closest
      ? event.target.closest("[data-comment-create='selection']")
      : null;
    if (createButton && commentSelectionDraft) {
      if (commentHoverClearTimer) {
        clearTimeout(commentHoverClearTimer);
        commentHoverClearTimer = null;
      }
    }
  });

  commentAnchorLayer.addEventListener("mouseleave", () => {
    clearHoveredCommentTargetSoon();
  });

  bodyEditor.addEventListener("mouseover", (event) => {
    const target = event.target && event.target.closest
      ? event.target.closest("[data-comment-target-id]")
      : null;
    if (target) {
      setHoveredCommentTarget(target.dataset.commentTargetId || "");
      return;
    }
    clearHoveredCommentTargetSoon();
  });

  bodyEditor.addEventListener("mouseleave", () => {
    clearHoveredCommentTargetSoon();
  });

  const handleCommentLinkClick = (event) => {
    const link = event.target && event.target.closest ? event.target.closest("a[data-comment-link]") : null;
    if (!link) {
      return false;
    }
    event.preventDefault();
    event.stopPropagation();
    if (link.dataset.commentLink === "external") {
      window.open(link.href, "_blank", "noopener,noreferrer");
      return true;
    }
    navigateToLink(link);
    return true;
  };

  commentsCloseButton.addEventListener("click", closeCommentsPanel);
  commentsResolveButton.addEventListener("click", () => {
    toggleResolvedThread().catch((error) => console.warn("Failed to toggle resolved state", error));
  });
  if (commentsPauseButton) {
    commentsPauseButton.addEventListener("click", () => {
      togglePausedThread().catch((error) => console.warn("Failed to toggle paused state", error));
    });
  }
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
    if (handleCommentLinkClick(event)) {
      return;
    }
    const actionTarget = event.target.closest("[data-comment-action]");
    if (!actionTarget || !commentOpenTargetId) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    const thread = getOrCreateThread(commentOpenTargetId);
    const commentId = actionTarget.dataset.commentId;
    const comment = getComment(thread, commentId);
    const action = actionTarget.dataset.commentAction;

    if (action === "like" && comment) {
      const actorId = normalizeActorId(getCurrentCommentActor().id);
      comment.likedBy = Array.isArray(comment.likedBy) ? [...comment.likedBy] : [];
      const existingIndex = comment.likedBy.findIndex((item) => normalizeActorId(item) === actorId);
      if (existingIndex === -1) {
        comment.likedBy.push(actorId);
      } else {
        comment.likedBy.splice(existingIndex, 1);
      }
      comment.likes = comment.likedBy.length;
      renderCommentsPanel();
      if (commentPageId) {
        commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/like`, {
          method: "POST",
          body: JSON.stringify({ author: getCurrentCommentActor().id, messageId: comment.id })
        }).then(() => syncThreadsFromServer())
        .then(() => {
          renderCommentsPanel();
          scheduleCommentAnchors();
          createCommentVersion("Изменена реакция в обсуждении", getCurrentCommentActor().id).catch((error) => console.warn("Failed to create like version", error));
        }).catch((error) => {
          const rollbackIndex = comment.likedBy.findIndex((item) => normalizeActorId(item) === actorId);
          if (existingIndex === -1) {
            if (rollbackIndex !== -1) {
              comment.likedBy.splice(rollbackIndex, 1);
            }
          } else if (rollbackIndex === -1) {
            comment.likedBy.push(actorId);
          }
          comment.likes = comment.likedBy.length;
          renderCommentsPanel();
          scheduleCommentAnchors();
          console.warn("Failed to toggle like", error);
        });
      } else {
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
      const targetId = commentOpenTargetId;
      const previousThread = cloneThreadState(thread);
      commentMenuOpenId = null;
      commentEditingId = null;
      commentReplyTo = null;

      if (isRootMessage) {
        commentThreads.delete(targetId);
        closeCommentsPanel();
      } else {
        thread.comments = thread.comments.filter((item) => item.id !== comment.id);
        thread.badgeCount = Math.max(thread.comments.length, 0);
        commentPanelMode = thread.comments.length ? "list" : "empty";
        renderCommentsPanel();
      }
      scheduleCommentAnchors();
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
        : Promise.resolve();
      request.then(() => {
        if (commentPageId) {
          syncThreadsFromServer(true).then(() => {
            if (commentOpenTargetId === targetId) {
              const nextThread = getThread(targetId);
              commentPanelMode = nextThread && nextThread.comments.length ? "list" : "empty";
              renderCommentsPanel();
            }
            scheduleCommentAnchors();
          }).catch((error) => console.warn("Failed to sync threads after delete", error));
          createCommentVersion(
            isRootMessage ? "Удалено обсуждение" : "Удален комментарий",
            getCurrentCommentActor().id
          ).catch((error) => console.warn("Failed to create delete version", error));
        }
      }).catch((error) => {
        commentThreads.set(targetId, previousThread);
        commentOpenTargetId = targetId;
        commentPanelMode = previousThread.comments.length ? "list" : "empty";
        renderCommentsPanel();
        scheduleCommentAnchors();
        console.warn("Failed to delete comment", error);
      });
      return;
    }
    if (action === "save-edit" && comment) {
      const input = commentsPanelList.querySelector(`[data-comment-edit-input="${comment.id}"]`);
      const nextValue = input ? input.value.trim() : "";
      if (!nextValue) {
        return;
      }
      const previousText = comment.text;
      comment.text = nextValue;
      commentEditingId = null;
      commentMenuOpenId = null;
      renderCommentsPanel();
      const request = commentPageId
        ? commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/messages/${encodeURIComponent(comment.id)}`, {
            method: "PUT",
            body: JSON.stringify({ body: nextValue, author: getCurrentCommentActor().id })
          })
        : Promise.resolve();
      request.then(() => {
        if (commentPageId) {
          syncThreadsFromServer(true).then(() => {
            renderCommentsPanel();
            scheduleCommentAnchors();
          }).catch((error) => console.warn("Failed to sync threads after edit", error));
          createCommentVersion("Изменен комментарий", getCurrentCommentActor().id)
            .catch((error) => console.warn("Failed to create edit version", error));
        }
      }).catch((error) => {
        comment.text = previousText;
        commentEditingId = comment.id;
        renderCommentsPanel();
        console.warn("Failed to save comment edit", error);
      });
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
    if (handleCommentLinkClick(event)) {
      return;
    }
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
      openHistoryModal("list").catch((error) => console.warn("Failed to reload history", error));
    }
  });

  if (commentsHistoryPageSelect) {
    commentsHistoryPageSelect.addEventListener("change", async () => {
      commentHistorySelectedPageId = commentsHistoryPageSelect.value || commentPageId || "";
      commentHistorySelectedThreadId = "";
      commentHistoryPage = 1;
      commentHistoryExpanded.clear();
      commentHistoryMode = "list";
      try {
        await loadHistoryThreadOptions(commentHistorySelectedPageId, true);
        await loadCommentHistoryFromServer(true, commentHistorySelectedPageId);
      } catch (error) {
        console.warn("Failed to switch history page", error);
        commentHistoryMode = "error";
      }
      renderHistoryModal();
    });
  }

  if (commentsHistoryThreadSelect) {
    commentsHistoryThreadSelect.addEventListener("change", () => {
      commentHistorySelectedThreadId = commentsHistoryThreadSelect.value || "";
      commentHistoryPage = 1;
      commentHistoryExpanded.clear();
      renderHistoryModal();
    });
  }

  document.addEventListener("click", (event) => {
    if (!commentsTopbar.contains(event.target)) {
      commentsTopDropdown.classList.remove("is-open");
      commentsAccessPopup.classList.remove("is-open");
    }
    if (accountSwitcher && !accountSwitcher.contains(event.target)) {
      accountSwitcher.classList.remove("is-open");
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
  bodyEditor.addEventListener("input", () => scheduleCommentDocumentSave("Изменение текста", getCurrentCommentActor().id));
  titleEditor.addEventListener("input", () => scheduleCommentDocumentSave("Изменен заголовок", getCurrentCommentActor().id));
  titleEditor.addEventListener("keyup", () => scheduleCommentDocumentSave("Изменен заголовок", getCurrentCommentActor().id));

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
          await createCommentVersion("Изменен доступ к комментариям", getCurrentCommentActor().id);
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
