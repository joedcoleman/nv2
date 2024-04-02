from fastapi import FastAPI, WebSocket


class WebSocketManager:
    def __init__(self):
        self.websocket: WebSocket = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.websocket = websocket

    async def send_message(self, message: dict):
        if self.websocket is not None:
            await self.websocket.send_json(message)


websocket_manager = WebSocketManager()
