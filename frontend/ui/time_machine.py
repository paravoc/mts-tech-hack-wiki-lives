from __future__ import annotations

from pathlib import Path
from textwrap import dedent


def time_machine_styles() -> str:
    return dedent(
        """
        :root {
          --tm-accent: #8b7cff;
          --tm-accent-strong: #7866ff;
          --tm-border: #dde3ee;
          --tm-surface: rgba(248, 250, 255, 0.98);
          --tm-text: #2a3140;
          --tm-muted: #8f98ab;
          --tm-shadow: 0 22px 40px rgba(31, 36, 48, 0.16);
        }

        .time-machine-top-trigger {
          position: fixed;
          top: 18px;
          right: 192px;
          z-index: 36;
          appearance: none;
          border: 0;
          background: transparent;
          color: var(--tm-accent);
          font-size: 13px;
          font-weight: 600;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 2px;
        }

        .time-machine-top-trigger svg,
        .time-machine-panel__info svg {
          width: 14px;
          height: 14px;
          display: block;
        }

        .time-machine-panel {
          position: fixed;
          top: 74px;
          right: 20px;
          bottom: 18px;
          width: 332px;
          border-radius: 18px;
          border: 1px solid var(--tm-border);
          background: var(--tm-surface);
          box-shadow: var(--tm-shadow);
          backdrop-filter: blur(12px);
          z-index: 35;
          display: flex;
          flex-direction: column;
          opacity: 0;
          visibility: hidden;
          transform: translateX(16px);
          transition: opacity .2s ease, transform .2s ease, visibility .2s ease;
          overflow: hidden;
        }

        .time-machine-panel.is-open {
          opacity: 1;
          visibility: visible;
          transform: translateX(0);
        }

        .time-machine-panel__header {
          padding: 18px 16px 14px;
          border-bottom: 1px solid #e8ebf2;
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 10px;
        }

        .time-machine-panel__title {
          font-size: 15px;
          font-weight: 700;
          color: var(--tm-text);
        }

        .time-machine-panel__subtitle {
          margin-top: 6px;
          font-size: 13px;
          color: var(--tm-muted);
        }

        .time-machine-panel__close {
          appearance: none;
          width: 24px;
          height: 24px;
          border: 0;
          border-radius: 999px;
          background: transparent;
          color: #b0b8c8;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          line-height: 1;
        }

        .time-machine-panel__close:hover {
          background: #f3f5f9;
          color: var(--tm-accent-strong);
        }

        .time-machine-panel__body {
          position: relative;
          flex: 1;
          min-height: 0;
          overflow: hidden;
          background: rgba(249, 250, 253, 0.72);
        }

        .time-machine-panel__scroll {
          height: 100%;
          overflow: auto;
          padding: 10px 12px 14px;
          scrollbar-width: thin;
          scrollbar-color: rgba(139, 124, 255, 0.35) transparent;
        }

        .time-machine-panel__scroll::-webkit-scrollbar {
          width: 8px;
        }

        .time-machine-panel__scroll::-webkit-scrollbar-thumb {
          border-radius: 999px;
          background: rgba(139, 124, 255, 0.24);
        }

        .time-machine-panel__state {
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: var(--tm-muted);
          font-size: 14px;
          padding: 0 24px;
        }

        .time-machine-panel__spinner {
          width: 40px;
          height: 40px;
          border-radius: 999px;
          border: 4px solid rgba(139, 124, 255, 0.14);
          border-top-color: var(--tm-accent-strong);
          animation: time-machine-spin .8s linear infinite;
        }

        @keyframes time-machine-spin {
          to { transform: rotate(360deg); }
        }

        .time-machine-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .time-machine-item {
          appearance: none;
          width: 100%;
          padding: 14px 12px;
          border: 1px solid transparent;
          border-radius: 14px;
          background: transparent;
          color: inherit;
          text-align: left;
          transition: background .18s ease, border-color .18s ease, box-shadow .18s ease;
        }

        .time-machine-item:hover {
          background: rgba(255, 255, 255, 0.82);
        }

        .time-machine-item.is-active {
          background: #ffffff;
          border-color: #eceffd;
          box-shadow: 0 10px 24px rgba(31, 36, 48, 0.08);
        }

        .time-machine-item__title {
          font-size: 13px;
          font-weight: 700;
          color: var(--tm-text);
        }

        .time-machine-item__meta {
          margin-top: 8px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          font-size: 12px;
          color: var(--tm-muted);
        }

        .time-machine-item__author {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          min-width: 0;
        }

        .time-machine-item__author-name {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 116px;
        }

        .time-machine-panel__info {
          width: 18px;
          height: 18px;
          border-radius: 999px;
          background: #59c4ff;
          color: #ffffff;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          flex: none;
        }

        .time-machine-item__stats {
          margin-top: 8px;
          display: inline-flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .time-machine-item__stat {
          padding: 3px 8px;
          border-radius: 999px;
          background: #f4f1ff;
          color: var(--tm-accent-strong);
          font-size: 11px;
          font-weight: 700;
        }

        .time-machine-preview {
          position: fixed;
          left: 50%;
          bottom: 18px;
          transform: translate(-50%, 18px);
          width: min(680px, calc(100vw - 340px));
          min-height: 94px;
          padding: 18px 22px;
          border-radius: 16px;
          background: rgba(17, 18, 24, 0.96);
          color: #ffffff;
          box-shadow: 0 20px 44px rgba(0, 0, 0, 0.28);
          z-index: 37;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          opacity: 0;
          visibility: hidden;
          transition: opacity .2s ease, transform .2s ease, visibility .2s ease;
        }

        .time-machine-preview.is-visible {
          opacity: 1;
          visibility: visible;
          transform: translate(-50%, 0);
        }

        .time-machine-preview__title {
          font-size: 15px;
          font-weight: 700;
        }

        .time-machine-preview__meta {
          margin-top: 6px;
          color: rgba(255, 255, 255, 0.7);
          font-size: 13px;
        }

        .time-machine-preview__action {
          appearance: none;
          min-width: 170px;
          height: 44px;
          border: 0;
          border-radius: 10px;
          background: #8b7cff;
          color: #ffffff;
          font-size: 15px;
          font-weight: 600;
          box-shadow: 0 14px 28px rgba(139, 124, 255, 0.28);
        }

        .time-machine-preview__action:hover {
          background: #7b68ee;
        }
        """
    ).strip()


def time_machine_markup() -> str:
    return dedent(
        """
        <button class="time-machine-top-trigger" id="timeMachineTrigger" type="button">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 3.2a4.8 4.8 0 1 1-3.4 1.4"></path>
            <path d="M2.8 2.7v3.5h3.5"></path>
            <path d="M8 5.2v3.1l2.2 1.4"></path>
          </svg>
          <span>Машина времени</span>
        </button>

        <aside class="time-machine-panel" id="timeMachinePanel">
          <div class="time-machine-panel__header">
            <div>
              <div class="time-machine-panel__title">Машина времени</div>
              <div class="time-machine-panel__subtitle">Все сохраненные действия по странице и обсуждениям</div>
            </div>
            <button class="time-machine-panel__close" id="timeMachineClose" type="button" aria-label="Закрыть">×</button>
          </div>
          <div class="time-machine-panel__body">
            <div class="time-machine-panel__state" id="timeMachineLoading" hidden>
              <div class="time-machine-panel__spinner" aria-hidden="true"></div>
            </div>
            <div class="time-machine-panel__state" id="timeMachineEmpty" hidden>История действий пока пуста</div>
            <div class="time-machine-panel__state" id="timeMachineError" hidden>Не удалось загрузить версии. Попробуйте еще раз</div>
            <div class="time-machine-panel__scroll" id="timeMachineScroll" hidden>
              <div class="time-machine-list" id="timeMachineList"></div>
            </div>
          </div>
        </aside>

        <div class="time-machine-preview" id="timeMachinePreview">
          <div>
            <div class="time-machine-preview__title">Предварительный просмотр</div>
            <div class="time-machine-preview__meta" id="timeMachinePreviewMeta">Версия не выбрана</div>
          </div>
          <button class="time-machine-preview__action" id="timeMachineRestore" type="button">Восстановить версию</button>
        </div>
        """
    ).strip()


def time_machine_script() -> str:
    return Path(__file__).with_name("time_machine_script.js").read_text(encoding="utf-8")
