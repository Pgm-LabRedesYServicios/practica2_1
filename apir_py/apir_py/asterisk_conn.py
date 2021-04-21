from pyami_asterisk import AMIClient
import asyncio


def ast_connect(host: str, port: int, username: str, secret: str, handler):
    ami = AMIClient(
        host='127.0.0.1',
        port=5038,
        username='username',
        secret='password'
    )
    ami.register_event(["*"], handler)

    return ami
