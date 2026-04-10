from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re
from typing import Any, Iterable


FORMULA_PATTERN = re.compile(r"\{\{([^:}]+):([^:}]+):([^}]+)\}\}")


@dataclass(slots=True)
class FormulaToken:
    index: int
    raw: str
    table_id: str
    record_id: str
    field_name: str


def build_formula_token(table_id: str, record_id: str, field_name: str) -> str:
    return f"{{{{{table_id}:{record_id}:{field_name}}}}}"


def extract_formula_tokens(content: str) -> list[FormulaToken]:
    tokens: list[FormulaToken] = []
    for index, match in enumerate(FORMULA_PATTERN.finditer(content)):
        table_id, record_id, field_name = match.groups()
        tokens.append(
            FormulaToken(
                index=index,
                raw=match.group(0),
                table_id=table_id,
                record_id=record_id,
                field_name=field_name,
            )
        )
    return tokens


def replace_formula_token(content: str, token_index: int, replacement: str) -> str:
    current_index = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal current_index
        if current_index == token_index:
            current_index += 1
            return replacement

        current_index += 1
        return match.group(0)

    return FORMULA_PATTERN.sub(replacer, content)


def count_words(content: str) -> int:
    return len([part for part in re.split(r"\s+", content.strip()) if part])


def _iter_insert_option_sets(insert_options: Any) -> Iterable[dict[str, Any]]:
    if not insert_options:
        return []
    if isinstance(insert_options, dict) and "records" in insert_options:
        return [insert_options]
    if isinstance(insert_options, dict):
        return [
            value
            for value in insert_options.values()
            if isinstance(value, dict) and "records" in value
        ]
    if isinstance(insert_options, list):
        return [value for value in insert_options if isinstance(value, dict) and "records" in value]
    return []


def _insert_lookup(insert_options: Any) -> dict[tuple[str, str, str], str]:
    lookup: dict[tuple[str, str, str], str] = {}
    for option_set in _iter_insert_option_sets(insert_options):
        table_id = option_set.get("tableId", "")
        for record in option_set.get("records", []):
            record_id = record.get("recordId", "")
            fields = record.get("fields", {})
            for field_name, value in fields.items():
                lookup[(table_id, record_id, field_name)] = str(value)
    return lookup


def describe_formula(token: FormulaToken, insert_options: Any) -> tuple[str, str]:
    lookup = _insert_lookup(insert_options)
    preview_value = lookup.get((token.table_id, token.record_id, token.field_name))

    if preview_value:
        return token.field_name, preview_value

    return token.field_name, "живое поле"


def _render_inline_formula(
    token: FormulaToken,
    insert_options: Any,
) -> str:
    label, preview_value = describe_formula(token, insert_options)
    return (
        '<span class="doc-formula-chip" '
        f'title="{escape(token.raw)}">'
        f'<span class="doc-formula-chip__index">#{token.index + 1}</span>'
        f'<span class="doc-formula-chip__label">{escape(label)}</span>'
        f'<span class="doc-formula-chip__value">{escape(preview_value)}</span>'
        "</span>"
    )


def render_document_html(content: str, insert_options: Any = None) -> str:
    if not content.strip():
        return """
        <div class="doc-empty-state">
            <div class="doc-empty-state__title">Лист пока пуст</div>
            <div class="doc-empty-state__text">
                Начни писать текст, а живые поля MWS можно вставлять через конструктор справа.
            </div>
        </div>
        """

    token_cursor = 0

    def replace_formulas(line: str) -> str:
        nonlocal token_cursor

        parts: list[str] = []
        last_end = 0
        for match in FORMULA_PATTERN.finditer(line):
            parts.append(escape(line[last_end:match.start()]))
            groups = match.groups()
            token = FormulaToken(
                index=token_cursor,
                raw=match.group(0),
                table_id=groups[0],
                record_id=groups[1],
                field_name=groups[2],
            )
            parts.append(_render_inline_formula(token, insert_options))
            token_cursor += 1
            last_end = match.end()

        parts.append(escape(line[last_end:]))
        return "".join(parts)

    blocks: list[str] = []
    paragraph_parts: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_parts:
            return

        blocks.append(
            f'<p class="doc-paragraph">{"<br/>".join(paragraph_parts)}</p>'
        )
        paragraph_parts.clear()

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            blocks.append(
                f'<h2 class="doc-heading">{replace_formulas(stripped[3:])}</h2>'
            )
            continue

        if stripped == "---":
            flush_paragraph()
            blocks.append('<div class="doc-divider"></div>')
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            blocks.append(
                '<div class="doc-callout">'
                f"{replace_formulas(stripped[2:])}"
                "</div>"
            )
            continue

        paragraph_parts.append(replace_formulas(line))

    flush_paragraph()
    return "".join(blocks)
