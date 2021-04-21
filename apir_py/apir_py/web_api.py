from tornado.websocket import WebSocketHandler


class EventsWebSocket(WebSocketHandler):
    def open(self):
        print("New Connection")

    def on_message(self, message):
        print(f"[+] New message {message}")

    def on_close(self):
        print("WebSocket closed")

    def on_ast_event(self, msg: str):
        self.write_message(u"" + msg)
