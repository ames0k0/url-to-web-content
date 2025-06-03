import os
import sys
import asyncio

import httpx


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8888
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
TARGET_URL = "http://0.0.0.0:8000"
REQUEST_URL = f"{SERVER_URL}/wcl?url={TARGET_URL}"
REQUEST_METHOD = "GET"
OUTPUT_FILEPATH = os.path.join("data", "server_content.html")


async def casyncio():
    message = "{request_method} {server_endpoint}\r\nHost: {client_host}\r\n".format(
        request_method=REQUEST_METHOD,
        server_endpoint=REQUEST_URL.replace(SERVER_URL, ''),
        client_host=SERVER_HOST,
    )

    reader, writer = await asyncio.open_connection(
        host=SERVER_HOST,
        port=SERVER_PORT,
    )

    writer.write(message.encode())
    await writer.drain()

    with open(OUTPUT_FILEPATH, "wb") as ftwb:
        while True:
            data = await reader.read(1000)
            if not data:
                break
            ftwb.write(data)
        print(f'Received: {ftwb.tell()} bytes.')

    writer.close()
    await writer.wait_closed()


async def chttpx():
    with httpx.stream(
        method=REQUEST_METHOD,
        url=REQUEST_URL,
    ) as response:
        with open(OUTPUT_FILEPATH, "wb") as ftwb:
            for chunk in response.iter_bytes():
                ftwb.write(chunk)
            print(f'Received: {ftwb.tell()} bytes.')


if __name__ == "__main__":
    client = None

    for arg in sys.argv:
        if arg == "asyncio":
            client = casyncio
            break
        if arg == "httpx":
            client = chttpx
            break
    else:
        print('Usage Example:\nuv run python src/client.py [asyncio,httpx]')
        exit()

    with asyncio.Runner() as runner:
        try:
            runner.run(client())
        except KeyboardInterrupt:
            pass
