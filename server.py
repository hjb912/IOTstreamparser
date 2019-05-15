import errno
import functools
import socket

import tornado.ioloop
from tornado.iostream import IOStream

MSG_HEADER_LEN = 16
MSG_CONTROL_POSITION = (0, 1)
MSG_CONTROL = bytes([0x1e, 0xdc])
MSG_LEN_POSITION = (12, 13)


async def handle_connection(connection, address):
    stream = IOStream(connection)

    message = '1'
    while message:
        try:
            message = await stream.read_bytes(len(MSG_CONTROL_POSITION))
            print(f"control message from client: {message}")

            _MSG_CONTROL = bytes([message[MSG_CONTROL_POSITION[0]], message[MSG_CONTROL_POSITION[1]]])

            if _MSG_CONTROL == MSG_CONTROL:
                message = await stream.read_bytes(MSG_HEADER_LEN - len(MSG_CONTROL_POSITION))
                print(f"message header is {message}")

                content_len = int.from_bytes(
                    bytes([message[MSG_LEN_POSITION[0]], message[MSG_LEN_POSITION[1]]]),
                    byteorder='big'
                )
                print(f"content_len is {content_len}")

                message = await stream.read_bytes(content_len)
                print(f"message body from client: {message}")

                message = await stream.read_bytes(1)
                print(f"checksum: {message}")

        except Exception as e:
            print(e)
            message = ''


def connection_ready(sock, fd, events):
    while True:
        try:
            connection, address = sock.accept()
        except socket.error as e:
            if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        connection.setblocking(0)
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.spawn_callback(handle_connection, connection, address)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(("", 8888))
    sock.listen(128)

    io_loop = tornado.ioloop.IOLoop.current()
    callback = functools.partial(connection_ready, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    io_loop.start()
