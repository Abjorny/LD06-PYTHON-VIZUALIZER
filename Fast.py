import asyncio, websockets, cv2, main, struct, json


class VideoWebSocketServer:
    def __init__(self):
        self.clients = set()
        self.robot = main.RobotView()
        self.running = True

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Клиент подключён. Всего: {len(self.clients)}")

    async def unregister(self, websocket):
        self.clients.discard(websocket)
        print(f"Клиент отключён. Всего: {len(self.clients)}")

    async def handler(self, websocket):
        await self.register(websocket)
        try:
            await websocket.wait_closed()
        finally:
            await self.unregister(websocket)

    async def broadcast_loop(self):
        while self.running:
            if not self.clients:
                await asyncio.sleep(0)
                continue

            frame, text = self.robot.view()
            if frame is None:
                continue

            ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not ok:
                continue

            img_bytes = buffer.tobytes()

            meta = {
                "text": text
            }
            meta_bytes = json.dumps(meta).encode("utf-8")

            # 4 байта — длина JSON
            payload = struct.pack(">I", len(meta_bytes)) + meta_bytes + img_bytes

            dead = []
            for ws in list(self.clients):
                try:
                    await ws.send(payload)
                except:
                    dead.append(ws)

            for ws in dead:
                self.clients.discard(ws)

    async def start(self, host="0.0.0.0", port=8001):
        print(f"WebSocket сервер: {host}:{port}")

        async with websockets.serve(
            self.handler,
            host,
            port,
            max_size=None,
            compression=None,
        ):
            await self.broadcast_loop()


if __name__ == "__main__":
    server = VideoWebSocketServer()
    asyncio.run(server.start())
