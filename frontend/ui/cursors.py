from __future__ import annotations

from urllib.parse import quote


def _svg_cursor(svg: str, hot_x: int, hot_y: int) -> str:
    compact = " ".join(part.strip() for part in svg.strip().splitlines())
    return f'url("data:image/svg+xml,{quote(compact, safe="")}") {hot_x} {hot_y}, auto'


_CURSOR_MAP: dict[str, tuple[str, int, int]] = {
    "default": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <path d='M6 4.5V22.5L11.7 17.2L15.8 24C16.2 24.6 17 24.8 17.7 24.4L19.5 23.3C20.1 22.9 20.3 22.1 19.9 21.5L15.9 14.9H23.1L6 4.5Z'
                fill='#E30613' stroke='white' stroke-width='1.8' stroke-linejoin='round'/>
        </svg>
        """,
        6,
        4,
    ),
    "pointer": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <circle cx='14' cy='14' r='8.5' fill='#E30613' stroke='white' stroke-width='2'/>
          <circle cx='14' cy='14' r='2.6' fill='white'/>
        </svg>
        """,
        14,
        14,
    ),
    "text": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <path d='M10 4H18M10 24H18M14 4V24' stroke='white' stroke-width='6' stroke-linecap='round'/>
          <path d='M10 4H18M10 24H18M14 4V24' stroke='#E30613' stroke-width='3' stroke-linecap='round'/>
        </svg>
        """,
        14,
        14,
    ),
    "grab": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <circle cx='14' cy='14' r='8.5' fill='#E30613' stroke='white' stroke-width='2'/>
          <circle cx='11' cy='11' r='1.5' fill='white'/>
          <circle cx='17' cy='11' r='1.5' fill='white'/>
          <circle cx='11' cy='17' r='1.5' fill='white'/>
          <circle cx='17' cy='17' r='1.5' fill='white'/>
        </svg>
        """,
        14,
        14,
    ),
    "grabbing": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <circle cx='14' cy='14' r='9' fill='#E30613' stroke='white' stroke-width='2'/>
          <path d='M10 11.5H18M10 16.5H18' stroke='white' stroke-width='2.4' stroke-linecap='round'/>
        </svg>
        """,
        14,
        14,
    ),
    "ew": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <path d='M7 14H21' stroke='white' stroke-width='6' stroke-linecap='round'/>
          <path d='M7 14H21' stroke='#E30613' stroke-width='3' stroke-linecap='round'/>
          <path d='M10 10L6 14L10 18M18 10L22 14L18 18' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M10 10L6 14L10 18M18 10L22 14L18 18' stroke='#E30613' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        14,
        14,
    ),
    "ns": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <path d='M14 7V21' stroke='white' stroke-width='6' stroke-linecap='round'/>
          <path d='M14 7V21' stroke='#E30613' stroke-width='3' stroke-linecap='round'/>
          <path d='M10 10L14 6L18 10M10 18L14 22L18 18' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M10 10L14 6L18 10M10 18L14 22L18 18' stroke='#E30613' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        14,
        14,
    ),
    "nwse": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <path d='M8 20L20 8' stroke='white' stroke-width='6' stroke-linecap='round'/>
          <path d='M8 20L20 8' stroke='#E30613' stroke-width='3' stroke-linecap='round'/>
          <path d='M9 9H20V20M19 19H8V8' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M9 9H20V20M19 19H8V8' stroke='#E30613' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        14,
        14,
    ),
    "nesw": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28' fill='none'>
          <path d='M8 8L20 20' stroke='white' stroke-width='6' stroke-linecap='round'/>
          <path d='M8 8L20 20' stroke='#E30613' stroke-width='3' stroke-linecap='round'/>
          <path d='M8 19V8H19M9 9H20V20' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M8 19V8H19M9 9H20V20' stroke='#E30613' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        14,
        14,
    ),
}


def cursor_root_variables(indent: str = "") -> str:
    lines = []
    for name, (svg, hot_x, hot_y) in _CURSOR_MAP.items():
        lines.append(f"{indent}--cursor-{name}: {_svg_cursor(svg, hot_x, hot_y)};")
    return "\n".join(lines)
