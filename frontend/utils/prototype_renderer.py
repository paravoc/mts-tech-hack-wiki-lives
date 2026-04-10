from __future__ import annotations

from html import escape

import streamlit as st


SECTIONS = [
    ("time-machine", "Машина времени"),
    ("comment-history", "История комментариев"),
    ("comment-access", "Управление доступом к комментариям"),
    ("comments", "Комментирование"),
    ("image", "Изображение"),
    ("link", "Ссылка"),
    ("page-basics", "Базовое взаимодействие со страницей"),
    ("page-loading", "Загрузка страницы"),
]


def icon(name: str, cls: str = "ui-icon") -> str:
    paths = {
        "square": "<rect x='3' y='3' width='14' height='14' rx='3'></rect>",
        "file": "<path d='M6 3.5h7l4 4V18a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5.5a2 2 0 0 1 2-2Z'></path><path d='M13 3.5V8h4'></path>",
        "undo": "<path d='M8 7H4V3'></path><path d='M4 7a8 8 0 1 1 2.6 5.9'></path>",
        "redo": "<path d='M16 7h4V3'></path><path d='M20 7a8 8 0 1 0-2.6 5.9'></path>",
        "align-left": "<path d='M4 6h14'></path><path d='M4 10h10'></path><path d='M4 14h14'></path><path d='M4 18h8'></path>",
        "align-center": "<path d='M5 6h14'></path><path d='M7 10h10'></path><path d='M5 14h14'></path><path d='M8 18h8'></path>",
        "align-right": "<path d='M6 6h14'></path><path d='M10 10h10'></path><path d='M6 14h14'></path><path d='M12 18h8'></path>",
        "list": "<path d='M9 6h11'></path><path d='M9 12h11'></path><path d='M9 18h11'></path><circle cx='5' cy='6' r='1'></circle><circle cx='5' cy='12' r='1'></circle><circle cx='5' cy='18' r='1'></circle>",
        "ordered": "<path d='M10 6h10'></path><path d='M10 12h10'></path><path d='M10 18h10'></path><path d='M4 7h2V4'></path><path d='M4 11c0-1 2-1 2 0s-2 1-2 2h2'></path><path d='M4 16c0-1 2-1 2 0s-1 1-1 1'></path>",
        "checklist": "<path d='M9 6h11'></path><path d='M9 12h11'></path><path d='M9 18h11'></path><path d='M4 6.5l1.4 1.4L7.8 5.5'></path><path d='M4 12.5l1.4 1.4 2.4-2.4'></path>",
        "link": "<path d='M10 14a3 3 0 0 0 4.2 0l3.3-3.3a3 3 0 0 0-4.2-4.2L11 8.7'></path><path d='M14 10a3 3 0 0 0-4.2 0l-3.3 3.3a3 3 0 1 0 4.2 4.2l2.2-2.2'></path>",
        "quote": "<path d='M6 8h5v5H7v4H4v-5a4 4 0 0 1 2-4Z'></path><path d='M15 8h5v5h-4v4h-3v-5a4 4 0 0 1 2-4Z'></path>",
        "image": "<rect x='3.5' y='5' width='17' height='14' rx='2.5'></rect><circle cx='8' cy='10' r='1.5'></circle><path d='m6 16 3.5-3.5 2.8 2.8 2.5-2.5 3.2 3.2'></path>",
        "comment": "<path d='M5 6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5v6A2.5 2.5 0 0 1 16.5 15H10l-4.5 4v-4H7.5A2.5 2.5 0 0 1 5 12.5Z'></path>",
        "close": "<path d='m6 6 12 12'></path><path d='m18 6-12 12'></path>",
        "send": "<path d='m4 12 15-7-3 14-4-5-8-2Z'></path>",
        "more": "<circle cx='6' cy='12' r='1.5'></circle><circle cx='12' cy='12' r='1.5'></circle><circle cx='18' cy='12' r='1.5'></circle>",
        "heart": "<path d='M12 19s-6.7-4.3-8.6-7.5C1.5 8.3 3.2 5 6.5 5c2 0 3.1 1 3.5 1.8C10.4 6 11.5 5 13.5 5 16.8 5 18.5 8.3 16.6 11.5 14.7 14.7 12 19 12 19Z'></path>",
        "thumb": "<path d='M8 10V6.8c0-1.1.9-2.3 2-2.8L11.7 3v7H19l-1 8H8'></path><path d='M4 10h4v9H4z'></path>",
        "history": "<path d='M3 12a9 9 0 1 0 2.7-6.4'></path><path d='M3 4v4h4'></path><path d='M12 7v5l3 2'></path>",
        "shield": "<path d='M12 3 5 6v5c0 4.5 2.9 7.5 7 9 4.1-1.5 7-4.5 7-9V6Z'></path>",
        "loader": "<path d='M12 4a8 8 0 0 1 8 8'></path><path d='M12 20a8 8 0 0 1-8-8'></path>",
        "check": "<path d='m5 12 4 4 10-10'></path>",
        "code": "<path d='m8 8-4 4 4 4'></path><path d='m16 8 4 4-4 4'></path><path d='m14 4-4 16'></path>",
    }
    path = paths[name]
    return (
        f"<svg class='{cls}' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
        f"stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'>{path}</svg>"
    )


def nav_item(target: str, label: str) -> str:
    return f"<a class='side-nav__item' href='#{target}'>{icon('square')}<span>{escape(label)}</span></a>"


def section_label(title: str) -> str:
    return f"<div class='scene-label'>{escape(title)}</div>"


def frame(title: str, body: str, wide: bool = False) -> str:
    cls = "frame frame--wide" if wide else "frame"
    return f"<div class='{cls}'><div class='frame__title'>{escape(title)}</div><div class='frame__viewport'>{body}</div></div>"


def surface(content: str, accent: bool = False, section_id: str = "", title: str = "") -> str:
    cls = "scene scene--accent" if accent else "scene"
    anchor = f" id='{escape(section_id)}'" if section_id else ""
    label = section_label(title) if title else ""
    return f"<section{anchor} class='{cls}'>{label}<div class='scene__body'>{content}</div></section>"


def tool_button(label: str, icon_name: str | None = None, active: bool = False, text: bool = False) -> str:
    cls = "tool-btn is-active" if active else "tool-btn"
    label_html = f"<span class='tool-btn__text'>{escape(label)}</span>" if label else ""
    icon_html = icon(icon_name, "tool-btn__icon") if icon_name else ""
    text_cls = " tool-btn--text" if text else ""
    return f"<button class='{cls}{text_cls}' type='button'>{icon_html}{label_html}</button>"


def toolbar(active: str = "") -> str:
    return (
        "<div class='editor-toolbar'><div class='editor-toolbar__group'>"
        f"{tool_button('', 'undo')}{tool_button('', 'redo')}"
        f"{tool_button('B', active=active == 'bold', text=True)}"
        f"{tool_button('T', 'square', active=active == 'type')}"
        f"{tool_button('U', active=active == 'underline', text=True)}"
        f"{tool_button('H1', active=active == 'h1', text=True)}"
        f"{tool_button('H2', active=active == 'h2', text=True)}"
        f"{tool_button('H3', active=active == 'h3', text=True)}</div>"
        "<div class='editor-toolbar__group'>"
        f"{tool_button('', 'align-left', active=active == 'align-left')}"
        f"{tool_button('', 'align-center', active=active == 'align-center')}"
        f"{tool_button('', 'align-right', active=active == 'align-right')}"
        f"{tool_button('', 'list', active=active == 'list')}"
        f"{tool_button('', 'ordered', active=active == 'ordered')}"
        f"{tool_button('@', active=active == 'mention', text=True)}"
        f"{tool_button('', 'link', active=active == 'link')}"
        f"{tool_button('', 'quote', active=active == 'quote')}"
        f"{tool_button('', 'image', active=active == 'image')}</div></div>"
    )


def floating_toolbar(active: str = "", with_tooltip: bool = False, with_link_menu: bool = False) -> str:
    link_menu = (
        "<div class='mini-dropdown mini-dropdown--link'>"
        f"{tool_button('', 'link', active=True)}{tool_button('', 'square')}{tool_button('', 'quote')}</div>"
        if with_link_menu
        else ""
    )
    tooltip = "<div class='black-tooltip'>Tooltip Text</div>" if with_tooltip else ""
    return (
        "<div class='floating-toolbar-wrap'><div class='floating-toolbar'>"
        f"{tool_button('B', active=active == 'bold', text=True)}"
        f"{tool_button('I', active=active == 'italic', text=True)}"
        f"{tool_button('U', active=active == 'underline', text=True)}"
        f"{tool_button('', 'link', active=active == 'link')}"
        f"{tool_button('', 'list', active=active == 'list')}"
        f"{tool_button('', 'align-left', active=active == 'align-left')}"
        f"</div>{link_menu}{tooltip}</div>"
    )


def top_links(active: str = "") -> str:
    return (
        "<div class='top-links'>"
        f"<a class='top-link{' is-active' if active == 'comments' else ''}' href='#comments'>Комментарии</a>"
        f"<a class='top-link{' is-active' if active == 'time' else ''}' href='#time-machine'>Машина времени</a>"
        "</div>"
    )


def editor_header(title: str, description: str, links: str = "") -> str:
    return (
        "<div class='editor-head'><div class='editor-head__main'>"
        f"{icon('file', 'doc-icon')}<div class='editor-head__meta'>"
        f"<div class='editor-head__title'>{escape(title)}</div>"
        f"<div class='editor-head__description'>{escape(description)}</div>"
        f"</div></div>{links}</div>"
    )


def viewer_banner() -> str:
    return (
        "<div class='viewer-banner'><span>You can only view and comment on this file.</span>"
        "<button class='viewer-banner__action' type='button'>Ask to edit</button>"
        f"<button class='viewer-banner__close' type='button'>{icon('close')}</button></div>"
    )


def command_menu(filtered: bool = False) -> str:
    items = [
        ("Обычный текст", "square"),
        ("Заголовок 1", "square"),
        ("Заголовок 2", "square"),
        ("Заголовок 3", "square"),
        ("Маркированный список", "list"),
        ("Нумерованный список", "ordered"),
        ("Чеклист", "checklist"),
        ("Код", "code"),
        ("Цитата", "quote"),
        ("Изображение", "image"),
    ]
    if filtered:
        items = items[1:4]
    rows = "".join(
        f"<div class='command-menu__item{' is-hovered' if index == 0 else ''}'>{icon(icon_name)}<span>{escape(label)}</span></div>"
        for index, (label, icon_name) in enumerate(items)
    )
    return f"<div class='command-menu'>{rows}</div>"


def selected_span(text: str) -> str:
    return f"<span class='selected-span'>{escape(text)}</span>"


def form_field(label: str, value: str = "", placeholder: str = "") -> str:
    text = escape(value) if value else ""
    placeholder_html = f"<span class='field__placeholder'>{escape(placeholder)}</span>" if placeholder and not value else ""
    return (
        "<label class='form-field'>"
        f"<span class='form-field__label'>{escape(label)}</span>"
        f"<span class='form-field__input'>{text}{placeholder_html}</span></label>"
    )


def modal_button(label: str, primary: bool = False, disabled: bool = False) -> str:
    cls = "modal-btn modal-btn--primary" if primary else "modal-btn"
    if disabled:
        cls += " is-disabled"
    return f"<button class='{cls}' type='button'>{escape(label)}</button>"


def image_mock(selected: bool = False, compact: bool = False, toolbar_visible: bool = False) -> str:
    handles = "".join(
        f"<span class='resize-handle resize-handle--{name}'></span>"
        for name in ["tl", "tr", "bl", "br", "tm", "bm", "ml", "mr"]
    )
    toolbar_html = (
        "<div class='image-float-toolbar'><span class='image-float-toolbar__pill'>small</span>"
        "<span class='image-float-toolbar__pill is-active'>medium</span><span class='image-float-toolbar__pill'>large</span>"
        f"{icon('align-left')} {icon('align-center')} {icon('align-right')} {icon('close')}</div>"
        if toolbar_visible
        else ""
    )
    cls = "image-block is-selected" if selected else "image-block"
    cls += " image-block--compact" if compact else ""
    return (
        f"<div class='{cls}'><div class='image-art'><div class='image-art__sky'></div>"
        "<div class='image-art__mountain image-art__mountain--back'></div>"
        "<div class='image-art__mountain image-art__mountain--front'></div><div class='image-art__sun'></div></div>"
        f"{handles if selected else ''}{toolbar_html}</div>"
    )


def skeleton_page() -> str:
    return (
        "<div class='editor-card'>"
        f"{editor_header('Новая страница', 'Добавить описание')}{toolbar()}"
        "<div class='editor-card__body editor-card__body--skeleton'>"
        "<div class='skeleton skeleton--short'></div><div class='skeleton'></div>"
        "<div class='skeleton skeleton--mid'></div><div class='skeleton'></div>"
        "<div class='skeleton skeleton--wide'></div></div></div>"
    )


def empty_page() -> str:
    body = (
        "<div class='doc-area doc-area--airy'><div class='focus-title'>Новая страница</div>"
        "<div class='focus-hint'>Начните вводить содержимое или нажмите / чтобы использовать команды</div></div>"
    )
    return f"<div class='editor-card'>{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='h1')}<div class='editor-card__body'>{body}</div></div>"


def content_page(with_viewer_banner: bool = True) -> str:
    body = (
        "<div class='doc-area doc-area--content'><h1 class='doc-title'>Отчет за IV квартал 2024</h1>"
        "<p class='doc-description'>Отчет включает сводку по взаимодействию клиентов Табс с ключевым функционалом платформы.</p>"
        "<h3 class='doc-subtitle'>Популярность инструментов:</h3>"
        "<p class='doc-paragraph'>Клиенты чаще всего используют редактор, совместное комментирование и быстрые ссылки между страницами.</p>"
        "<p class='doc-paragraph'>/<span class='doc-typed'>изо</span></p>"
        f"{command_menu()}</div>"
    )
    banner = viewer_banner() if with_viewer_banner else ""
    return f"<div class='editor-card editor-card--viewer'>{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='image')}<div class='editor-card__body'>{body}</div>{banner}</div>"


def heading_picker_page() -> str:
    body = (
        "<div class='doc-area doc-area--content'><h1 class='doc-title'>Новая страница</h1>"
        "<p class='doc-paragraph'>/загол</p>"
        f"{command_menu(filtered=True)}</div>"
    )
    return f"<div class='editor-card'>{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='type')}<div class='editor-card__body'>{body}</div></div>"


def toolbar_showcase() -> str:
    body = (
        "<div class='doc-area doc-area--content'><h1 class='doc-title'>Новая страница</h1>"
        "<p class='doc-paragraph'>Панель инструментов повторяет структуру макета и служит главным центром управления текстом.</p></div>"
    )
    return f"<div class='editor-card'>{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='link')}<div class='editor-card__body'>{body}</div></div>"


def selection_page() -> str:
    body = (
        "<div class='doc-area doc-area--content is-selection-demo'><h1 class='doc-title'>Отчет за IV квартал 2024</h1>"
        "<p class='doc-paragraph'>Отчет включает сводку по взаимодействию клиентов Табс с "
        f"{selected_span('ключевым функционалом платформы')}"
        f".</p>{floating_toolbar(active='bold', with_tooltip=True)}</div>"
    )
    return f"<div class='editor-card'>{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='bold')}<div class='editor-card__body'>{body}</div></div>"


def link_inline_state() -> str:
    body = (
        "<div class='doc-area doc-area--content is-selection-demo'><h1 class='doc-title'>Отчет за IV квартал 2024</h1>"
        "<p class='doc-paragraph'>Отчет включает сводку по взаимодействию клиентов Табс с "
        f"{selected_span('ключевым функционалом платформы')}"
        f".</p>{floating_toolbar(active='link', with_link_menu=True)}</div>"
    )
    return f"<div class='editor-card'>{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='link')}<div class='editor-card__body'>{body}</div></div>"


def link_modal(primary_disabled: bool = False) -> str:
    return (
        "<div class='editor-card editor-card--modal-demo'>"
        f"{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='link')}"
        "<div class='editor-card__body editor-card__body--dim'></div>"
        "<div class='modal modal--center'><div class='modal__title'>Вставить ссылку</div>"
        f"{form_field('Label', 'Отчет за IV квартал 2024' if not primary_disabled else '', 'Введите текст')}"
        f"{form_field('Filled text', '' if primary_disabled else 'https://wikilive.tabs/report', 'Введите ссылку')}"
        "<label class='check-row'><span class='check-row__box is-checked'></span><span>Открывать в новой вкладке</span></label>"
        f"<div class='modal__actions'>{modal_button('Кнопка', primary=not primary_disabled, disabled=primary_disabled)}{modal_button('Кнопка')}</div></div></div>"
    )


def upload_zone(with_preview: bool = False, error_text: str = "", alert: str = "", disabled: bool = False) -> str:
    preview = ""
    if with_preview:
        retry = "<a class='upload-preview__retry' href='#'>Повторить</a>" if error_text else ""
        status_cls = "upload-preview__status is-error" if error_text else "upload-preview__status"
        status = error_text if error_text else "Файл добавлен"
        preview = (
            "<div class='upload-preview'><div class='upload-preview__thumb'><div class='image-art image-art--thumb'>"
            "<div class='image-art__sky'></div><div class='image-art__mountain image-art__mountain--back'></div>"
            "<div class='image-art__mountain image-art__mountain--front'></div><div class='image-art__sun'></div></div></div>"
            f"<div class='upload-preview__meta'><div class='upload-preview__name'>screen.png</div><div class='{status_cls}'>{escape(status)}</div>{retry}</div>"
            "<div class='upload-preview__size'>1.2 МБ</div></div>"
        )
    alert_html = f"<div class='alert'>{escape(alert)}</div>" if alert else ""
    return (
        f"{alert_html}<div class='dropzone'><div class='dropzone__label'>Файл изображения</div>"
        "<div class='dropzone__box'>"
        f"{icon('image')}<div class='dropzone__line'><a href='#'>Выберите файл</a><span>или переместите его сюда</span></div>"
        "<div class='dropzone__hint'>Формат файла JPG, PNG, GIF. Не более 5 МБ</div></div>"
        f"{preview}</div><div class='modal__actions'>{modal_button('Отменить')}{modal_button('Подтвердить', primary=True, disabled=disabled)}</div>"
    )


def image_modal(state: str) -> str:
    if state == "selected":
        inner = upload_zone(with_preview=True, disabled=False)
    elif state == "upload-error":
        inner = upload_zone(with_preview=True, error_text="Ошибка загрузки", disabled=True)
    elif state == "format-error":
        inner = upload_zone(alert="Для загрузки доступны файлы в форматах JPG, PNG, GIF", disabled=True)
    else:
        inner = upload_zone(disabled=True)
    return (
        "<div class='editor-card editor-card--modal-demo'>"
        f"{editor_header('Новая страница', 'Добавить описание')}{toolbar(active='image')}"
        "<div class='editor-card__body editor-card__body--dim'></div>"
        "<div class='modal modal--center modal--wide'><div class='modal__head'><div class='modal__title'>Вставить изображение</div>"
        f"<button class='icon-btn' type='button'>{icon('close')}</button></div>{inner}</div></div>"
    )


def inserted_image_page() -> str:
    body = (
        "<div class='doc-area doc-area--content'><h1 class='doc-title'>Отчет за IV квартал 2024</h1>"
        "<p class='doc-description'>Отчет включает сводку по взаимодействию клиентов Табс с ключевым функционалом платформы.</p>"
        "<h3 class='doc-subtitle'>Популярность инструментов:</h3>"
        f"{image_mock(selected=True, toolbar_visible=True)}"
        f"<div class='image-pair'>{image_mock(selected=True, compact=True)}{image_mock(selected=False, compact=True)}</div></div>"
    )
    return f"<div class='editor-card'>{editor_header('Отчет за IV квартал 2024', 'Добавить описание')}{toolbar(active='image')}<div class='editor-card__body'>{body}</div></div>"


def comment_badge(count: str = "22", tooltip: str = "") -> str:
    tooltip_html = f"<div class='black-tooltip black-tooltip--side'>{escape(tooltip)}</div>" if tooltip else ""
    return f"<div class='comment-badge-wrap'><div class='comment-badge'>{icon('comment')}<span>{escape(count)}</span></div>{tooltip_html}</div>"


def avatar(letter: str, tone: str) -> str:
    return f"<span class='avatar avatar--{tone}'>{escape(letter)}</span>"


def comment_item(
    letter: str,
    tone: str,
    name: str,
    date: str,
    text: str,
    likes: str = "",
    with_menu: bool = False,
    highlighted: bool = False,
    editing: bool = False,
) -> str:
    count = f"<span class='comment-item__count'>{escape(likes)}</span>" if likes else ""
    actions = (
        "<div class='comment-item__actions'>"
        f"<button class='icon-btn' type='button'>{icon('thumb')}</button>"
        f"{count}"
        f"<button class='icon-btn' type='button'>{icon('heart')}</button>"
        f"<button class='icon-btn' type='button'>{icon('more')}</button>"
        "</div>"
        if with_menu
        else ""
    )
    body = (
        "<div class='comment-editor-inline'><div class='comment-editor-inline__field'>"
        "Этот текст тяжело воспринимать. Давайте сделаем его проще и понятнее для читателя."
        "</div>"
        f"{modal_button('Сохранить', primary=True)}</div>"
        if editing
        else f"<div class='comment-item__text'>{escape(text)}</div>"
    )
    cls = "comment-item is-highlighted" if highlighted else "comment-item"
    return (
        f"<div class='{cls}'>{avatar(letter, tone)}<div class='comment-item__body'>"
        f"<div class='comment-item__top'><div><div class='comment-item__name'>{escape(name)}</div>"
        f"<div class='comment-item__date'>{escape(date)}</div></div>{actions}</div>"
        f"{body}</div></div>"
    )


def mention_list() -> str:
    users = [
        ("И", "blue", "Иван Иванов", "@ivan"),
        ("С", "violet", "Сергей Иванов", "@sergei"),
        ("А", "yellow", "Антон Серганов", "@anton"),
    ]
    rows = "".join(
        "<div class='mention-row'>"
        f"{avatar(letter, tone)}"
        "<div class='mention-row__meta'>"
        f"<div class='mention-row__name'>{escape(name)}</div>"
        f"<div class='mention-row__login'>{escape(login)}</div>"
        "</div></div>"
        for letter, tone, name, login in users
    )
    return f"<div class='mention-list'>{rows}<div class='mention-list__more'>Дополнительно</div></div>"


def comment_panel(mode: str = "list") -> str:
    content = ""
    reply = ""
    footer_extra = ""
    header_status = ""
    if mode == "empty":
        content = "<div class='panel-empty'>Нет комментариев</div>"
    elif mode == "loading":
        content = f"<div class='panel-empty panel-empty--loader'>{icon('loader', 'loader-icon')}</div>"
    elif mode == "error":
        content = (
            "<div class='panel-empty panel-empty--text'><div>Не удалось загрузить комментарии. Попробуйте еще раз</div>"
            f"{modal_button('Загрузить повторно', primary=True)}</div>"
        )
    else:
        comments = [
            comment_item(
                "И",
                "blue",
                "Иван Иванов",
                "27.10.25 в 18:03",
                "Думаю этот параграф стоит переписать, слишком сложно, тут же весь смысл в простоте донесения мысли.",
                likes="4",
                with_menu=True,
                highlighted=mode in {"list", "reply", "solved"},
            ),
            comment_item(
                "С",
                "violet",
                "Сергей Иванов",
                "27.10.25 в 18:14",
                "@sergei уволен!",
                with_menu=True,
            ),
            comment_item(
                "А",
                "yellow",
                "Антон Серганов",
                "27.10.25 в 18:20",
                "Слишком сложно написано. Нужно, чтобы читатель понимал все с первого раза, как будто с другом говоришь.",
                with_menu=mode == "long",
            ),
        ]
        if mode == "editing":
            comments[0] = comment_item(
                "И",
                "blue",
                "Иван Иванов",
                "27.10.25 в 18:03",
                "",
                with_menu=True,
                highlighted=True,
                editing=True,
            )
        content = "<div class='comment-list'>" + "".join(comments) + "</div>"
    if mode == "reply":
        reply = "<div class='reply-chip'>Ответ @sergei: …<button type='button'>×</button></div>"
        footer_extra = mention_list()
    if mode == "solved":
        header_status = "<span class='resolved-pill'>Solved</span>"
    return (
        "<aside class='comment-panel'><div class='comment-panel__head'>"
        "<div class='comment-panel__title'>Комментарии</div>"
        f"<div class='comment-panel__head-actions'>{header_status}<button class='icon-btn' type='button'>{icon('check')}</button><button class='icon-btn' type='button'>{icon('close')}</button></div>"
        "</div><div class='comment-panel__context'>Этот текст тяжело воспринимать. Давайте сделаем его проще и понятнее для читателя.</div>"
        f"<div class='comment-panel__content'>{content}</div><div class='comment-panel__footer'>{reply}"
        f"<div class='comment-input'><span>Новый комментарий</span><button class='icon-btn icon-btn--accent' type='button'>{icon('send')}</button></div>"
        f"{footer_extra}</div></aside>"
    )


def comment_page() -> str:
    body = (
        "<div class='doc-with-comments'><div class='doc-area doc-area--content'>"
        "<h1 class='doc-title'>Страница для комментирования</h1>"
        "<p class='doc-paragraph'>Порой кажется, что наша жизнь — это бесконечное плавание против течения, в мутной воде повседневных забот. Мы, как упрямые лососи, стремимся к своим целям, преодолевая пороги трудностей и обходя сети сомнений.</p>"
        "<div class='paragraph-comment-anchor'><p class='doc-paragraph'>Но стоит лишь на мгновение остановиться и прислушаться к тихому плеску мыслей, как становится ясно: каждый из нас — это целый океан возможностей.</p>"
        "<div class='paragraph-comment-anchor__rail'></div>"
        f"{comment_badge('22')}"
        f"<div class='paragraph-comment-anchor__icon'>{icon('comment')}</div></div>"
        "<p class='doc-paragraph'>Именно в этой внутренней глубине скрывается тот самый источник, из которого рождаются настоящие действия и смелые решения.</p>"
        f"</div>{comment_panel('list')}</div>"
    )
    return f"<div class='editor-card'>{editor_header('Страница для комментирования', 'Добавить описание', top_links('comments'))}{toolbar(active='quote')}<div class='editor-card__body'>{body}</div></div>"


def comment_controls_showcase() -> str:
    return (
        "<div class='mini-cards'>"
        "<div class='mini-card'><div class='mini-card__title'>Кнопка комментария</div>"
        f"<div class='mini-card__row'><button class='icon-btn icon-btn--soft' type='button'>{icon('comment')}</button><div class='black-tooltip black-tooltip--inline'>Начать обсуждение</div></div></div>"
        "<div class='mini-card'><div class='mini-card__title'>Счетчик комментариев</div>"
        f"<div class='mini-card__row'>{comment_badge('22', 'Показать 22 комментария')}</div></div>"
        f"<div class='mini-card'><div class='mini-card__title'>Упоминания</div>{mention_list()}</div></div>"
    )


def comment_panel_states() -> str:
    return (
        "<div class='panel-state-grid'>"
        f"<div class='panel-state'>{comment_panel('empty')}</div>"
        f"<div class='panel-state'>{comment_panel('loading')}</div>"
        f"<div class='panel-state'>{comment_panel('error')}</div>"
        f"<div class='panel-state'>{comment_panel('reply')}</div>"
        f"<div class='panel-state'>{comment_panel('editing')}</div>"
        f"<div class='panel-state'>{comment_panel('solved')}</div>"
        "</div>"
    )


def access_dropdown() -> str:
    return (
        "<div class='editor-card'>"
        f"{editor_header('Новая страница', 'Добавить описание', top_links('comments'))}{toolbar(active='quote')}"
        "<div class='editor-card__body editor-card__body--compact'></div>"
        "<div class='small-dropdown small-dropdown--top-right'>"
        f"<div class='small-dropdown__item'>{icon('history')}<span>История комментариев</span></div>"
        f"<div class='small-dropdown__item is-hovered'>{icon('shield')}<span>Доступ к комментариям</span></div>"
        "</div></div>"
    )


def access_popup() -> str:
    return (
        "<div class='editor-card'>"
        f"{editor_header('Новая страница', 'Добавить описание', top_links('comments'))}{toolbar(active='quote')}"
        "<div class='editor-card__body editor-card__body--compact'></div>"
        "<div class='popup popup--top-right'><div class='popup__title'>Доступ к комментариям</div>"
        "<div class='popup__text'>Укажите, кто может комментировать</div>"
        "<label class='radio-row'><span class='radio-row__dot is-active'></span><span>Все пользователи</span></label>"
        "<label class='radio-row'><span class='radio-row__dot'></span><span>Только создатель страницы</span></label>"
        "</div></div>"
    )


def history_entry(
    letter: str,
    tone: str,
    name: str,
    status: str,
    date: str,
    text: str,
    with_children: bool = False,
    with_image: bool = False,
) -> str:
    image_part = (
        "<div class='history-entry__image'><div class='image-art image-art--thumb'>"
        "<div class='image-art__sky'></div><div class='image-art__mountain image-art__mountain--back'></div>"
        "<div class='image-art__mountain image-art__mountain--front'></div><div class='image-art__sun'></div></div></div>"
        if with_image
        else ""
    )
    children = ""
    toggle = "<a class='history-entry__toggle' href='#'>Показать 2 комментария ветки</a>"
    if with_children:
        children = (
            "<div class='history-entry__children'>"
            f"{comment_item('С', 'violet', 'Сергей Иванов', '29.10.25 в 13:35', '@sergei заменить картинку', with_menu=False)}"
            f"{comment_item('А', 'yellow', 'Антон Серганов', '29.10.25 в 13:36', 'Мое предложение вообще ничего не делать. Потому что лень.', with_menu=False)}"
            "</div>"
        )
        toggle = "<a class='history-entry__toggle' href='#'>Скрыть ветку</a>"
    return (
        "<div class='history-entry'>"
        f"{avatar(letter, tone)}<div class='history-entry__body'><div class='history-entry__top'>"
        f"<div class='history-entry__name'>{escape(name)}</div><div class='history-entry__status'>{escape(status)} {escape(date)}</div>"
        f"</div><div class='history-entry__quote'>Этот текст тяжело воспринимать. Давайте сделаем его проще и понятнее для читателя.</div>"
        f"<div class='history-entry__text'>{escape(text)}</div>{image_part}{toggle}{children}</div></div>"
    )


def history_modal(error: bool = False, expanded: bool = False) -> str:
    if error:
        content = "<div class='history-empty'><div>Не удалось загрузить комментарии. Попробуйте еще раз</div>" + modal_button("Загрузить повторно", primary=True) + "</div>"
    else:
        content = (
            "<div class='history-list'>"
            f"{history_entry('И', 'blue', 'Иван Иванов', 'Удален', '29.10.25 в 13:32', 'Этот текст тяжело воспринимать. Давайте сделаем его проще и понятнее для читателя.')}"
            f"{history_entry('С', 'violet', 'Сергей Иванов', 'Решена', '29.10.25 в 13:34', '@sergei заменить картинку', with_children=expanded, with_image=True)}"
            "</div><div class='pagination'><span class='pagination__item is-active'>1</span><span class='pagination__item'>2</span>"
            "<span class='pagination__item'>3</span><span class='pagination__dots'>…</span><span class='pagination__item'>10</span>"
            f"<span class='pagination__item pagination__item--icon'>{icon('redo')}</span></div>"
        )
    return (
        "<div class='editor-card editor-card--modal-demo'>"
        f"{editor_header('Страница для комментирования', 'Добавить описание', top_links('comments'))}{toolbar(active='quote')}"
        "<div class='editor-card__body editor-card__body--dim'></div>"
        "<div class='modal modal--center modal--history'><div class='modal__head'><div><div class='modal__title'>История комментариев</div>"
        "<div class='modal__subtitle'>Отображаются удаленные или решенные ветки</div></div>"
        f"<button class='icon-btn' type='button'>{icon('close')}</button></div>{content}</div></div>"
    )


def time_machine_panel() -> str:
    entries = [
        ("Действие", "2025-11-14 15:53:57", "Константин Иванов"),
        ("Изменение текста", "2025-11-14 15:48:31", "Мария Сергеева"),
        ("Добавление комментария", "2025-11-14 15:42:10", "Иван Иванов"),
        ("Загрузка изображения", "2025-11-14 15:37:02", "Сергей Иванов"),
    ]
    items = "".join(
        "<div class='time-entry{active}'><div class='time-entry__top'>"
        f"<div class='time-entry__title'>{escape(title)}</div>"
        f"<div class='time-entry__author'>{escape(author)} {icon('square', 'time-entry__status')}</div>"
        f"</div><div class='time-entry__date'>{escape(date)}</div></div>".format(active=" is-active" if index == 1 else "")
        for index, (title, date, author) in enumerate(entries)
    )
    return f"<aside class='time-machine'><div class='time-machine__head'><div class='time-machine__title'>Машина времени</div><button class='icon-btn' type='button'>{icon('close')}</button></div>{items}</aside>"


def time_machine_page() -> str:
    body = (
        "<div class='doc-with-comments'><div class='doc-area doc-area--content'>"
        "<h1 class='doc-title'>Страница для комментирования</h1>"
        "<p class='doc-paragraph'>Порой кажется, что наша жизнь — это бесконечное плавание против течения, в мутной воде повседневных забот.</p>"
        "<p class='doc-paragraph'>Мы, как упрямые лососи, стремимся к своим целям, преодолевая пороги трудностей и обходя сети сомнений.</p>"
        "<p class='doc-paragraph'>Но стоит лишь на мгновение остановиться и прислушаться к тихому плеску мыслей, как становится ясно: каждый из нас — это целый океан возможностей.</p>"
        f"</div>{time_machine_panel()}</div>"
    )
    return f"<div class='editor-card'>{editor_header('Страница для комментирования', 'Добавить описание', top_links('time'))}{toolbar(active='bold')}<div class='editor-card__body'>{body}</div></div>"


def styles() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root { --canvas:#434347; --paper:#fff; --panel:#f7f7fb; --line:#e6e8ef; --line-strong:#d8dbe6; --ink:#121318; --muted:#9195a3; --muted-strong:#6f7485; --accent:#8f7cff; --accent-soft:#f2efff; --accent-deep:#6f5cff; --danger:#ff4f8b; --danger-soft:#fff0f5; --blue:#46a6ff; --shadow:0 18px 44px rgba(12,16,33,.12); --shadow-soft:0 10px 24px rgba(12,16,33,.08); }
    * { box-sizing:border-box; } .prototype { background:radial-gradient(circle at top right, rgba(143,124,255,.12), transparent 18%), radial-gradient(circle at bottom left, rgba(70,166,255,.08), transparent 24%), var(--canvas); color:var(--ink); min-height:100vh; padding:28px 24px 64px; font-family:'Inter',sans-serif; }
    .prototype__layout { display:grid; grid-template-columns:272px minmax(0,1fr); gap:28px; align-items:start; max-width:1800px; margin:0 auto; }
    .side-nav { position:sticky; top:24px; padding:22px 18px; border-radius:18px; background:rgba(26,27,31,.28); border:1px solid rgba(255,255,255,.08); box-shadow:inset 0 1px 0 rgba(255,255,255,.04); }
    .side-nav__title { color:rgba(255,255,255,.92); font-size:14px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; margin-bottom:18px; }
    .side-nav__list { display:flex; flex-direction:column; gap:12px; }
    .side-nav__item { display:flex; align-items:center; gap:12px; min-height:42px; padding:9px 10px; border-radius:12px; color:#fff; text-decoration:none; font-size:18px; font-weight:600; letter-spacing:-.01em; transition:background .16s ease, transform .16s ease; opacity:.94; }
    .side-nav__item:hover { background:rgba(255,255,255,.06); transform:translateX(2px); } .side-nav__item .ui-icon { width:18px; height:18px; color:rgba(255,255,255,.88); flex:none; }
    .prototype__main { display:flex; flex-direction:column; gap:42px; } .scene { position:relative; padding-top:12px; } .scene--accent .scene__body { border:1px solid rgba(70,166,255,.95); box-shadow:0 0 0 1px rgba(70,166,255,.15); }
    .scene-label { display:inline-flex; align-items:center; min-height:30px; padding:0 12px; border-radius:10px; background:#2e2f33; color:#fff; font-size:13px; font-weight:700; margin-bottom:14px; }
    .scene__body { display:flex; flex-direction:column; gap:18px; padding:18px; border-radius:18px; background:rgba(255,255,255,.04); }
    .frames { display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:18px; } .frame--wide { grid-column:1/-1; } .frame__title { color:rgba(255,255,255,.86); font-size:13px; font-weight:600; margin-bottom:10px; }
    .frame__viewport { position:relative; min-height:180px; padding:22px; border-radius:18px; background:linear-gradient(180deg, #4a4a4f 0%, #404045 100%); box-shadow:inset 0 1px 0 rgba(255,255,255,.04); overflow:hidden; }
    .editor-card { position:relative; border-radius:16px; background:var(--paper); box-shadow:var(--shadow); border:1px solid rgba(228,231,239,.95); overflow:hidden; } .editor-card--viewer { padding-bottom:66px; } .editor-card--modal-demo { min-height:630px; }
    .editor-head { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; padding:22px 24px 14px; } .editor-head__main { display:flex; align-items:flex-start; gap:12px; } .doc-icon { width:20px; height:20px; color:#6f7485; margin-top:2px; flex:none; }
    .editor-head__title { font-size:22px; font-weight:800; line-height:1.15; letter-spacing:-.03em; color:var(--ink); } .editor-head__description { margin-top:6px; font-size:13px; color:var(--muted); }
    .top-links { display:flex; align-items:center; gap:14px; padding-top:4px; } .top-link { color:var(--muted-strong); text-decoration:none; font-size:14px; font-weight:600; } .top-link.is-active { color:var(--accent); }
    .editor-toolbar { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 18px; background:var(--panel); border-top:1px solid var(--line); border-bottom:1px solid var(--line); flex-wrap:wrap; } .editor-toolbar__group { display:flex; flex-wrap:wrap; gap:8px; }
    .tool-btn,.icon-btn,.modal-btn,.viewer-banner__action,.viewer-banner__close { appearance:none; border:1px solid transparent; background:transparent; cursor:default; transition:background .16s ease, border-color .16s ease, color .16s ease, box-shadow .16s ease; font-family:inherit; }
    .tool-btn { display:inline-flex; align-items:center; justify-content:center; gap:6px; min-width:30px; height:30px; padding:0 10px; border-radius:10px; background:#f0f1f6; color:#646a79; } .tool-btn--text { font-size:12px; font-weight:700; }
    .tool-btn:hover,.tool-btn.is-active { background:#fff; border-color:rgba(255,79,139,.55); color:#2d3140; box-shadow:0 4px 12px rgba(255,79,139,.12); }
    .tool-btn__icon,.icon-btn .ui-icon,.comment-badge .ui-icon,.small-dropdown__item .ui-icon,.paragraph-comment-anchor__icon .ui-icon,.dropzone .ui-icon,.image-float-toolbar .ui-icon,.time-entry__status,.viewer-banner__close .ui-icon { width:15px; height:15px; flex:none; }
    .editor-card__body { position:relative; min-height:420px; padding:28px 32px 36px; } .editor-card__body--skeleton { display:flex; flex-direction:column; justify-content:center; gap:16px; min-height:460px; max-width:640px; margin:0 auto; } .editor-card__body--dim { min-height:480px; background:linear-gradient(180deg, rgba(248,249,252,.82), rgba(248,249,252,.92)); } .editor-card__body--compact { min-height:260px; }
    .skeleton { height:16px; border-radius:999px; background:linear-gradient(90deg, #eff1f5 0%, #e7eaf2 50%, #eff1f5 100%); } .skeleton--short { width:30%; } .skeleton--mid { width:72%; } .skeleton--wide { width:86%; }
    .doc-area { position:relative; min-height:360px; max-width:820px; margin:0 auto; } .doc-area--airy { display:flex; flex-direction:column; align-items:flex-start; justify-content:center; min-height:430px; padding-top:24px; }
    .focus-title { min-width:420px; padding:14px 18px; border-radius:14px; border:2px solid rgba(143,124,255,.45); box-shadow:0 0 0 4px rgba(143,124,255,.12); color:var(--ink); font-size:42px; font-weight:800; line-height:1.05; letter-spacing:-.04em; } .focus-hint { margin-top:18px; font-size:14px; color:var(--muted); }
    .doc-title { margin:0 0 10px; font-size:42px; font-weight:800; line-height:1.05; letter-spacing:-.04em; color:var(--ink); } .doc-description { margin:0 0 20px; font-size:15px; line-height:1.75; color:#63697c; max-width:680px; }
    .doc-subtitle { margin:18px 0 10px; font-size:20px; font-weight:800; letter-spacing:-.02em; color:var(--ink); } .doc-paragraph { margin:0 0 16px; color:#272c37; line-height:1.9; font-size:15px; }
    .doc-typed { color:var(--muted-strong); } .command-menu { position:absolute; top:182px; left:0; width:236px; padding:10px; border-radius:14px; background:#fff; border:1px solid var(--line); box-shadow:var(--shadow-soft); }
    .command-menu__item { display:flex; align-items:center; gap:10px; min-height:36px; padding:8px 10px; border-radius:10px; color:#2a2f39; font-size:13px; font-weight:600; } .command-menu__item.is-hovered,.command-menu__item:hover { background:#f4f5f8; }
    .selected-span { background:rgba(70,166,255,.32); border-radius:4px; padding:0 1px; } .floating-toolbar-wrap { position:absolute; top:110px; left:210px; display:flex; flex-direction:column; align-items:center; gap:8px; }
    .floating-toolbar,.mini-dropdown { display:flex; align-items:center; gap:8px; padding:8px; border-radius:14px; background:#fff; border:1px solid var(--line); box-shadow:var(--shadow-soft); }
    .black-tooltip { display:inline-flex; align-items:center; justify-content:center; min-height:30px; padding:0 12px; border-radius:10px; background:#1c1d22; color:#fff; font-size:12px; font-weight:600; } .black-tooltip--inline { margin-left:8px; } .black-tooltip--side { position:absolute; left:calc(100% + 8px); top:50%; transform:translateY(-50%); white-space:nowrap; }
    .modal { position:absolute; background:#fff; border:1px solid var(--line); border-radius:14px; box-shadow:var(--shadow); padding:18px; } .modal--center { top:52%; left:50%; transform:translate(-50%, -50%); width:430px; } .modal--wide { width:500px; } .modal--history { width:760px; max-width:calc(100% - 64px); }
    .modal__head { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px; } .modal__title { font-size:20px; font-weight:800; letter-spacing:-.03em; } .modal__subtitle { margin-top:4px; color:var(--muted); font-size:13px; }
    .form-field { display:block; margin-bottom:12px; } .form-field__label { display:block; margin-bottom:7px; color:var(--muted-strong); font-size:13px; font-weight:600; } .form-field__input { display:flex; align-items:center; min-height:44px; padding:0 14px; border-radius:12px; border:1px solid var(--line); color:var(--ink); font-size:14px; background:#fff; } .field__placeholder { color:var(--muted); }
    .check-row,.radio-row { display:flex; align-items:center; gap:10px; min-height:34px; color:#2d3340; font-size:14px; } .check-row__box,.radio-row__dot { width:18px; height:18px; border-radius:5px; border:1px solid var(--line-strong); background:#fff; position:relative; flex:none; } .radio-row__dot { border-radius:999px; }
    .check-row__box.is-checked::after,.radio-row__dot.is-active::after { content:""; position:absolute; inset:3px; border-radius:inherit; background:var(--accent); }
    .modal__actions { display:flex; gap:10px; margin-top:16px; } .modal-btn { min-width:124px; height:42px; padding:0 18px; border-radius:12px; background:#f1f2f6; color:#2d3340; font-size:14px; font-weight:700; } .modal-btn--primary { background:var(--danger); color:#fff; box-shadow:0 10px 20px rgba(255,79,139,.2); } .modal-btn.is-disabled { background:#f3f4f7; color:#b8bcc7; box-shadow:none; }
    .dropzone__label { margin-bottom:10px; color:var(--muted-strong); font-size:13px; font-weight:600; } .dropzone__box { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; min-height:180px; padding:22px; border-radius:14px; border:1px dashed #cfd5e4; background:#fbfcfe; text-align:center; }
    .dropzone__line { display:flex; gap:5px; flex-wrap:wrap; justify-content:center; font-size:14px; color:var(--muted); } .dropzone__line a { color:#4c8fff; text-decoration:none; font-weight:600; } .dropzone__hint { color:var(--muted); font-size:12px; }
    .upload-preview { display:grid; grid-template-columns:56px minmax(0,1fr) auto; gap:12px; align-items:center; margin-top:14px; padding:10px; border-radius:12px; background:#fafbfe; border:1px solid var(--line); } .upload-preview__thumb { width:56px; height:56px; border-radius:10px; overflow:hidden; }
    .upload-preview__name { font-size:14px; font-weight:700; color:#1f2430; } .upload-preview__status { margin-top:4px; color:var(--muted); font-size:12px; } .upload-preview__status.is-error { color:var(--danger); font-weight:600; } .upload-preview__retry { display:inline-block; margin-top:5px; color:#4c8fff; font-size:12px; font-weight:600; text-decoration:none; } .upload-preview__size { color:var(--muted-strong); font-size:13px; font-weight:600; }
    .alert { margin-bottom:12px; padding:10px 12px; border-radius:12px; background:var(--danger-soft); color:#d53f6f; font-size:13px; font-weight:600; }
    .image-block { position:relative; margin-top:18px; border-radius:14px; border:1px solid transparent; overflow:visible; } .image-block--compact { margin-top:0; } .image-block.is-selected { border-color:rgba(255,79,139,.95); box-shadow:0 0 0 2px rgba(255,79,139,.12); }
    .image-art { position:relative; height:250px; border-radius:12px; overflow:hidden; background:linear-gradient(180deg, #d7e8ff 0%, #f5f6fd 100%); } .image-block--compact .image-art { height:120px; } .image-art--thumb { height:100%; border-radius:0; }
    .image-art__sky,.image-art__mountain,.image-art__sun { position:absolute; } .image-art__sky { inset:0; background:linear-gradient(180deg, #dbe6ff 0%, #f8fbff 100%); } .image-art__mountain--back { left:-5%; right:-5%; bottom:16%; height:48%; background:linear-gradient(180deg, #b6c4ea 0%, #91a4d5 100%); clip-path:polygon(0 100%, 20% 44%, 35% 72%, 48% 36%, 64% 67%, 79% 40%, 100% 100%); } .image-art__mountain--front { left:-5%; right:-5%; bottom:0; height:56%; background:linear-gradient(180deg, #7d8fbe 0%, #5c709e 100%); clip-path:polygon(0 100%, 13% 60%, 26% 78%, 40% 34%, 55% 64%, 71% 26%, 86% 70%, 100% 100%); } .image-art__sun { width:70px; height:70px; top:22px; right:24px; border-radius:999px; background:radial-gradient(circle, #fff3b0 0%, #ffd77e 48%, rgba(255,215,126,0) 70%); opacity:.95; }
    .resize-handle { position:absolute; width:11px; height:11px; border-radius:999px; background:#fff; border:2px solid var(--danger); } .resize-handle--tl { top:-6px; left:-6px; } .resize-handle--tr { top:-6px; right:-6px; } .resize-handle--bl { bottom:-6px; left:-6px; } .resize-handle--br { bottom:-6px; right:-6px; } .resize-handle--tm { top:-6px; left:calc(50% - 5px); } .resize-handle--bm { bottom:-6px; left:calc(50% - 5px); } .resize-handle--ml { left:-6px; top:calc(50% - 5px); } .resize-handle--mr { right:-6px; top:calc(50% - 5px); }
    .image-float-toolbar { position:absolute; top:14px; left:14px; display:inline-flex; align-items:center; gap:10px; min-height:36px; padding:0 12px; border-radius:999px; background:rgba(255,255,255,.95); border:1px solid var(--line); box-shadow:var(--shadow-soft); color:#5e6576; font-size:12px; font-weight:600; } .image-float-toolbar__pill { display:inline-flex; align-items:center; justify-content:center; min-width:52px; height:24px; padding:0 10px; border-radius:999px; background:#f1f2f7; } .image-float-toolbar__pill.is-active { background:var(--accent-soft); color:var(--accent-deep); }
    .image-pair { display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:16px; margin-top:18px; } .doc-with-comments { display:grid; grid-template-columns:minmax(0,1fr) 320px; gap:26px; align-items:start; }
    .paragraph-comment-anchor { position:relative; padding-right:72px; } .paragraph-comment-anchor__rail { position:absolute; top:12px; right:24px; width:2px; height:calc(100% - 24px); background:var(--accent); border-radius:999px; } .paragraph-comment-anchor__icon { position:absolute; top:16px; right:0; display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:10px; background:#f6f1ff; color:var(--accent); }
    .comment-badge-wrap { position:absolute; top:8px; right:38px; } .comment-badge { display:inline-flex; align-items:center; gap:6px; min-height:28px; padding:0 10px; border-radius:999px; background:var(--accent); color:#fff; font-size:12px; font-weight:700; box-shadow:0 8px 18px rgba(143,124,255,.22); }
    .comment-panel,.time-machine { border-radius:14px; border:1px solid var(--line); background:#fbfbfe; box-shadow:var(--shadow-soft); overflow:hidden; } .comment-panel { display:flex; flex-direction:column; min-height:520px; }
    .comment-panel__head,.time-machine__head { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:16px 16px 12px; border-bottom:1px solid var(--line); background:#fff; } .comment-panel__title,.time-machine__title { font-size:16px; font-weight:800; letter-spacing:-.02em; }
    .comment-panel__head-actions { display:flex; align-items:center; gap:8px; } .resolved-pill { display:inline-flex; align-items:center; height:24px; padding:0 10px; border-radius:999px; background:var(--accent-soft); color:var(--accent-deep); font-size:12px; font-weight:700; }
    .comment-panel__context { padding:10px 16px 12px; border-bottom:1px solid var(--line); font-size:12px; color:var(--muted); line-height:1.55; } .comment-panel__content { flex:1; min-height:220px; max-height:340px; overflow:auto; padding:6px 0; } .comment-panel__footer { position:relative; border-top:1px solid var(--line); padding:12px 16px 16px; background:#fff; }
    .comment-input { display:flex; align-items:center; justify-content:space-between; gap:12px; min-height:44px; padding:0 8px 0 14px; border-radius:12px; border:1px solid var(--line); color:var(--muted); font-size:14px; background:#fff; } .icon-btn { display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:10px; color:#6a7080; } .icon-btn--soft { background:#f2f3f7; } .icon-btn--accent { background:var(--accent-soft); color:var(--accent); } .icon-btn:hover { background:#f0f2f8; color:#313646; }
    .comment-list { display:flex; flex-direction:column; } .comment-item { display:grid; grid-template-columns:32px minmax(0,1fr); gap:12px; padding:14px 16px; border-bottom:1px solid #eceef5; } .comment-item.is-highlighted { background:rgba(143,124,255,.06); }
    .comment-item__top { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; } .comment-item__name,.history-entry__name { font-size:14px; font-weight:700; color:#232733; } .comment-item__date,.mention-row__login,.time-entry__date { margin-top:2px; font-size:12px; color:var(--muted); }
    .comment-item__text,.history-entry__text { margin-top:8px; font-size:13px; line-height:1.7; color:#2d3340; } .comment-item__actions { display:flex; align-items:center; gap:2px; } .comment-item__count { color:var(--accent); font-size:12px; font-weight:700; margin-right:2px; }
    .comment-editor-inline { margin-top:10px; } .comment-editor-inline__field { min-height:72px; padding:12px 14px; border-radius:12px; border:1px solid var(--line); background:#fff; color:#2d3340; font-size:13px; line-height:1.6; } .comment-editor-inline .modal-btn { margin-top:10px; min-width:110px; }
    .reply-chip { display:inline-flex; align-items:center; gap:8px; margin-bottom:10px; min-height:30px; padding:0 10px; border-radius:999px; background:#f3f0ff; color:var(--accent-deep); font-size:12px; font-weight:600; } .reply-chip button { border:none; background:transparent; color:inherit; font-size:14px; }
    .mention-list { margin-top:10px; border-radius:12px; border:1px solid var(--line); background:#fff; box-shadow:var(--shadow-soft); overflow:hidden; } .mention-row { display:flex; align-items:center; gap:10px; padding:10px 12px; border-bottom:1px solid #eef0f5; } .mention-row:last-child { border-bottom:none; } .mention-row__name { font-size:13px; font-weight:700; color:#242936; } .mention-list__more { padding:10px 12px; color:var(--muted-strong); font-size:13px; font-weight:600; background:#fafbfe; }
    .panel-empty { display:flex; align-items:center; justify-content:center; min-height:180px; color:var(--muted); font-size:14px; } .panel-empty--loader .loader-icon { width:28px; height:28px; color:var(--accent); } .panel-empty--text { flex-direction:column; gap:12px; padding:24px; text-align:center; color:#4a5162; }
    .mini-cards,.panel-state-grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:14px; } .panel-state-grid { grid-template-columns:repeat(2, minmax(0,1fr)); } .mini-card,.panel-state { padding:14px; border-radius:14px; background:#fff; border:1px solid rgba(231,234,242,.95); box-shadow:var(--shadow-soft); min-width:0; } .mini-card__title { margin-bottom:12px; font-size:13px; font-weight:700; color:#2c3240; } .mini-card__row { position:relative; display:flex; align-items:center; }
    .small-dropdown,.popup { position:absolute; right:24px; top:78px; width:240px; padding:10px; border-radius:14px; background:#fff; border:1px solid var(--line); box-shadow:var(--shadow); } .small-dropdown__item { display:flex; align-items:center; gap:10px; min-height:38px; padding:8px 10px; border-radius:10px; color:#2b3040; font-size:13px; font-weight:600; } .small-dropdown__item.is-hovered,.small-dropdown__item:hover { background:#f5f6fa; }
    .popup__title { font-size:16px; font-weight:800; letter-spacing:-.02em; } .popup__text { margin:6px 0 12px; color:var(--muted); font-size:13px; line-height:1.6; }
    .history-list { display:flex; flex-direction:column; max-height:520px; overflow:auto; } .history-entry { display:grid; grid-template-columns:32px minmax(0,1fr); gap:12px; padding:14px 0; border-bottom:1px solid #eceef5; } .history-entry__top { display:flex; justify-content:space-between; gap:14px; align-items:flex-start; } .history-entry__status { color:var(--muted); font-size:12px; font-weight:600; }
    .history-entry__quote { margin-top:8px; padding:10px 12px; border-radius:10px; background:#f7f8fc; color:var(--muted); font-size:12px; line-height:1.5; } .history-entry__toggle { display:inline-block; margin-top:10px; color:var(--accent); font-size:13px; font-weight:600; text-decoration:none; } .history-entry__children { margin-top:12px; border-top:1px solid #eceef5; padding-top:8px; } .history-entry__image { margin-top:10px; width:132px; border-radius:10px; overflow:hidden; }
    .history-empty { display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:280px; gap:14px; color:#4a5162; text-align:center; } .pagination { display:flex; align-items:center; gap:8px; margin-top:16px; } .pagination__item { display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; padding:0 10px; border-radius:10px; border:1px solid transparent; color:#394050; font-size:13px; font-weight:700; } .pagination__item.is-active { border-color:var(--line-strong); background:#fff; } .pagination__item--icon .ui-icon { width:14px; height:14px; } .pagination__dots { color:var(--muted); font-size:13px; }
    .time-machine { min-height:500px; background:#f7f8fc; } .time-entry { padding:14px 16px; border-bottom:1px solid #e8ebf3; transition:background .16s ease, box-shadow .16s ease; } .time-entry:hover { background:rgba(255,255,255,.7); } .time-entry.is-active { background:#fff; box-shadow:inset 0 0 0 1px rgba(226,230,240,.9); }
    .time-entry__top { display:flex; justify-content:space-between; gap:12px; align-items:center; } .time-entry__title { font-size:14px; font-weight:700; color:#222733; } .time-entry__author { display:inline-flex; align-items:center; gap:8px; color:#4f5770; font-size:12px; font-weight:600; } .time-entry__status { width:14px; height:14px; color:#69a9ff; }
    .viewer-banner { position:absolute; left:22px; right:22px; bottom:18px; display:flex; align-items:center; justify-content:space-between; gap:14px; min-height:46px; padding:0 10px 0 14px; border-radius:12px; background:#ebf5ff; color:#376fa8; font-size:13px; font-weight:600; } .viewer-banner__action { height:32px; padding:0 12px; border-radius:10px; background:#d8ebff; color:#2d6bac; font-size:12px; font-weight:700; } .viewer-banner__close { width:30px; height:30px; border-radius:10px; color:#4c81b6; }
    .avatar { display:inline-flex; align-items:center; justify-content:center; width:32px; height:32px; border-radius:999px; color:#fff; font-size:14px; font-weight:700; } .avatar--blue { background:#69a9ff; } .avatar--violet { background:#8f7cff; } .avatar--yellow { background:#f3c352; }
    @media (max-width: 1320px) { .prototype__layout { grid-template-columns:1fr; } .side-nav { position:relative; top:0; } }
    @media (max-width: 980px) { .frames,.mini-cards,.panel-state-grid,.image-pair,.doc-with-comments { grid-template-columns:1fr; } .frame__viewport,.scene__body { padding:16px; } .editor-card__body { padding:24px 20px 28px; } .modal--history,.modal--wide,.modal--center { position:relative; top:auto; left:auto; transform:none; width:auto; margin:24px; } }
    </style>
    """


def render_prototype() -> None:
    nav_html = "".join(nav_item(section_id, title) for section_id, title in SECTIONS)
    loading_group = surface("<div class='frames'>" + frame("2. Загрузка страницы", skeleton_page(), wide=True) + "</div>", section_id="page-loading", title="Загрузка страницы")
    basics_group = surface("<div class='frames'>" + frame("3.1. Пустая новая страница", empty_page()) + frame("3.2. Страница с контентом и slash menu", content_page()) + frame("3.3. Выбор типа заголовка", heading_picker_page()) + frame("3.4. Верхний тулбар редактора", toolbar_showcase()) + frame("3.5. Выделение текста", selection_page()) + "</div>", accent=True, section_id="page-basics", title="Базовое взаимодействие со страницей")
    link_group = surface("<div class='frames'>" + frame("5.1. Плавающий mini-toolbar над выделенным текстом", link_inline_state()) + frame("5.2. Popup добавления ссылки", link_modal()) + frame("Состояние disabled primary", link_modal(primary_disabled=True), wide=True) + "</div>", section_id="link", title="Ссылка")
    image_group = surface("<div class='frames'>" + frame("7.1. Пустой modal вставки изображения", image_modal('empty')) + frame("7.2. Выбранный файл", image_modal('selected')) + frame("7.3. Ошибка загрузки", image_modal('upload-error')) + frame("7.4. Ошибка формата", image_modal('format-error')) + frame("7.5. Изображение вставлено в документ", inserted_image_page(), wide=True) + "</div>", accent=True, section_id="image", title="Изображение")
    comments_group = surface("<div class='frames'>" + frame("9.1. Страница с комментариями", comment_page(), wide=True) + frame("9.2. Кнопка комментариев и бейдж", comment_controls_showcase(), wide=True) + frame("9.3–9.9. Состояния правой панели комментариев", comment_panel_states(), wide=True) + "</div>", accent=True, section_id="comments", title="Комментирование")
    access_group = surface("<div class='frames'>" + frame("12.1. Dropdown from top-right", access_dropdown()) + frame("12.2. Popup настройки доступа", access_popup()) + "</div>", section_id="comment-access", title="Управление доступом к комментариям")
    history_group = surface("<div class='frames'>" + frame("13.1. Основное модальное окно", history_modal()) + frame("13.2. Развернутая ветка", history_modal(expanded=True)) + frame("13.4. Ошибка загрузки истории", history_modal(error=True), wide=True) + "</div>", accent=True, section_id="comment-history", title="История комментариев")
    time_machine_group = surface("<div class='frames'>" + frame("15. Режим машины времени", time_machine_page(), wide=True) + "</div>", accent=True, section_id="time-machine", title="Машина времени")
    html = (
        styles()
        + "<div class='prototype'><div class='prototype__layout'><aside class='side-nav'><div class='side-nav__title'>Список разделов</div><div class='side-nav__list'>"
        + nav_html
        + "</div></aside><main class='prototype__main'>"
        + time_machine_group
        + history_group
        + access_group
        + comments_group
        + image_group
        + link_group
        + basics_group
        + loading_group
        + "</main></div></div>"
    )
    st.markdown(html, unsafe_allow_html=True)
