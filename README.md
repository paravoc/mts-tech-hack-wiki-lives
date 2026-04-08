# WikiLive

WikiLive — прототип живой вики-системы для MWS Tables. Пользователь создает страницы, вставляет в текст ссылки вида `{{tableId:recordId:fieldName}}`, а сервер рендерит эти вставки в актуальные значения из таблиц.

## Что уже реализовано

- backend на `C++23`
- HTTP API на `uWebSockets`
- CRUD для вики-страниц
- рендер текста с wiki-вставками
- единый JSON-формат ответов и ошибок
- базовая интеграция с MWS Tables через `WinHTTP`
- хранение страниц в `WikiPages` через MWS Tables
- модульный AI-слой под `OpenRouter` и `Ollama`
- модульные тесты через `CTest`

## Текущие endpoint'ы

- `GET /health`
- `GET /api/pages`
- `GET /api/pages/{pageId}`
- `POST /api/pages`
- `PUT /api/pages/{pageId}`
- `DELETE /api/pages/{pageId}`
- `POST /api/render`

## Формат страницы

```json
{
  "pageId": "page-1",
  "title": "Статус проекта",
  "content": "Текст страницы",
  "createdAt": "2026-04-08T12:00:00Z",
  "updatedAt": "2026-04-08T12:00:00Z",
  "renderedHtml": "<span>...</span>"
}
```

## Пример вставки

```text
Статус проекта: {{dstPqo6u9dqgb6Ls2t:rec123456:Статус}}
```

## Конфигурация

Настройки задаются в `.env`.

Пример:

```env
MWS_TOKEN=your_token
MWS_TABLE_ID=dst...
MWS_VIEW_ID=viw...

WIKI_PAGES_TABLE_ID=dst...
WIKI_PAGES_VIEW_ID=viw...

HTTP_PORT=3000
LOG_LEVEL=info
CACHE_TTL_SECONDS=60
REQUEST_TIMEOUT_MS=10000
RETRY_ATTEMPTS=3
RETRY_BASE_DELAY_MS=1000
WS_HEARTBEAT_SECONDS=20
ENABLE_WEBSOCKET=true
ENABLE_AI=false
AI_PROVIDER=none
AI_BASE_URL=
AI_API_KEY=
AI_MODEL=
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.2
```

## Сборка

Проект собирается через preset `windows-debug`.

```powershell
cmake --preset windows-debug
cmake --build --preset windows-debug
```

Готовый бинарник появляется по пути:

```text
C:\Users\smidr\AppData\Local\WikiLive\build\windows-vs-debug\Debug\wikilive_backend.exe
```

## Запуск

```powershell
C:\Users\smidr\AppData\Local\WikiLive\build\windows-vs-debug\Debug\wikilive_backend.exe
```

После запуска сервер по умолчанию слушает `http://127.0.0.1:3000`.

Проверка:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/health
```

## Тесты

Сборка тестов выполняется вместе с проектом. Запуск:

```powershell
ctest --test-dir "$env:LOCALAPPDATA\WikiLive\build\windows-vs-debug" -C Debug --output-on-failure
```

Покрыты базовые сценарии:

- парсинг wiki-вставок
- работа кэша
- CRUD и сортировка страниц
- работа router-слоя

## Структура проекта

```text
wikilive/
├── CMakeLists.txt
├── CMakePresets.json
├── README.md
├── .env.example
├── config/
├── src/
│   ├── api/
│   ├── ai/
│   ├── core/
│   ├── models/
│   ├── server/
│   ├── services/
│   ├── storage/
│   ├── utils/
│   └── wiki/
└── tests/
```

## Что дальше

1. Добавить первые AI endpoint'ы поверх уже готового модульного `src/ai`.
2. Подключить фронтенд к `pages`, `render` и `ws`.
3. Вынести кэш рендера и MWS-данных в отдельный слой.
4. Расширить live-render для более сложных типов полей.
5. Добавить polling или event-механику для внешних изменений в MWS.
