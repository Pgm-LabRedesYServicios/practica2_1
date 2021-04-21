from tornado.ioloop import IOLoop
from tornado.web import Application
import asyncio
from sys import argv, exit

from apir_py.web_api import EventsWebSocket
from apir_py.asterisk_conn import ast_connect


def make_app():
    return Application([
        (r"/api", EventsWebSocket)
    ])


def print_handler(e):
    print(e)


def main():
    if len(argv) != 5:
        print(f"Usage: {argv[0]} <host> <port> <username> <secret>\n")
        exit(1)

    try:
        host = argv[1]
        port = int(argv[2])
        username = argv[3]
        secret = argv[4]
    except:
        print("Error while parsing arguments")
        exit(1)

    ast_conn = ast_connect(host, port, username, secret, print_handler)

    app = make_app()
    app.listen(8888)

    ast_conn.connect()


if __name__ == "__main__":
    main()
