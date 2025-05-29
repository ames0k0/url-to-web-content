import os
import asyncio


async def main():
    url = "http://127.0.0.1:8000"

    message = "GET {}\r\nHost: {}\r\n".format(
        f"http://127.0.0.1:8888/get?url={url}",
        "client",
    )

    reader, writer = await asyncio.open_connection(
        '127.0.0.1',
        8888
    )

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    filepath = os.path.join("data", "server_content.html")
    with open(filepath, "wb") as ftwb:
        while True:
            data = await reader.read(1000)
            if not data:
                break
            ftwb.write(data)

    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
