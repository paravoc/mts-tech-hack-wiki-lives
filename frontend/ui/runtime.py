from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import time

import requests
import streamlit as st


CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_EXE = REPO_ROOT / "out" / "build" / "x64-Debug" / "wikilive_backend.exe"
DEFAULT_BACKEND_URL = os.getenv("WIKILIVE_BACKEND_URL", "http://127.0.0.1:3000")


@dataclass(slots=True)
class BackendStatus:
    ready: bool
    url: str
    launched: bool = False
    message: str = ""


def backend_is_ready(base_url: str) -> bool:
    try:
        response = requests.get(f"{base_url.rstrip('/')}/health", timeout=2.0)
        return response.ok
    except requests.RequestException:
        return False


def ensure_backend_running(base_url: str = DEFAULT_BACKEND_URL) -> BackendStatus:
    if backend_is_ready(base_url):
        return BackendStatus(ready=True, url=base_url)

    if not BACKEND_EXE.exists():
        return BackendStatus(
            ready=False,
            url=base_url,
            message=f"Не найден backend-бинарник: {BACKEND_EXE}",
        )

    if not st.session_state.get("_backend_boot_attempted"):
        stdout_path = REPO_ROOT / "backend.out.log"
        stderr_path = REPO_ROOT / "backend.err.log"
        with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
            subprocess.Popen(
                [str(BACKEND_EXE)],
                cwd=str(REPO_ROOT),
                stdout=stdout,
                stderr=stderr,
                creationflags=CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
            )
        st.session_state["_backend_boot_attempted"] = True

    deadline = time.time() + 8.0
    while time.time() < deadline:
        if backend_is_ready(base_url):
            return BackendStatus(ready=True, url=base_url, launched=True)
        time.sleep(0.35)

    return BackendStatus(
        ready=False,
        url=base_url,
        launched=True,
        message=f"Backend на {base_url} не ответил после автозапуска.",
    )

