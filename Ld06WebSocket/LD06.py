import websocket
import threading
import struct

class LD06_Point:
    def __init__(self, data):
        self.dist = data['Dist']
        self.intes = data['Intes']
        self.angle = data['Angle']

class LD06_WebSocket:
    def __init__(self, url="ws://localhost:8000/ws"):
        self.points: list[LD06_Point] = []
        with open('points_data.txt', 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            i = 1
            for line in lines:
                self.points.append(
                    LD06_Point({
                        "Dist" : float(line),
                        "Intes" : 1,
                        "Angle" : i
                    })
                )
                i += 1

    #     self.ws = websocket.WebSocketApp(
    #         url,
    #         on_open=self._on_open,
    #         on_message=self._on_message,
    #         on_error=self._on_error,
    #         on_close=self._on_close
    #     )
    #     t = threading.Thread(target=self.ws.run_forever, daemon=True)
    #     t.start()

    # def _on_open(self, ws):
    #     print("Connected to LIDAR WS")

    # def _on_message(self, ws, message):
    #     points = []
    #     for i in range(0, len(message), 5):
    #         dist = struct.unpack_from("<H", message, i)[0] / 1000.0
    #         intes = message[i+2]
    #         angle = struct.unpack_from("<H", message, i+3)[0]
    #         points.append(LD06_Point({"Dist": dist, "Intes": intes, "Angle": angle}))

    #     self.points = points

    # def _on_error(self, ws, error):
    #     print("Error:", error)

    # def _on_close(self, ws):
    #     print("Connection closed")


