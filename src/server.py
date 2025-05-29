import asyncio
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs


@dataclass
class RequestHeader:
    method: str
    router: str
    queries: dict[str, list[str]]


def parse_request_header(*, message: str) -> RequestHeader:
    method, endpoint = message.split()[:2]
    parsed_endpoint = urlparse(endpoint)
    queries = parse_qs(parsed_endpoint.query)
    return RequestHeader(
        method=method,
        router=parsed_endpoint.path, 
        queries=queries
    )


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    request_header = parse_request_header(message=message)

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()
    print(request_header)


async def main():
    server = await asyncio.start_server(
        handle_echo,
        '127.0.0.1',
        8888
    )

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()


asyncio.run(main())
