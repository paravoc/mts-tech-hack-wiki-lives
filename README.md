# WikiLive

![WikiLive cover](docs/images/wikilive-banner.svg)

**WikiLive** - платформа для совместной работы с документами и внутренними знаниями в реальном времени, разработанная в рамках MTS Tech Hack. Проект сочетает производительный backend на C++ и легкий интерфейс на Streamlit, чтобы редактирование, обсуждение, контроль версий и AI-помощь работали быстро и в одном пространстве.

Основной сценарий проекта - живая командная работа со страницами: создание и редактирование контента, комментарии по месту, просмотр истории изменений, управление доступом, встраивание медиа-блоков из MWS и использование AI-инструментов прямо внутри рабочего процесса.

## Возможности

- совместная wiki-среда для проектов и страниц знаний
- комментарии с ответами, лайками, редактированием, паузой и завершением обсуждений
- история изменений и восстановление предыдущих версий страниц
- разграничение прав доступа на уровне проекта, страницы, пользователей и групп
- AI-подсказки для улучшения текста и вставки контента
- интеграция с MWS для загрузки и встраивания медиа-блоков
- архитектура, готовая к live-обновлениям через WebSocket

## Интерфейс

<p align="center">
  <img src="docs/images/wikilive-shot-01.png" alt="WikiLive editor" width="31%">
  <img src="docs/images/wikilive-shot-02.png" alt="WikiLive comments" width="31%">
  <img src="docs/images/wikilive-shot-03.png" alt="WikiLive time machine" width="31%">
</p>

## Демо

- Витрина проекта в `docs/`, готовая для GitHub Pages: [docs/index.html](docs/index.html)
- Демо-видео: [docs/media/wikilive-demo.mp4](docs/media/wikilive-demo.mp4)

## Архитектура

![WikiLive architecture](docs/images/wikilive-architecture.svg)

Основные слои проекта:

- `frontend/` - приложение на Streamlit и UI-модули
- `src/server/` - HTTP-маршруты и API
- `src/core/` - инициализация приложения и сборка зависимостей
- `src/services/` - доменные сервисы, AI-интеграция и MWS-интеграция
- `src/storage/` - локальное хранение пользователей, страниц, проектов и состояния коллаборации
- `src/wiki/` - wiki-логика и связанные модели

## Технологии

- Backend: `C++23`
- HTTP-слой: `uWebSockets`
- Frontend: `Streamlit`
- Обмен данными: `nlohmann/json`
- Внешние интеграции: `libcurl`
- Локальный запуск: `Docker Compose`

## Быстрый старт

```bash
docker compose up --build
```

После запуска доступны:

- Frontend: `http://localhost:8501`
- Проверка backend: `http://localhost:3000/health`

## Локальная разработка

Backend:

```bash
cmake -S . -B build
cmake --build build
```

Frontend:

```bash
cd frontend
streamlit run app.py
```

## Дополнительно

В каталоге [`docs/`](docs/) также лежат материалы по планированию и трекингу, которые использовались в ходе хакатона.
