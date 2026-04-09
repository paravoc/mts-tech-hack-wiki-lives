from __future__ import annotations

import json
import threading
from collections.abc import Callable

import websocket


EventCallback = Callable[[dict], None]


class WikiLiveWebSocketClient:
    def __init__(self, ws_url: str, on_event: EventCallback | None = None) -> None:
        self._ws_url = ws_url
        self._on_event = on_event
        self._app: websocket.WebSocketApp | None = None
        self._thread: threading.Thread | None = None

    def connect(self) -> None:
        if self._app is not None:
            return

        self._app = websocket.WebSocketApp(
            self._ws_url,
            on_message=self._handle_message,
        )
        self._thread = threading.Thread(target=self._app.run_forever, daemon=True)
        self._thread.start()

    def subscribe_page(self, page_id: str) -> None:
        self._send({"action": "subscribe", "pageId": page_id})

    def unsubscribe_page(self, page_id: str) -> None:
        self._send({"action": "unsubscribe", "pageId": page_id})

    def ping(self) -> None:
        self._send({"action": "ping"})

    def close(self) -> None:
        if self._app is not None:
            self._app.close()
        self._app = None
        self._thread = None

    def _send(self, payload: dict) -> None:
        if self._app is None or self._app.sock is None or not self._app.sock.connected:
            return
        self._app.send(json.dumps(payload))

    def _handle_message(self, _socket: websocket.WebSocketApp, message: str) -> None:
        if self._on_event is None:
            return

        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            return

        self._on_event(payload)
