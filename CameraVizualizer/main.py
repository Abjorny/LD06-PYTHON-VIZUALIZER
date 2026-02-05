import asyncio
import websockets
import json
import struct
from io import BytesIO
from picamera2 import Picamera2


class VideoWebSocketServer:
    def __init__(self):
        self.clients = set()
        self.running = True

        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()

    async def register(self, ws):
        self.clients.add(ws)
        print(f"Клиент подключён. Всего: {len(self.clients)}")

    async def unregister(self, ws):
        self.clients.discard(ws)
        print(f"Клиент отключён. Всего: {len(self.clients)}")

    async def handler(self, ws):
        await self.register(ws)
        try:
            await ws.wait_closed()
        finally:
            await self.unregister(ws)

    async def broadcast_loop(self):
        while self.running:
            if not self.clients:
                await asyncio.sleep(0.01)
                continue

            # 🔥 JPEG напрямую из Picamera2
            buffer = BytesIO()
            self.picam2.capture_file(buffer, format="jpeg")
            img_bytes = buffer.getvalue()

            meta = {
                "text": "init"
            }
            meta_bytes = json.dumps(meta).encode("utf-8")

            payload = (
                struct.pack(">I", len(meta_bytes)) +
                meta_bytes +
                img_bytes
            )

            dead = []
            for ws in list(self.clients):
                try:
                    await ws.send(payload)
                except:
                    dead.append(ws)

            for ws in dead:
                self.clients.discard(ws)

            await asyncio.sleep(0)  

    async def start(self, host="0.0.0.0", port=8002):
        print(f"WebSocket сервер запущен на {host}:{port}")
        async with websockets.serve(
            self.handler,
            host,
            port,
            max_size=None,
            compression=None,
        ):
            await self.broadcast_loop()


if __name__ == "__main__":
    asyncio.run(VideoWebSocketServer().start())
