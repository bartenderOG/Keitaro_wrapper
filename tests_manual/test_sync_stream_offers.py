import asyncio

from app.db.session import SessionLocal
from app.models.stream import Stream
from app.models.offer import Offer
from app.models.stream_offer import StreamOffer
from app.services.keitaro_client import KeitaroClient
from app.services.sync_service import SyncService


async def main():
    db = SessionLocal()

    try:
        stream = (
            db.query(Stream)
            .filter(
                Stream.keitaro_id == 1326838,
            )
            .first()
        )

        if stream is None:
            print("Stream не найден")
            return

        stream_offers = (
            db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream.id,
            )
            .all()
        )

        print("\nДо Sync:")

        for stream_offer in stream_offers:
            offer = db.get(Offer, stream_offer.offer_id)

            print(
                offer.keitaro_id,
                offer.name,
                "| weight:", stream_offer.weight,
                "| status:", stream_offer.status,
            )

        print(
            f"Синхронизируем offers stream: "
            f"{stream.name} "
            f"(Keitaro ID: {stream.keitaro_id})"
        )

        async with KeitaroClient() as keitaro:
            service = SyncService(db, keitaro)

            await service.sync_stream_offers(stream)

        print("\nПосле Sync:")

        stream_offers = (
            db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream.id,
            )
            .all()
        )

        for stream_offer in stream_offers:
            offer = db.get(Offer, stream_offer.offer_id)

            print(
                offer.keitaro_id,
                offer.name,
                "| weight:", stream_offer.weight,
                "| status:", stream_offer.status,
            )

        print("Синхронизация offers завершена")

    finally:
        db.close()


asyncio.run(main())
