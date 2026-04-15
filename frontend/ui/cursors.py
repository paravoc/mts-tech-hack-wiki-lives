from __future__ import annotations

from urllib.parse import quote


def _svg_cursor(svg: str, hot_x: int, hot_y: int) -> str:
    compact = " ".join(part.strip() for part in svg.strip().splitlines())
    return f'url("data:image/svg+xml,{quote(compact, safe="")}") {hot_x} {hot_y}, auto'


_CURSOR_MAP: dict[str, tuple[str, int, int]] = {
    "default": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M4 2.5V15.5L7.8 12L10.6 17C10.9 17.5 11.6 17.7 12.1 17.4L13.1 16.8C13.6 16.5 13.7 15.8 13.4 15.3L10.7 10.8H15.8L4 2.5Z'
                fill='#E30613' stroke='white' stroke-width='1.3' stroke-linejoin='round'/>
        </svg>
        """,
        4,
        2,
    ),
    "pointer": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M10.1 2.6C8 2.6 6.3 4.1 6.3 6.2V9.1H5.5C4.6 9.1 3.9 9.8 3.9 10.7C3.9 11.2 4 11.6 4.3 11.9L8.2 16.7C8.8 17.5 9.7 18 10.8 18H12.1C13.6 18 14.9 17 15.3 15.6L16.1 12.9C16.2 12.6 16.3 12.2 16.3 11.8C16.3 10.9 15.6 10.1 14.6 10.1H14.5V6.3C14.5 5.5 13.9 4.9 13.1 4.9C12.7 4.9 12.4 5 12.1 5.3C11.8 4.5 11.2 4.1 10.4 4.1C10.2 4.1 10.2 4.1 10.1 4.1V2.6Z'
                fill='#E30613' stroke='white' stroke-width='1.2' stroke-linejoin='round'/>
          <path d='M8.7 6.2V11.1M10.7 5.5V10.8M12.6 6.1V10.6' stroke='white' stroke-width='1.1' stroke-linecap='round'/>
        </svg>
        """,
        9,
        3,
    ),
    "text": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M7 3.2H13M7 16.8H13M10 3.2V16.8' stroke='white' stroke-width='3.8' stroke-linecap='round'/>
          <path d='M7 3.2H13M7 16.8H13M10 3.2V16.8' stroke='#E30613' stroke-width='1.8' stroke-linecap='round'/>
        </svg>
        """,
        10,
        10,
    ),
    "grab": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M7.3 8.2V4.8C7.3 4.1 7.8 3.6 8.5 3.6C9.2 3.6 9.7 4.1 9.7 4.8V8.2M9.7 8V4C9.7 3.3 10.2 2.8 10.9 2.8C11.6 2.8 12.1 3.3 12.1 4V8.6M12.1 8.1V4.8C12.1 4.2 12.6 3.7 13.2 3.7C13.9 3.7 14.4 4.2 14.4 4.8V10.5M7.3 8.4V6.4C7.3 5.7 6.8 5.2 6.1 5.2C5.4 5.2 4.9 5.7 4.9 6.4V11C4.9 12 5.2 12.9 5.8 13.7L7.1 15.5C7.8 16.4 8.9 17 10.1 17H11.7C13.1 17 14.4 16 14.7 14.7L15.5 11.4'
                fill='#E30613' stroke='white' stroke-width='1.1' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        10,
        4,
    ),
    "grabbing": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M7.1 9.1V5.2C7.1 4.5 7.6 4 8.3 4C9 4 9.5 4.5 9.5 5.2V8.9M9.5 8.9V4.4C9.5 3.7 10 3.2 10.7 3.2C11.4 3.2 11.9 3.7 11.9 4.4V9.2M11.9 8.9V5.2C11.9 4.5 12.4 4 13.1 4C13.8 4 14.3 4.5 14.3 5.2V10.2M7.1 9.1L6 8C5.5 7.5 4.7 7.5 4.2 8C3.7 8.5 3.7 9.3 4.2 9.8L7 12.6C7.8 13.4 8.8 13.8 9.9 13.8H11.8C13.2 13.8 14.4 12.9 14.8 11.5L15.5 9.2'
                fill='#E30613' stroke='white' stroke-width='1.1' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        10,
        4,
    ),
    "ew": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M4.5 10H15.5' stroke='white' stroke-width='3.6' stroke-linecap='round'/>
          <path d='M4.5 10H15.5' stroke='#E30613' stroke-width='1.8' stroke-linecap='round'/>
          <path d='M7 7.2L4.2 10L7 12.8M13 7.2L15.8 10L13 12.8' stroke='white' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M7 7.2L4.2 10L7 12.8M13 7.2L15.8 10L13 12.8' stroke='#E30613' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        10,
        10,
    ),
    "ns": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M10 4.5V15.5' stroke='white' stroke-width='3.6' stroke-linecap='round'/>
          <path d='M10 4.5V15.5' stroke='#E30613' stroke-width='1.8' stroke-linecap='round'/>
          <path d='M7.2 7L10 4.2L12.8 7M7.2 13L10 15.8L12.8 13' stroke='white' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M7.2 7L10 4.2L12.8 7M7.2 13L10 15.8L12.8 13' stroke='#E30613' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        10,
        10,
    ),
    "nwse": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M5.2 14.8L14.8 5.2' stroke='white' stroke-width='3.6' stroke-linecap='round'/>
          <path d='M5.2 14.8L14.8 5.2' stroke='#E30613' stroke-width='1.8' stroke-linecap='round'/>
          <path d='M7.2 4.8H15.2V12.8M12.8 15.2H4.8V7.2' stroke='white' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M7.2 4.8H15.2V12.8M12.8 15.2H4.8V7.2' stroke='#E30613' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        10,
        10,
    ),
    "nesw": (
        """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'>
          <path d='M5.2 5.2L14.8 14.8' stroke='white' stroke-width='3.6' stroke-linecap='round'/>
          <path d='M5.2 5.2L14.8 14.8' stroke='#E30613' stroke-width='1.8' stroke-linecap='round'/>
          <path d='M4.8 12.8V4.8H12.8M7.2 15.2H15.2V7.2' stroke='white' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'/>
          <path d='M4.8 12.8V4.8H12.8M7.2 15.2H15.2V7.2' stroke='#E30613' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        10,
        10,
    ),
}


def cursor_root_variables(indent: str = "") -> str:
    lines = []
    for name, (svg, hot_x, hot_y) in _CURSOR_MAP.items():
        lines.append(f"{indent}--cursor-{name}: {_svg_cursor(svg, hot_x, hot_y)};")
    return "\n".join(lines)
