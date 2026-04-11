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
  { id: "ivan", name: "Иван Иванов", handle: "ivan", short: "И", color: "#59c4ff", nick: "#Tabs" },
  { id: "sergei", name: "Сергей Иванов", handle: "sergei", short: "С", color: "#7b68ee", nick: "#Tabs" },
  { id: "anton", name: "Антон Серганов", handle: "anton", short: "А", color: "#ffc83d", nick: "#Tabs" },
  { id: "anton-clean", name: "Антон Андреевич Чистяков", handle: "achistyakov", short: "И", color: "#39c785", nick: "#Tabs" },
  { id: "anna", name: "Анна Алексеевна Ивлева", handle: "anna", short: "И", color: "#4f83ff", nick: "#Tabs" },
  { id: "artem", name: "Артем Геннадьевич Михеенко", handle: "artem", short: "И", color: "#56c8ff", nick: "#Tabs" },
  { id: "artem2", name: "Артем Сергеевич Коховец", handle: "artem.ko", short: "И", color: "#ffcb3f", nick: "#Tabs" },
  { id: "maxim", name: "Максим Алексеевич Карпов", handle: "max", short: "И", color: "#5f79ff", nick: "#Tabs" },
  { id: "artem3", name: "Артем Эдуардович Горбачев", handle: "gorbachev", short: "И", color: "#7a63f1", nick: "#Tabs" }
];
const commentUserMap = new Map(commentUsers.map((user) => [user.id, user]));

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

function commentIconSvg() {
  return '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 3.5h11v7h-7l-2.8 2V10.5H2.5z"></path><path d="M5.2 6.2h5.6M5.2 8.2h3.4"></path></svg>';
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
    nick: "#WikiLive"
  };
}

function createComment(id, userId, date, text, extra = {}) {
  return { id, userId, date, text, likes: extra.likes || 0, replyTo: extra.replyTo || null, editable: extra.editable !== false };
}

function createThread(id, targetId, options = {}) {
  return { id, targetId, badgeCount: options.badgeCount || 0, status: options.status || "open", demoState: options.demoState || "ready", preview: options.preview || "", comments: options.comments || [], iconOnly: Boolean(options.iconOnly) };
}

async function commentApiRequest(path, options = {}) {
  const response = await fetch(commentApiBase + path, {
    headers: {
      "Content-Type": "application/json"
    },
    ...options
  });

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
      body: "Думаю этот абзац стоит переписать, слишком сложно, тут же весь смысл в простоте донесения мысли.",
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
      body: JSON.stringify({ author: "sergei", body: "Согласен. Нужна более спокойная подача." })
    });
    await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments/${encodeURIComponent(mainThread.threadId)}/replies`, {
      method: "POST",
      body: JSON.stringify({ author: "anton", body: "@sergei да, давай упростим формулировку." })
    });
  }

  if (targets[2]) {
    const thirdTarget = targets[2];
    await commentApiRequest(`/api/pages/${encodeURIComponent(pageId)}/comments`, {
      method: "POST",
      body: JSON.stringify({
        author: "ivan",
        body: "Этот блок уже обсудили, можно оставить как есть.",
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
  const comments = (item.messages || []).map((message) => createComment(
    message.messageId,
    message.author || "viewer",
    formatThreadDate(message.updatedAt || message.createdAt),
    message.body || "",
    {
      likes: 0,
      replyTo: message.replyToMessageId || null
    }
  ));
  if (comments.length) {
    comments[comments.length - 1].likes = item.likeCount || 0;
  }
  return createThread(item.threadId, item.targetId, {
    badgeCount: item.messages ? item.messages.length : 0,
    status: item.resolved ? "resolved" : "open",
    preview: item.targetPreview || item.selectionLabel || "",
    comments,
    iconOnly: !(item.messages || []).length
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
    nextThreads.set(item.targetId, mapThreadFromApi(item));
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
    await syncThreadsFromServer();
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

function seedThreads(targets) {
  if (commentInitDone || !targets.length) {
    return;
  }
  if (targets[0]) {
    const id = ensureTargetId(targets[0]);
    commentThreads.set(id, createThread("thread-main", id, {
      badgeCount: 22,
      preview: getTargetPreview(targets[0]),
      comments: [
        createComment("comment-1", "ivan", "27.10.25 в 18:03", "Думаю этот параграф стоит переписать, слишком сложно, тут же весь смысл в простоте донесения мысли. Читатель не поймет, если мы будет говорить как Достоевский, нужно как Фейс"),
        createComment("comment-2", "sergei", "27.10.25 в 18:03", "Мое предложение вообще ничего не делать. Потому что лень."),
        createComment("comment-3", "ivan", "27.10.25 в 18:03", "@sergei уволен!", { likes: 4 })
      ]
    }));
  }
  if (targets[1]) {
    const id = ensureTargetId(targets[1]);
    commentThreads.set(id, createThread("thread-empty", id, {
      preview: getTargetPreview(targets[1]),
      comments: [],
      iconOnly: true,
      demoState: "error"
    }));
  }
  if (targets[2]) {
    const id = ensureTargetId(targets[2]);
    commentThreads.set(id, createThread("thread-resolved", id, {
      badgeCount: 1,
      preview: getTargetPreview(targets[2]),
      status: "resolved",
      comments: [
        createComment("comment-4", "ivan", "27.10.25 в 18:03", "Думаю этот параграф стоит переписать, слишком сложно, тут же весь смысл в простоте донесения мысли. Читатель не поймет, если мы будет говорить как Достоевский, нужно как Фейс", { likes: 4 })
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
      preview: getTargetPreview(document.querySelector(`[data-comment-target-id="${targetId}"]`))
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
  commentMentionCandidates = commentUsers.filter((user) => !query || `${user.name} ${user.handle}`.toLowerCase().includes(query)).slice(0, 6);
  if (!commentMentionCandidates.length) {
    commentsMentionDropdown.classList.remove("is-open");
    commentsMentionDropdown.innerHTML = "";
    return;
  }
  commentMentionIndex = Math.min(commentMentionIndex, Math.max(commentMentionCandidates.length - 1, 0));
  commentsMentionDropdown.innerHTML = commentMentionCandidates.map((user, index) => {
    return `<button class="comments-mentions__item${index === commentMentionIndex ? " is-active" : ""}" data-mention-user="${user.id}" type="button"><span class="comment-card__avatar" style="background:${user.color};width:30px;height:30px;font-size:16px;">${user.short}</span><span><span class="comments-mentions__name">${escapeHtml(user.name)}</span><span class="comments-mentions__nick">@${escapeHtml(user.handle)}</span></span></button>`;
  }).join("") + '<div class="comments-mentions__more">Дополнительно</div>';
  commentsMentionDropdown.classList.add("is-open");
}

function applyMention(userId) {
  const user = getCommentUser(userId);
  commentsComposerInput.value = commentsComposerInput.value.replace(/@([a-zA-Zа-яА-Я0-9._-]*)$/, `@${user.handle} `);
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
  return `
    <article class="comment-card${isReplyTarget ? " is-focused" : ""}${menuOpen ? " is-menu-open" : ""}${isEditing ? " is-editing" : ""}" data-comment-id="${comment.id}">
      <span class="comment-card__avatar" style="background:${user.color}">${user.short}</span>
      <div class="comment-card__body">
        <div class="comment-card__top">
          <div>
            <div class="comment-card__name">${escapeHtml(user.name)}</div>
            <div class="comment-card__date">${escapeHtml(comment.date)}</div>
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
  if (commentPageId) {
    try {
      await syncThreadsFromServer();
    } catch (error) {
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
          author: "anton",
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
          author: "anton",
          body: text,
          replyToMessageId: commentReplyTo || ""
        })
      });
    }
    await syncThreadsFromServer();
  } else {
    const now = new Date();
    const dateLabel = now.toLocaleDateString("ru-RU") + " в " + now.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
    thread.comments.push(createComment(`comment-${Date.now()}`, "anton", dateLabel, text));
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
  const totalPages = 10;
  const page = Math.min(Math.max(commentHistoryPage, 1), totalPages);
  const start = (page - 1) * itemsPerPage;
  const pageItems = commentHistoryItems.slice(start, start + itemsPerPage);

  commentsHistoryBody.innerHTML = pageItems.map((item) => {
    const user = getCommentUser(item.userId);
    const expanded = commentHistoryExpanded.has(item.id);
    const nested = expanded
      ? `<div class="comments-history-item__thread">${(item.thread || []).map((entry) => {
          const nestedUser = getCommentUser(entry.userId);
          return `
            <div class="comments-history-item__nested">
              <div class="comments-history-item__meta">
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
        <div class="comments-history-item__meta">
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
        ${(item.thread || []).length ? `<button class="comments-history-item__toggle" data-history-action="toggle-thread" data-history-id="${item.id}" type="button">${expanded ? "Скрыть ветку" : escapeHtml(item.toggleLabel || "Показать ветку")}</button>` : ""}
        ${nested}
      </article>
    `;
  }).join("");

  const pages = [];
  for (let pageNumber = 1; pageNumber <= Math.min(totalPages, 3); pageNumber += 1) {
    pages.push(`<button class="comments-history-modal__page${pageNumber === page ? " is-active" : ""}" data-history-action="page" data-history-page="${pageNumber}" type="button">${pageNumber}</button>`);
  }
  pages.push('<span class="comments-history-modal__ellipsis">…</span>');
  pages.push(`<button class="comments-history-modal__page${page === totalPages ? " is-active" : ""}" data-history-action="page" data-history-page="${totalPages}" type="button">${totalPages}</button>`);
  pages.push(`<button class="comments-history-modal__next" data-history-action="next" type="button" aria-label="Следующая страница">›</button>`);
  commentsHistoryFooter.innerHTML = pages.join("");
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
  renderCommentsPanel();
  scheduleCommentAnchors();
  ensureCommentPage();

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
          body: JSON.stringify({ author: "anton" })
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
                  body: JSON.stringify({ author: "anton" })
                })
              : commentApiRequest(`/api/pages/${encodeURIComponent(commentPageId)}/comments/${encodeURIComponent(thread.id)}/messages/${encodeURIComponent(comment.id)}`, {
                  method: "DELETE",
                  body: JSON.stringify({ author: "anton" })
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
  commentSyncTimer = window.setInterval(() => {
    if (!commentPageId || !commentsPanel.classList.contains("is-open")) {
      return;
    }
    syncThreadsFromServer().then(() => {
      renderCommentsPanel();
      scheduleCommentAnchors();
    }).catch(() => {});
  }, 6000);
}

window.initializeCommentsSystem = initializeCommentsSystem;
