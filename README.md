# WikiLive

WikiLive — прототип живой вики-системы для MWS Tables. Пользователь создает страницы, вставляет в текст ссылки вида `{{tableId:recordId:fieldName}}`, а сервер рендерит эти вставки в актуальные значения из таблиц.

## Что уже реализовано

- backend на `C++23`
- HTTP API на `uWebSockets`
- web frontend на `Streamlit`
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
- `POST /api/ai/suggest-insert`
- `GET /ws`

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
C:\Users\smidr\OneDrive\Desktop\mts\out\build\x64-Debug\wikilive_backend.exe
```

## Запуск

```powershell
C:\Users\smidr\OneDrive\Desktop\mts\out\build\x64-Debug\wikilive_backend.exe
```

После запуска сервер по умолчанию слушает `http://127.0.0.1:3000`.

Проверка:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/health
```

## Frontend

Зависимости frontend находятся в `frontend/requirements.txt`.

Установка:

```powershell
C:\Users\smidr\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r frontend\requirements.txt
```

Запуск:

```powershell
C:\Users\smidr\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run frontend\app.py
```

По умолчанию frontend ожидает backend на `http://127.0.0.1:3000`.

Если нужно изменить адрес backend:

```powershell
$env:WIKILIVE_BACKEND_URL="http://127.0.0.1:3000"
C:\Users\smidr\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run frontend\app.py
```

Что уже умеет web UI:

- список страниц в sidebar
- создание, обновление и удаление страницы
- живой предпросмотр через `/api/render`
- загрузка существующей страницы из `WikiPages`
- AI-кнопка для `suggest-insert`
- архитектура, готовая к desktop-обертке

## Docker (одна команда)

Важно: текущий backend использует WinHTTP, поэтому контейнер запускается в **Windows containers**.
Перед запуском убедитесь, что бинарник backend собран локально и лежит в `out/build/x64-Debug/wikilive_backend.exe`.

Одна команда:

```bash
docker compose -f docker-compose.windows.yml up --build
```

После запуска:
- Backend: http://127.0.0.1:3000
- Frontend: http://127.0.0.1:8501

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
├── frontend/
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

1. Добавить во frontend подписку на `/ws` и fallback на polling.
2. Сделать cursor-aware вставку AI-кандидатов, а не только вставку в конец текста.
3. Вынести кэш рендера и MWS-данных в отдельный слой.
4. Расширить live-render для более сложных типов полей.
5. Добавить дополнительные AI-сценарии: `analyze` и `generate-page`.
