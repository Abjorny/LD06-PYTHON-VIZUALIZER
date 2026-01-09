import asyncio, websockets, json, struct, cv2
from picamera2 import Picamera2

class VideoWebSocketServer:
    def __init__(self):
        self.clients = set()
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"size": (640, 480)})
        self.picam2.configure(config)
        self.picam2.start()
        self.running = True

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Клиент подключён. Всего: {len(self.clients)}")

    async def unregister(self, websocket):
        self.clients.discard(websocket)
        print(f"Клиент отключён. Всего: {len(self.clients)}")

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            await websocket.wait_closed()
        finally:
            await self.unregister(websocket)

    async def broadcast_loop(self):
        while self.running:
            if not self.clients:
                await asyncio.sleep(0.01)
                continue

            frame = self.picam2.capture_array()
            if frame is None:
                continue

            text = "init"  
            ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not ok:
                continue
            img_bytes = buffer.tobytes()
            meta = {"text": text}
            meta_bytes = json.dumps(meta).encode("utf-8")
            payload = struct.pack(">I", len(meta_bytes)) + meta_bytes + img_bytes

            dead_clients = []
            for ws in list(self.clients):
                try:
                    await ws.send(payload)
                except:
                    dead_clients.append(ws)

            for ws in dead_clients:
                self.clients.discard(ws)

            await asyncio.sleep(0)

    async def start(self, host="0.0.0.0", port=8002):
        print(f"WebSocket сервер запущен на {host}:{port}")
        async with websockets.serve(self.handler, host, port, max_size=None, compression=None):
            await self.broadcast_loop()


if __name__ == "__main__":
    server = VideoWebSocketServer()
    asyncio.run(server.start())
