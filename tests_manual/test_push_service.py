import asyncio

from app.db.session import SessionLocal
from app.models.stream import Stream
from app.services.keitaro_client import KeitaroClient
from app.services.push_service import PushService


async def main():
    db = SessionLocal()

    try:
        stream = (
            db.query(Stream)
            .filter(Stream.keitaro_id == 1326838)
            .first()
        )

        if stream is None:
            print("Stream не найден")
            return

        async with KeitaroClient() as keitaro:
            service = PushService(
                db=db,
                keitaro=keitaro,
            )

            payload = await service.build_offers_payload(
                stream.id
            )

            print("Payload для Keitaro:")
            print(payload)

    finally:
        db.close()


asyncio.run(main())