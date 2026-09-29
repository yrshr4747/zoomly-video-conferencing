from collections import defaultdict

from fastapi import WebSocket


class MeetingConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)

    async def connect(self, meeting_id: str, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[meeting_id][client_id] = websocket

    def disconnect(self, meeting_id: str, client_id: str) -> None:
        self.connections[meeting_id].pop(client_id, None)
        if not self.connections[meeting_id]:
            self.connections.pop(meeting_id, None)

    async def broadcast(self, meeting_id: str, event: dict, exclude_client_id: str | None = None) -> None:
        stale: list[str] = []
        for client_id, websocket in self.connections.get(meeting_id, {}).copy().items():
            if client_id == exclude_client_id:
                continue
            try:
                await websocket.send_json(event)
            except Exception:
                stale.append(client_id)
        for client_id in stale:
            self.disconnect(meeting_id, client_id)

    async def send_to(self, meeting_id: str, client_id: str, event: dict) -> None:
        websocket = self.connections.get(meeting_id, {}).get(client_id)
        if not websocket:
            return
        try:
            await websocket.send_json(event)
        except Exception:
            self.disconnect(meeting_id, client_id)


meeting_connections = MeetingConnectionManager()
