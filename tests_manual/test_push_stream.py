import asyncio

from app.db.session import SessionLocal
from app.models.campaign import Campaign
from app.models.offer import Offer
from app.models.stream import Stream
from app.models.stream_offer import StreamOffer
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

        print("До Push:")
        print("has_unpublished_changes:", stream.has_unpublished_changes)

        async with KeitaroClient() as keitaro:
            service = PushService(
                db=db,
                keitaro=keitaro,
            )

            result = await service.push_stream(stream.id)

            print("\nKeitaro ответил:")
            print(result)
            db.commit()
        db.refresh(stream)

        print("\nПосле Push:")
        print("has_unpublished_changes:", stream.has_unpublished_changes)

    finally:
        db.close()


asyncio.run(main())