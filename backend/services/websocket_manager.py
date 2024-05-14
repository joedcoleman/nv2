from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.websocket: WebSocket = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.websocket = websocket

    async def send_message(self, message: dict):
        if self.websocket is not None:
            await self.websocket.send_json(message)

    async def send_audio_chunk(self, data: bytes):
        if self.websocket is not None:
            await self.websocket.send_bytes(data)


websocket_manager = WebSocketManager()
