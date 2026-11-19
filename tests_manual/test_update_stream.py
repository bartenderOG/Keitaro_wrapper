import asyncio

from app.services.keitaro_client import KeitaroClient


async def main():
    async with KeitaroClient() as client:
        offers = [
            {
                "offer_id": 18813,
                "share": 100,
                "state": "active",
            }
        ]

        print("Отправляем в Keitaro:")
        print(offers)

        result = await client.update_stream(
            stream_id=1326838,
            offers=offers,
        )

        print("Keitaro ответил:")
        print(result)


asyncio.run(main())