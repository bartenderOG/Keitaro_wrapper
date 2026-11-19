from sqlalchemy.orm import Session

from app.models.offer import Offer
from app.models.stream import Stream
from app.models.stream_offer import StreamOffer
from app.models.stream_offer_snapshot import StreamOfferSnapshot
from app.services.keitaro_client import KeitaroClient


class PushService:
    def __init__(
        self,
        db: Session,
        keitaro: KeitaroClient,
    ):
        self.db = db
        self.keitaro = keitaro

    async def build_offers_payload(self, stream_id: int) -> list[dict]:
        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        keitaro_offers = await self.keitaro.get_offers()

        keitaro_offer_ids = {
            offer["id"]
            for offer in keitaro_offers
        }

        stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.status == "active",
            )
            .all()
        )

        payload = []

        for stream_offer in stream_offers:
            offer = self.db.get(Offer, stream_offer.offer_id)

            if offer is None:
                raise ValueError(
                    f"Offer {stream_offer.offer_id} not found"
                )

            if offer.keitaro_id not in keitaro_offer_ids:
                raise ValueError(
                    f"Offer {offer.keitaro_id} is not available in Keitaro"
                )

            payload.append(
                {
                    "offer_id": offer.keitaro_id,
                    "share": stream_offer.weight,
                    "state": "active",
                }
            )

        return payload

    async def push_stream(self, stream_id: int):
        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        payload = await self.build_offers_payload(stream_id)

        result = await self.keitaro.update_stream(
            stream.keitaro_id,
            payload,
        )

        self.db.query(StreamOfferSnapshot).filter(
            StreamOfferSnapshot.stream_id == stream_id,
        ).delete()

        stream.has_unpublished_changes = False

        return result
