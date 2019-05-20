import errno
import functools
import socket
import datetime

import tornado.ioloop
from tornado.iostream import IOStream

from model import SensorDataModel


FRAME_HEADER = bytes([0x1e, 0xdc])
CTRL_SIGN = bytes([0x30])

CONTENT_LEN = 2
DEVICE_VERSION_LEN = 1
DEVICE_ID_LEN = 6
SESSION_LEN = 4
CTRL_SIGN_LEN = 1


async def save(parsed_data):
    t = await SensorDataModel.create(
        pm2d5=parsed_data['pm2d5'],
        pm10=parsed_data['pm10'],
        noise=parsed_data['noise'],
        temperature=parsed_data['temperature'],
        humidity=parsed_data['humidity'],
        wind_direction=parsed_data['wind_direction'],
        wind_speed=parsed_data['wind_speed'],
        air_pressure=parsed_data['air_pressure'],
        dust=parsed_data['dust'],
    )
    print(t)


async def handle_connection(connection, address):
    stream = IOStream(connection)

    message = '1'
    while message:
        try:
            if await is_frame_header(stream):
                version = await get_device_version(stream)

                device_id = await get_device_id(stream)

                session = await get_session(stream)

                ctrl_sign = await get_ctrl_sign(stream)

                content = await get_content(stream)

                await parse_content(content)

                checksum = await get_checksum(stream)

        except Exception as e:
            print("exception: " + str(e))
            message = ''


async def get_frame_msg(stream):
    return await stream.read_bytes(len(FRAME_HEADER))


async def is_frame_header(stream):
    frame_header = await get_frame_msg(stream)
    print(f"frame header from client: {frame_header}")
    return True if frame_header == FRAME_HEADER else False


async def get_device_version(stream):
    version = await stream.read_bytes(DEVICE_VERSION_LEN)
    print(f"device version from client: {version}")
    return version


async def get_device_id(stream):
    device_id = await stream.read_bytes(DEVICE_ID_LEN)
    print(f"device id from client: {device_id}")
    return int.from_bytes(device_id, byteorder='big')


async def get_session(stream):
    session = await stream.read_bytes(SESSION_LEN)
    print(f"device session from client: {session}")
    return session


async def get_ctrl_sign(stream):
    ctrl_sign = await stream.read_bytes(len(CTRL_SIGN))
    print(f"ctrl_sign from client: {ctrl_sign}")
    return ctrl_sign


async def get_content(stream):
    content = await stream.read_bytes(CONTENT_LEN)
    print(f"message body from client: {content}")
    return content


async def parse_content(content):
    parsed_data = {
        'pm2d5': _get_pm2d5(content),
        'pm10': _get_pm10(content),
        'noise': _get_noise(content),
        'temperature': _get_temperature(content),
        'humidity': _get_humidity(content),
        'wind_direction': _get_wind_direction(content),
        'wind_speed': _get_wind_speed(content),
        'air_pressure': _get_air_pressure(content),
        'dust': _get_dust(content)
    }
    await save(parsed_data)


def _get_pm2d5(content):
    pm2d5 = content[:4]
    return int.from_bytes(pm2d5, byteorder='big')


def _get_pm10(content):
    pm10 = content[4:8]
    return int.from_bytes(pm10, byteorder='big')


def _get_noise(content):
    noise = content[8:12]
    return int.from_bytes(noise, byteorder='big') * 0.1


def _get_temperature(content):
    temperature = content[12:16]
    return int.from_bytes(temperature, byteorder='big', signed=True) * 0.1


def _get_humidity(content):
    humidity = content[16:20]
    return int.from_bytes(humidity, byteorder='big') * 0.1


def _get_wind_direction(content):
    wind_direction = content[20:24]
    return int.from_bytes(wind_direction, byteorder='big')


def _get_wind_speed(content):
    wind_speed = content[24:28]
    return int.from_bytes(wind_speed, byteorder='big') * 0.1


def _get_air_pressure(content):
    try:
        air_pressure = content[28:32]
    except Exception:
        air_pressure = 0
    return int.from_bytes(air_pressure, byteorder='big') * 0.001


def _get_dust(content):
    try:
        dust = content[32:36]
    except Exception:
        dust = 0
    return int.from_bytes(dust, byteorder='big')


async def get_checksum(stream):
    checksum = await stream.read_bytes(1)
    print(f"checksum: {checksum}")
    return checksum


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
