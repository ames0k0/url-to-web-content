import asyncio
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from playwright.async_api import async_playwright


@dataclass
class RequestHeader:
    method: str
    router: str
    queries: dict[str, list[str]]


class WCLPlaywright:
    context: str | None = None
    browser: str | None = None

    @classmethod
    async def initiate(cls):
        cls.context = await async_playwright().start()
        cls.browser = await cls.context.chromium.launch(headless=True)
    @classmethod
    async def terminate(cls):
        await cls.browser.close()
        await cls.context.stop()

    @classmethod
    async def get_content(cls, url: str) -> str:
        page = await cls.browser.new_page()
        await page.goto(url)

        content = await page.content()
        await page.close()

        return content


class Server:
    HOST: str = "0.0.0.0"
    PORT: int = 8888
    instance: str | None = None

    @classmethod
    async def initiate(cls):
        cls.instance = await asyncio.start_server(
            cls.handle_requests,
            host=cls.HOST,
            port=cls.PORT,
        )
        addrs = ', '.join(str(sock.getsockname()) for sock in cls.instance.sockets)
        print(f'Serving on {addrs}')
    @classmethod
    async def terminate(cls):
        pass

    @staticmethod
    def parse_request_header(*, message: str) -> RequestHeader:
        method, endpoint = message.split()[:2]
        parsed_endpoint = urlparse(endpoint)
        queries = parse_qs(parsed_endpoint.query)
        return RequestHeader(
            method=method,
            router=parsed_endpoint.path,
            queries=queries
        )

    async def handle_requests(reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        request_header = Server.parse_request_header(message=message)

        for url in request_header.queries.get("url", [])[:1]:
            content = await WCLPlaywright.get_content(url=url)
            writer.write(content.encode())
            print(f"Sent: {len(content)} bytes.")
            await writer.drain()

        print("Close the connection")
        writer.close()
        await writer.wait_closed()
        print(request_header)


async def initiate():
    await Server.initiate()
    await WCLPlaywright.initiate()
async def terminate():
    await Server.terminate()
    await WCLPlaywright.terminate()


async def main():
    try:
        async with Server.instance:
            await Server.instance.serve_forever()
    except Exception as e:
        print(e.args[0])


if __name__ == "__main__":
    with asyncio.Runner() as runner:
        runner.run(initiate())
        try:
            runner.run(main())
        except KeyboardInterrupt:
            pass
        runner.run(terminate())
