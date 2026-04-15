from __future__ import annotations

from pathlib import Path
from textwrap import dedent


def comments_styles() -> str:
    return dedent(
        """
        :root {
          --comment-accent: #8b7cff;
          --comment-accent-strong: #7461ff;
          --comment-accent-soft: #f2efff;
          --comment-accent-line: #d9d0ff;
          --comment-paused: #ef8e94;
          --comment-paused-strong: #dd6d76;
          --comment-paused-soft: #fff1f2;
          --comment-paused-line: #f4c4c8;
          --comment-panel-bg: rgba(250, 251, 255, 0.96);
          --comment-border: #e4e8f0;
          --comment-text: #2a3140;
          --comment-muted: #8e97a8;
          --comment-shadow: 0 22px 44px rgba(31, 36, 48, 0.14);
        }

        .comments-topbar {
          position: fixed;
          top: 18px;
          right: 26px;
          z-index: 36;
          display: flex;
          align-items: flex-start;
          gap: 10px;
        }

        .comments-topbar__trigger {
          appearance: none;
          border: 0;
          background: transparent;
          color: #8e97a8;
          font-size: 13px;
          font-weight: 600;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 2px;
        }
        .comments-topbar__trigger:hover,
        .comments-topbar__trigger.is-active {
          color: var(--comment-accent-strong);
        }

        .comments-topbar__trigger svg,
        .comment-anchor__icon svg,
        .comments-panel__icon svg,
        .comment-action svg,
        .comments-history__icon svg {
          width: 14px;
          height: 14px;
          display: block;
        }

        .comments-topbar__dropdown,
        .comments-access,
        .comment-card__menu {
          position: absolute;
          top: calc(100% + 8px);
          right: 0;
          width: 194px;
          padding: 8px;
          border-radius: 14px;
          border: 1px solid rgba(223, 227, 235, 0.92);
          background: rgba(255, 255, 255, 0.98);
          box-shadow: 0 18px 34px rgba(31, 36, 48, 0.16);
          opacity: 0;
          visibility: hidden;
          transform: translateY(-6px);
          transition: opacity .18s ease, transform .18s ease, visibility .18s ease;
          pointer-events: none;
        }

        .comments-topbar__dropdown.is-open,
        .comments-access.is-open,
        .comment-card__menu.is-open {
          opacity: 1;
          visibility: visible;
          transform: translateY(0);
          pointer-events: auto;
        }

        .comments-topbar__item {
          width: 100%;
          min-height: 42px;
          padding: 0 12px;
          border: 0;
          border-radius: 10px;
          background: transparent;
          color: #30384a;
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 13px;
          font-weight: 500;
          text-align: left;
        }

        .comments-topbar__item:hover {
          background: #f6f7fb;
        }

        .comments-access {
          width: 356px;
          padding: 18px 18px 14px;
        }

        .comments-access__title {
          font-size: 16px;
          font-weight: 700;
          color: var(--comment-text);
        }

        .comments-access__subtitle {
          margin-top: 4px;
          font-size: 13px;
          color: var(--comment-muted);
        }

        .comments-access__options {
          margin-top: 14px;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .comments-access__option {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #384152;
        }

        .comments-access__option input {
          margin: 0;
          accent-color: var(--comment-accent-strong);
        }

        .comment-anchor-layer {
          position: absolute;
          inset: 0;
          pointer-events: none;
          z-index: 28;
        }

        .comment-anchor {
          position: absolute;
          min-height: 22px;
          pointer-events: auto;
        }

        .comment-anchor__line {
          position: absolute;
          top: 0;
          left: 10px;
          width: 1px;
          background: var(--comment-accent-line);
          border-radius: 999px;
        }

        .comment-anchor__button {
          position: absolute;
          top: 0;
          left: 0;
          appearance: none;
          min-width: 24px;
          height: 22px;
          padding: 0 7px;
          border: 0;
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.94);
          color: var(--comment-accent-strong);
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          box-shadow: 0 8px 18px rgba(31, 36, 48, 0.10);
          transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
        }

        .comment-anchor__button:hover,
        .comment-anchor__button.is-active {
          transform: translateY(-1px);
          background: var(--comment-accent);
          color: #ffffff;
          box-shadow: 0 12px 24px rgba(139, 124, 255, 0.28);
        }

        .comment-anchor.is-paused .comment-anchor__line {
          background: var(--comment-paused-line);
        }

        .comment-anchor__button.is-paused {
          color: var(--comment-paused-strong);
          background: rgba(255, 255, 255, 0.96);
          box-shadow: 0 10px 20px rgba(221, 109, 118, 0.16);
        }

        .comment-anchor__button.is-paused:hover,
        .comment-anchor__button.is-paused.is-active {
          background: var(--comment-paused);
          color: #ffffff;
          box-shadow: 0 12px 24px rgba(221, 109, 118, 0.24);
        }

        .comment-anchor__button.is-empty {
          width: 22px;
          padding: 0;
          border: 1px solid rgba(139, 124, 255, 0.18);
        }

        .comment-anchor__button.is-create {
          color: var(--comment-accent-strong);
          background: rgba(255, 255, 255, 0.98);
        }

        .comment-anchor__badge {
          font-size: 11px;
          font-weight: 700;
          line-height: 1;
        }

        [data-comment-tooltip] {
          position: relative;
        }

        [data-comment-tooltip]:hover::after {
          content: attr(data-comment-tooltip);
          position: absolute;
          left: 50%;
          bottom: calc(100% + 8px);
          transform: translateX(-50%);
          padding: 6px 10px;
          border-radius: 8px;
          background: #16181d;
          color: #ffffff;
          font-size: 12px;
          white-space: nowrap;
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
          z-index: 12;
        }

        .comment-target--active {
          position: relative;
        }

        .comment-target--active::before {
          content: "";
          position: absolute;
          inset: -6px -10px;
          border-radius: 12px;
          background: rgba(139, 124, 255, 0.06);
          pointer-events: none;
        }

        .comment-selection-target {
          border-radius: 6px;
          box-decoration-break: clone;
          -webkit-box-decoration-break: clone;
          background: rgba(139, 124, 255, 0.12);
          transition: background .16s ease, box-shadow .16s ease;
          padding: 1px 2px;
        }

        .comment-selection-target:hover,
        .comment-selection-target.comment-target--active {
          background: rgba(139, 124, 255, 0.18);
          box-shadow: inset 0 0 0 1px rgba(139, 124, 255, 0.26);
        }

        .comments-panel {
          position: fixed;
          top: 74px;
          right: 20px;
          bottom: 18px;
          width: 332px;
          border-radius: 18px;
          border: 1px solid var(--comment-border);
          background: var(--comment-panel-bg);
          box-shadow: var(--comment-shadow);
          z-index: 34;
          display: flex;
          flex-direction: column;
          opacity: 0;
          visibility: hidden;
          transform: translateX(16px);
          transition: opacity .2s ease, transform .2s ease, visibility .2s ease;
          overflow: hidden;
          backdrop-filter: blur(12px);
        }

        .comments-panel.is-open {
          opacity: 1;
          visibility: visible;
          transform: translateX(0);
        }

        .comments-panel__header {
          padding: 18px 16px 14px;
          border-bottom: 1px solid #e8ebf2;
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 10px;
        }

        .comments-panel__title {
          font-size: 15px;
          font-weight: 700;
          color: var(--comment-text);
        }

        .comments-panel__context {
          margin-top: 6px;
          max-width: 240px;
          font-size: 13px;
          color: #8b94a5;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .comments-panel__status {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          margin-top: 8px;
          padding: 3px 8px;
          border-radius: 999px;
          background: rgba(139, 124, 255, 0.10);
          color: var(--comment-accent-strong);
          font-size: 11px;
          font-weight: 700;
        }

        .comments-panel__status.is-paused {
          background: var(--comment-paused-soft);
          color: var(--comment-paused-strong);
        }

        .comments-panel__header-actions {
          display: inline-flex;
          align-items: center;
          gap: 6px;
        }

        .comments-panel__header-button {
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
        }

        .comments-panel__header-button:hover {
          background: #f3f5f9;
          color: var(--comment-accent-strong);
        }

        .comments-panel__header-button.is-paused:hover,
        .comments-panel__header-button.is-paused.is-active {
          background: var(--comment-paused-soft);
          color: var(--comment-paused-strong);
        }

        .comments-panel__body {
          position: relative;
          flex: 1;
          min-height: 0;
          overflow: hidden;
          background: rgba(249, 250, 253, 0.75);
        }

        .comments-panel__scroll {
          height: 100%;
          overflow: auto;
          padding: 0 16px;
          scrollbar-width: thin;
          scrollbar-color: rgba(139, 124, 255, 0.35) transparent;
        }

        .comments-panel__scroll::-webkit-scrollbar {
          width: 8px;
        }

        .comments-panel__scroll::-webkit-scrollbar-thumb {
          border-radius: 999px;
          background: rgba(139, 124, 255, 0.24);
        }

        .comments-panel__placeholder,
        .comments-panel__loading,
        .comments-panel__error {
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: #8e97a8;
          font-size: 15px;
          padding: 0 24px;
        }

        .comments-panel__body > [hidden] {
          display: none !important;
        }

        .comments-panel__error-inner {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 14px;
          max-width: 230px;
        }

        .comments-panel__retry {
          appearance: none;
          min-width: 140px;
          height: 38px;
          border: 0;
          border-radius: 10px;
          background: var(--comment-accent);
          color: #ffffff;
          font-size: 14px;
          font-weight: 600;
          box-shadow: 0 10px 24px rgba(139, 124, 255, 0.24);
        }

        .comments-panel__spinner {
          width: 42px;
          height: 42px;
          border-radius: 999px;
          border: 4px solid rgba(139, 124, 255, 0.15);
          border-top-color: var(--comment-accent-strong);
          animation: comment-spin .8s linear infinite;
        }

        @keyframes comment-spin {
          to { transform: rotate(360deg); }
        }

        .comment-list {
          display: flex;
          flex-direction: column;
        }

        .comment-card {
          position: relative;
          display: grid;
          grid-template-columns: 34px 1fr;
          gap: 12px;
          padding: 14px 0;
          border-bottom: 1px solid #e8ebf2;
        }

        .comment-card:hover {
          background: rgba(139, 124, 255, 0.05);
        }

        .comment-card.is-focused {
          background: rgba(139, 124, 255, 0.10);
          border-radius: 14px;
        }

        .comment-card__avatar {
          width: 34px;
          height: 34px;
          border-radius: 999px;
          color: #ffffff;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          font-weight: 700;
          flex: none;
        }

        .comment-card__body {
          min-width: 0;
        }

        .comment-card__top {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 12px;
        }

        .comment-card__name {
          font-size: 13px;
          font-weight: 700;
          color: var(--comment-text);
        }

        .comment-card__meta-line {
          margin-top: 4px;
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          align-items: center;
        }

        .comment-card__date {
          margin-top: 2px;
          font-size: 12px;
          color: #8e97a8;
        }

        .comment-card__role {
          padding: 2px 7px;
          border-radius: 999px;
          background: #f4f6fb;
          color: #6f7b90;
          font-size: 11px;
          font-weight: 700;
        }

        .comment-card__text {
          margin-top: 10px;
          color: #374051;
          font-size: 13px;
          line-height: 1.58;
          word-break: break-word;
        }

        .comment-card__text .comment-mention {
          color: var(--comment-accent-strong);
          font-weight: 600;
        }

        .comment-card__text a,
        .comments-history-item__text a,
        .comments-history-item__preview a {
          color: var(--comment-accent-strong);
          text-decoration: none;
          font-weight: 600;
        }

        .comment-card__text a:hover,
        .comments-history-item__text a:hover,
        .comments-history-item__preview a:hover {
          text-decoration: underline;
        }

        .comment-card__target {
          margin-top: 10px;
          display: inline-flex;
          flex-wrap: wrap;
          gap: 8px;
          align-items: center;
        }

        .comment-card__target-type {
          padding: 3px 8px;
          border-radius: 999px;
          background: #f4f1ff;
          color: var(--comment-accent-strong);
          font-size: 11px;
          font-weight: 700;
        }

        .comment-card__target-preview {
          color: #8b95a7;
          font-size: 12px;
        }

        .comment-card__quote {
          margin-top: 10px;
          padding: 10px 12px;
          border-radius: 12px;
          border: 1px solid #eceafc;
          background: rgba(248, 247, 255, 0.92);
        }

        .comment-card__quote-label {
          color: var(--comment-accent-strong);
          font-size: 11px;
          font-weight: 700;
        }

        .comment-card__quote-text {
          margin-top: 4px;
          color: #5c6678;
          font-size: 12px;
          line-height: 1.45;
        }

        .comment-card__attachment {
          margin-top: 10px;
          display: inline-flex;
          align-items: center;
          gap: 10px;
          padding: 9px 11px;
          border-radius: 12px;
          background: #f7f8fc;
          color: #465163;
          font-size: 12px;
          font-weight: 600;
        }

        .comment-card__attachment-thumb {
          width: 46px;
          height: 28px;
          border-radius: 8px;
          background: linear-gradient(135deg, #d78f65 0%, #eac49d 45%, #6a7bdc 100%);
          flex: none;
        }

        .comment-card__attachment-icon {
          width: 20px;
          height: 20px;
          border-radius: 999px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          background: #eceffd;
          color: var(--comment-accent-strong);
          font-size: 12px;
          font-weight: 800;
          flex: none;
        }

        .comment-card__actions {
          opacity: 0;
          transition: opacity .16s ease;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          position: relative;
        }

        .comment-card:hover .comment-card__actions,
        .comment-card.is-menu-open .comment-card__actions,
        .comment-card.is-editing .comment-card__actions {
          opacity: 1;
        }

        .comment-action {
          appearance: none;
          min-width: 22px;
          height: 22px;
          border: 0;
          border-radius: 999px;
          background: transparent;
          color: #8a93a5;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 3px;
          font-size: 11px;
          font-weight: 700;
        }

        .comment-action:hover {
          background: rgba(139, 124, 255, 0.08);
          color: var(--comment-accent-strong);
        }

        .comment-action.is-active {
          background: rgba(139, 124, 255, 0.14);
          color: var(--comment-accent-strong);
        }

        .comment-card__menu-wrap[hidden] {
          display: none !important;
        }

        .comment-action__count {
          font-size: 11px;
          font-weight: 700;
        }

        .comment-card__menu {
          top: 24px;
          width: 156px;
          padding: 6px;
          z-index: 5;
        }

        .comment-card__menu button {
          width: 100%;
          min-height: 36px;
          border: 0;
          border-radius: 10px;
          background: transparent;
          text-align: left;
          padding: 0 12px;
          color: #333b4a;
          font-size: 13px;
          font-weight: 500;
        }

        .comment-card__menu button:hover {
          background: #f5f6fb;
        }

        .comment-card__menu .is-danger {
          color: #dc4d76;
        }

        .comment-card__editor {
          margin-top: 10px;
          padding: 10px;
          border-radius: 12px;
          border: 1px solid #dadff0;
          background: rgba(255, 255, 255, 0.94);
        }

        .comment-card__editor textarea {
          width: 100%;
          min-height: 78px;
          border: 1px solid #e2e6f0;
          border-radius: 10px;
          background: #fbfcff;
          resize: vertical;
          padding: 10px 12px;
          font-size: 13px;
          line-height: 1.5;
          color: #344053;
          outline: none;
        }

        .comment-card__editor textarea:focus {
          border-color: rgba(139, 124, 255, 0.5);
          box-shadow: 0 0 0 3px rgba(139, 124, 255, 0.12);
        }

        .comment-card__save {
          margin-top: 10px;
          appearance: none;
          min-width: 90px;
          height: 34px;
          border: 0;
          border-radius: 10px;
          background: var(--comment-accent);
          color: #ffffff;
          font-size: 13px;
          font-weight: 600;
        }

        .comments-panel__composer {
          position: sticky;
          bottom: 0;
          padding: 10px 12px 12px;
          border-top: 1px solid #e4e8f0;
          background: rgba(255, 255, 255, 0.98);
          backdrop-filter: blur(10px);
        }

        .comments-panel__meta {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 12px;
          margin-bottom: 8px;
        }

        .comments-panel__actor {
          min-width: 0;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .comments-panel__actor-label {
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.02em;
          text-transform: uppercase;
          color: #8b95a7;
        }

        .comments-panel__actor-select {
          min-width: 172px;
          height: 34px;
          padding: 0 12px;
          border-radius: 10px;
          border: 1px solid #e2e6f0;
          background: #ffffff;
          color: #334052;
          font-size: 13px;
          font-weight: 600;
          outline: none;
        }

        .comments-panel__actor-select:focus {
          border-color: rgba(139, 124, 255, 0.56);
          box-shadow: 0 0 0 3px rgba(139, 124, 255, 0.14);
        }

        .comments-panel__actor-note {
          font-size: 12px;
          color: #8e97a8;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .comments-panel__group-hints {
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: 6px;
        }

        .comments-panel__group-hint {
          padding: 5px 9px;
          border-radius: 999px;
          background: #f4f1ff;
          color: var(--comment-accent-strong);
          font-size: 11px;
          font-weight: 700;
        }

        .comments-panel__reply {
          display: none;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
          margin-bottom: 8px;
          padding: 10px 12px;
          border-radius: 14px;
          border: 1px solid #eceafc;
          background: rgba(248, 247, 255, 0.92);
          color: #556073;
          font-size: 12px;
        }

        .comments-panel__reply.is-visible {
          display: flex;
        }

        .comments-panel__reply strong,
        .comments-panel__reply .comment-mention {
          color: var(--comment-accent-strong);
        }

        .comments-panel__reply-cancel {
          appearance: none;
          width: 20px;
          height: 20px;
          border: 0;
          border-radius: 999px;
          background: transparent;
          color: #a0a8b6;
        }

        .comments-panel__reply-cancel:hover {
          background: #eceffd;
          color: var(--comment-accent-strong);
        }

        .comments-panel__composer-shell {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 44px 28px;
  gap: 8px;
  align-items: end;
}

        .comments-panel__composer-input {
          width: 100%;
          min-height: 44px;
          max-height: 140px;
          resize: none;
          padding: 10px 12px;
          border-radius: 12px;
          border: 1px solid #e2e6f0;
          background: #ffffff;
          color: #334052;
          font-size: 13px;
          line-height: 1.5;
          outline: none;
        }

        .comments-panel__composer-input:focus {
          border-color: rgba(139, 124, 255, 0.56);
          box-shadow: 0 0 0 3px rgba(139, 124, 255, 0.14);
        }

        .comments-panel__composer-ai {
  appearance: none;
  width: 44px;
  height: 44px;
  border: 1px solid #ddd6ff;
  border-radius: 12px;
  background: #f6f3ff;
  color: var(--comment-accent-strong);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
}

.comments-panel__composer-ai:hover {
  background: #efe9ff;
}

.comments-panel__composer-ai:disabled {
  opacity: 0.5;
}
        .comments-panel__composer-send {
          appearance: none;
          width: 28px;
          height: 28px;
          border: 0;
          border-radius: 999px;
          background: transparent;
          color: var(--comment-accent-strong);
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }

        .comments-panel__composer-send:disabled {
          color: #c1c8d6;
        }

        .comments-mentions {
          position: absolute;
          left: 0;
          right: 36px;
          bottom: calc(100% + 10px);
          border-radius: 14px;
          border: 1px solid #eceff6;
          background: rgba(255, 255, 255, 0.99);
          box-shadow: 0 20px 34px rgba(31, 36, 48, 0.16);
          overflow: hidden;
          opacity: 0;
          visibility: hidden;
          transform: translateY(6px);
          transition: opacity .16s ease, transform .16s ease, visibility .16s ease;
        }

        .comments-mentions.is-open {
          opacity: 1;
          visibility: visible;
          transform: translateY(0);
        }

        .comments-mentions__section {
          padding: 8px 12px 4px;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #98a1b3;
        }

        .comments-mentions__item,
        .comments-mentions__more {
          width: 100%;
          border: 0;
          background: transparent;
          padding: 10px 12px;
          display: grid;
          grid-template-columns: 30px 1fr;
          gap: 10px;
          align-items: center;
          text-align: left;
        }

        .comments-mentions__item:hover,
        .comments-mentions__item.is-active {
          background: #f7f7fd;
        }

        .comments-mentions__name {
          font-size: 13px;
          font-weight: 600;
          color: #313848;
        }

        .comments-mentions__nick {
          margin-top: 2px;
          font-size: 12px;
          color: #8b7cff;
        }

        .comments-mentions__meta {
          margin-top: 3px;
          font-size: 11px;
          color: #99a1b1;
        }

        .comments-mentions__group-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 30px;
          height: 30px;
          border-radius: 999px;
          background: linear-gradient(135deg, #8b7cff 0%, #ac8dff 100%);
          color: #ffffff;
          font-size: 11px;
          font-weight: 800;
          letter-spacing: 0.04em;
        }

        .comments-mentions__more {
          display: flex;
          justify-content: center;
          padding: 10px 12px 12px;
          border-top: 1px solid #eceff6;
          font-size: 13px;
          color: #7b8497;
        }

        .comments-history-modal {
          position: fixed;
          inset: 0;
          z-index: 44;
          display: none;
          align-items: center;
          justify-content: center;
          padding: 24px;
          background: rgba(11, 16, 24, 0.10);
          backdrop-filter: blur(4px);
        }

        .comments-history-modal.is-open {
          display: flex;
        }

        .comments-history-modal__dialog {
          width: min(860px, calc(100vw - 48px));
          max-height: calc(100vh - 48px);
          border-radius: 22px;
          border: 1px solid #e5e8f0;
          background: rgba(255, 255, 255, 0.99);
          box-shadow: 0 30px 70px rgba(17, 24, 39, 0.18);
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .comments-history-modal__header {
          padding: 22px 24px 14px;
          border-bottom: 1px solid #eceff5;
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: flex-start;
        }

        .comments-history-modal__title {
          font-size: 28px;
          font-weight: 700;
          color: #2c3444;
        }

        .comments-history-modal__subtitle {
          margin-top: 4px;
          font-size: 14px;
          color: #9aa3b4;
        }

        .comments-history-modal__close {
          appearance: none;
          width: 28px;
          height: 28px;
          border: 0;
          border-radius: 999px;
          background: transparent;
          color: #b4bccb;
        }

        .comments-history-modal__close:hover {
          background: #f5f7fb;
          color: #7f889a;
        }

        .comments-history-modal__body {
          min-height: 360px;
          max-height: calc(100vh - 180px);
          overflow: auto;
          padding: 0 24px;
        }

        .comments-history-modal__filters {
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
          gap: 12px;
          padding: 14px 24px;
          border-bottom: 1px solid #eceff5;
          background: rgba(250, 251, 255, 0.95);
        }

        .comments-history-modal__field {
          min-width: 0;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .comments-history-modal__field label {
          font-size: 11px;
          font-weight: 800;
          letter-spacing: .03em;
          text-transform: uppercase;
          color: #97a0b1;
        }

        .comments-history-modal__select {
          width: 100%;
          min-width: 0;
          height: 38px;
          border-radius: 12px;
          border: 1px solid #dde3ee;
          background: #ffffff;
          color: #334052;
          padding: 0 12px;
          font-size: 13px;
        }

        .comments-history-item {
          padding: 20px 0;
          border-bottom: 1px solid #eceff5;
        }

        .comments-history-item__head {
          display: grid;
          grid-template-columns: 42px 1fr auto;
          gap: 14px;
          align-items: start;
        }

        .comments-history-item__status {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 4px 8px;
          border-radius: 999px;
          background: #f4f6fb;
          color: #8b95a6;
          font-size: 12px;
          font-weight: 600;
          white-space: nowrap;
        }

        .comments-history-item__preview {
          margin: 10px 0 10px 56px;
          padding: 10px 14px;
          border-radius: 12px;
          background: #f7f8fc;
          color: #a2aabc;
          font-size: 13px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .comments-history-item__text {
          margin-left: 56px;
          color: #394254;
          font-size: 15px;
          line-height: 1.56;
        }

        .comments-history-item__thumb {
          margin: 12px 0 10px 56px;
          display: inline-flex;
          align-items: center;
          gap: 12px;
          padding: 10px 12px;
          border-radius: 12px;
          background: #f6f7fc;
          color: #4a5468;
          box-shadow: inset 0 0 0 1px rgba(255,255,255,0.5);
        }

        .comments-history-item__thumb-image {
          width: 74px;
          height: 40px;
          border-radius: 10px;
          background: linear-gradient(135deg, #d78f65 0%, #eac49d 45%, #6a7bdc 100%);
          flex: none;
        }

        .comments-history-item__thumb-label {
          font-size: 13px;
          font-weight: 600;
          color: #4a5468;
        }

        .comments-history-item__actions {
          margin: 10px 0 0 56px;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          color: var(--comment-accent-strong);
          font-size: 14px;
          font-weight: 500;
        }

        .comments-history-item__toggle {
          margin-top: 12px;
          margin-left: 56px;
          appearance: none;
          border: 0;
          background: transparent;
          color: var(--comment-accent-strong);
          font-size: 14px;
          font-weight: 500;
          padding: 0;
        }

        .comments-history-item__thread {
          margin-top: 16px;
          margin-left: 56px;
          padding-top: 8px;
        }

        .comments-history-item__nested {
          padding: 16px 0;
          border-top: 1px solid #eceff5;
        }

        .comments-history-item__nested.is-deleted {
          opacity: 0.72;
        }

        .comments-history-modal__error {
          min-height: 360px;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: #8d96a7;
          font-size: 18px;
        }

        .comments-history-modal__error-inner {
          display: flex;
          flex-direction: column;
          gap: 18px;
          align-items: center;
        }

        .comments-history-modal__footer {
          padding: 14px 24px 18px;
          border-top: 1px solid #eceff5;
          display: flex;
          align-items: center;
          justify-content: flex-start;
          gap: 8px;
        }

        .comments-history-modal__page,
        .comments-history-modal__ellipsis,
        .comments-history-modal__next {
          min-width: 30px;
          height: 30px;
          border-radius: 9px;
          border: 1px solid transparent;
          background: transparent;
          color: #485265;
          font-size: 14px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 0 8px;
        }

        .comments-history-modal__page.is-active {
          border-color: #d9dfea;
          background: #ffffff;
        }

        .comments-history-modal__next:hover,
        .comments-history-modal__page:hover {
          background: #f6f8fc;
        }

        @media (max-width: 1220px) {
          .comments-panel {
            width: 308px;
          }

          .comments-topbar {
            right: 18px;
          }
        }

        @media (max-width: 1040px) {
          .comments-panel {
            width: min(332px, calc(100vw - 28px));
            right: 14px;
            top: 84px;
            bottom: 12px;
          }

          .comments-topbar {
            right: 14px;
          }

          .comments-history-modal__dialog {
            width: calc(100vw - 28px);
          }
        }
        """
    ).strip()


def comments_markup() -> str:
    return dedent(
        """
        <div class="comments-topbar" id="commentsTopbar">
          <button class="comments-topbar__trigger" id="commentsTopTrigger" type="button">
            <span class="comments-topbar__icon">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2.5 3.5h11v7h-7l-2.8 2V10.5H2.5z"></path>
                <path d="M5.2 6.2h5.6M5.2 8.2h3.4"></path>
              </svg>
            </span>
            <span>Комментарии</span>
          </button>
          <div class="comments-topbar__dropdown" id="commentsTopDropdown">
            <button class="comments-topbar__item" id="commentsHistoryButton" type="button">
              <svg class="comments-history__icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2.4 3.4h11.2v9.2H2.4z"></path>
                <path d="M5 6h6M5 8.2h6M5 10.4h4"></path>
              </svg>
              <span>История комментариев</span>
            </button>
            <button class="comments-topbar__item" id="commentsAccessButton" type="button">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3.6" y="7" width="8.8" height="5.8" rx="1.5"></rect>
                <path d="M5.2 7V5.7A2.8 2.8 0 0 1 8 2.9 2.8 2.8 0 0 1 10.8 5.7V7"></path>
              </svg>
              <span>Доступ к комментариям</span>
            </button>
          </div>
          <div class="comments-access" id="commentsAccessPopup">
            <div class="comments-access__title">Доступ к комментариям</div>
            <div class="comments-access__subtitle">Укажите, кто может комментировать</div>
            <div class="comments-access__options">
              <label class="comments-access__option">
                <input type="radio" name="commentAccess" value="all" checked />
                <span>Все пользователи</span>
              </label>
              <label class="comments-access__option">
                <input type="radio" name="commentAccess" value="author" />
                <span>Только создатель страницы</span>
              </label>
            </div>
          </div>
        </div>

        <div class="comment-anchor-layer" id="commentAnchorLayer"></div>

        <aside class="comments-panel" id="commentsPanel">
          <div class="comments-panel__header">
            <div>
              <div class="comments-panel__title">Комментарии</div>
              <div class="comments-panel__context" id="commentsPanelContext">Нет выбранного блока</div>
              <div class="comments-panel__status" id="commentsPanelStatus" hidden>Решена</div>
            </div>
            <div class="comments-panel__header-actions">
              <button class="comments-panel__header-button" id="commentsPauseButton" type="button" data-comment-tooltip="Приостановить обсуждение">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="4" y="3" width="3" height="10" rx="1"></rect>
                  <rect x="9" y="3" width="3" height="10" rx="1"></rect>
                </svg>
              </button>
              <button class="comments-panel__header-button" id="commentsResolveButton" type="button" data-comment-tooltip="Отметить ветку как решенную">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3.2 8.4l3 3.1 6.7-7"></path>
                </svg>
              </button>
              <button class="comments-panel__header-button" id="commentsCloseButton" type="button" aria-label="Закрыть">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <path d="M4 4l8 8M12 4l-8 8"></path>
                </svg>
              </button>
            </div>
          </div>
          <div class="comments-panel__body">
            <div class="comments-panel__loading" id="commentsPanelLoading" hidden>
              <div class="comments-panel__spinner" aria-hidden="true"></div>
            </div>
            <div class="comments-panel__error" id="commentsPanelError" hidden>
              <div class="comments-panel__error-inner">
                <div>Не удалось загрузить комментарии. Попробуйте еще раз</div>
                <button class="comments-panel__retry" id="commentsRetryButton" type="button">Загрузить повторно</button>
              </div>
            </div>
            <div class="comments-panel__placeholder" id="commentsPanelPlaceholder" hidden>Нет комментариев</div>
            <div class="comments-panel__scroll" id="commentsPanelScroll">
              <div class="comment-list" id="commentsPanelList"></div>
            </div>
          </div>
          <div class="comments-panel__composer">
            <div class="comments-panel__meta">
              <label class="comments-panel__actor">
                <span class="comments-panel__actor-label">От имени</span>
                <select class="comments-panel__actor-select" id="commentsActorSelect"></select>
                <span class="comments-panel__actor-note" id="commentsActorNote"></span>
              </label>
              <div class="comments-panel__group-hints" id="commentsGroupHints"></div>
            </div>
            <div class="comments-panel__reply" id="commentsReplyPill">
              <div id="commentsReplyText">Ответ</div>
              <button class="comments-panel__reply-cancel" id="commentsReplyCancel" type="button" aria-label="Отменить ответ">?</button>
            </div>
            <div class="comments-panel__composer-shell">
  <div class="comments-mentions" id="commentsMentionDropdown"></div>
  <textarea class="comments-panel__composer-input" id="commentsComposerInput" placeholder="Новый комментарий"></textarea>
  <button class="comments-panel__composer-ai" id="commentsComposerAi" type="button" aria-label="Исправить через AI">AI</button>
  <button class="comments-panel__composer-send" id="commentsComposerSend" type="button" aria-label="Отправить">
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2L2.8 7.2l4 1 1 4L14 2z"></path>
    </svg>
  </button>
</div>
          </div>
        </aside>

        <div class="comments-history-modal" id="commentsHistoryModal">
          <div class="comments-history-modal__dialog" role="dialog" aria-modal="true" aria-labelledby="commentsHistoryTitle">
            <div class="comments-history-modal__header">
              <div>
                <div class="comments-history-modal__title" id="commentsHistoryTitle">История комментариев</div>
                <div class="comments-history-modal__subtitle">Отображаются удаленные или решенные ветки</div>
              </div>
              <button class="comments-history-modal__close" id="commentsHistoryClose" type="button" aria-label="Закрыть">?</button>
            </div>
            <div class="comments-history-modal__filters">
              <div class="comments-history-modal__field">
                <label for="commentsHistoryPageSelect">Страница</label>
                <select class="comments-history-modal__select" id="commentsHistoryPageSelect"></select>
              </div>
              <div class="comments-history-modal__field">
                <label for="commentsHistoryThreadSelect">Обсуждение</label>
                <select class="comments-history-modal__select" id="commentsHistoryThreadSelect"></select>
              </div>
            </div>
            <div class="comments-history-modal__body" id="commentsHistoryBody"></div>
            <div class="comments-history-modal__footer" id="commentsHistoryFooter"></div>
          </div>
        </div>
        """
    ).strip()


def comments_script() -> str:
    return Path(__file__).with_name("comments_script.js").read_text(encoding="utf-8")
