from tornado import tcpclient
from tornado.ioloop import IOLoop

async def connect(host="localhost", port=8888):
    print("init..")
    client = tcpclient.TCPClient()
    print(f"Initial connection {host}:{port}")
    stream = await client.connect(host, port)
    print(f"Sending 's' command to {host}:{port}")
    key = bytes(
        [0x1e, 0xdc, 0x01, 0x00, 0x01, 0x02, 0x03, 0x04,
            0x05, 0x06, 0x07, 0x08, 0x08, 0x10, 0x00, 0x02, 0x13, 0x14, 0x00])
    await stream.write(key)
    #answer = await stream.read_until_close()
    #answer = answer.decode("utf8")
    print('answer')
    await stream.write(key)
    #stream.close()

if __name__ == "__main__":
    print("start..")
    IOLoop.instance().run_sync(connect)


