from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re
from typing import Any, Iterable


FORMULA_PATTERN = re.compile(r"\{\{([^:}]+):([^:}]+):([^}]+)\}\}")
TABLE_SEPARATOR_CELL_PATTERN = re.compile(r"^:?-{3,}:?$")


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
            <div class="doc-empty-state__text">Начни писать текст.</div>
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

    def is_table_line(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("|") and stripped.endswith("|") and "|" in stripped[1:-1]

    def parse_table_cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip()[1:-1].split("|")]

    def is_table_separator(line: str) -> bool:
        cells = parse_table_cells(line)
        return bool(cells) and all(TABLE_SEPARATOR_CELL_PATTERN.match(cell) for cell in cells)

    def render_table_block(header_cells: list[str], body_rows: list[list[str]]) -> str:
        header_html = "".join(
            f'<th style="padding:0.72rem 0.8rem;text-align:left;border-bottom:1px solid rgba(20,23,28,0.08);background:rgba(227,6,19,0.05);">{replace_formulas(cell)}</th>'
            for cell in header_cells
        )
        body_html = []
        for row in body_rows:
            cells_html = "".join(
                f'<td style="padding:0.72rem 0.8rem;border-bottom:1px solid rgba(20,23,28,0.06);vertical-align:top;">{replace_formulas(cell)}</td>'
                for cell in row
            )
            body_html.append(f"<tr>{cells_html}</tr>")
        return (
            '<div class="doc-table-wrap" style="overflow:auto;margin:0.85rem 0;border:1px solid rgba(20,23,28,0.08);border-radius:18px;background:#fff;">'
            '<table class="doc-table" style="width:100%;border-collapse:collapse;font-size:0.97rem;">'
            f"<thead><tr>{header_html}</tr></thead>"
            f"<tbody>{''.join(body_html)}</tbody>"
            "</table></div>"
        )

    lines = content.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            index += 1
            continue

        if (
            is_table_line(stripped)
            and index + 1 < len(lines)
            and is_table_line(lines[index + 1].strip())
            and is_table_separator(lines[index + 1].strip())
        ):
            flush_paragraph()
            header_cells = parse_table_cells(stripped)
            body_rows: list[list[str]] = []
            index += 2
            while index < len(lines):
                candidate = lines[index].rstrip()
                candidate_stripped = candidate.strip()
                if not is_table_line(candidate_stripped):
                    break
                row_cells = parse_table_cells(candidate_stripped)
                if len(row_cells) != len(header_cells):
                    break
                body_rows.append(row_cells)
                index += 1
            blocks.append(render_table_block(header_cells, body_rows))
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            blocks.append(
                f'<h2 class="doc-heading">{replace_formulas(stripped[3:])}</h2>'
            )
            index += 1
            continue

        if stripped == "---":
            flush_paragraph()
            blocks.append('<div class="doc-divider"></div>')
            index += 1
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            blocks.append(
                '<div class="doc-callout">'
                f"{replace_formulas(stripped[2:])}"
                "</div>"
            )
            index += 1
            continue

        paragraph_parts.append(replace_formulas(line))
        index += 1

    flush_paragraph()
    return "".join(blocks)
