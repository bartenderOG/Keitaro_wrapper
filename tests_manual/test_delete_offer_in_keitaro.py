import asyncio

from app.services.keitaro_client import KeitaroClient


async def main():
    async with KeitaroClient() as keitaro:
        result = await keitaro.update_stream(
            1326838,
            [],
        )

        print("Keitaro ответил:")
        print(result)


asyncio.run(main())
