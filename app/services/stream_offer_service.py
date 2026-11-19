from sqlalchemy.orm import Session

from app.models.offer import Offer
from app.models.stream import Stream
from app.models.stream_offer import StreamOffer
from app.models.stream_offer_snapshot import StreamOfferSnapshot
from app.services.weight_service import calculate_weights

class StreamOfferService:

    def __init__(self, db: Session):
        self.db = db

    def _create_snapshot(self, stream_id: int):
        existing_snapshot = (
            self.db.query(StreamOfferSnapshot)
            .filter(
                StreamOfferSnapshot.stream_id == stream_id,
            )
            .first()
        )

        if existing_snapshot is not None:
            return

        stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
            )
            .all()
        )

        for stream_offer in stream_offers:
            snapshot = StreamOfferSnapshot(
                stream_id=stream_offer.stream_id,
                offer_id=stream_offer.offer_id,
                weight=stream_offer.weight,
                is_pinned=stream_offer.is_pinned,
                status=stream_offer.status,
            )
            self.db.add(snapshot)

        self.db.flush()


    def add_offer(
        self,
        stream_id: int,
        offer_id: int,
    ):
        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        offer = self.db.get(Offer, offer_id)

        if offer is None:
            raise ValueError("Offer not found")

        self._create_snapshot(stream_id)

        stream_offer = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.offer_id == offer_id,
            )
            .first()
        )
        if stream_offer is not None:
            if stream_offer.status == "removed":
                stream_offer.status = "active"
            else:
                raise ValueError("Offer already exists")

        else:
            stream_offer = StreamOffer(
                stream_id=stream_id,
                offer_id=offer_id,
                weight=0,
                is_pinned=False,
                status="active",
            )

            self.db.add(stream_offer)
        self.db.flush()

        active_stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.status == "active",
            )
            .all()
        )

        weight_data = [
            {
                "id": item.id,
                "weight": item.weight,
                "is_pinned": item.is_pinned,
                "status": item.status,
            }
            for item in active_stream_offers
        ]



        calculate_weights(weight_data)

        for item, data in zip(active_stream_offers, weight_data):
            item.weight = data["weight"]

        stream.has_unpublished_changes = True

        return stream_offer

    def remove_offer(self, stream_id: int, offer_id: int):
        stream_offer = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.offer_id == offer_id,
            )
            .first()
        )

        if stream_offer is None:
            raise ValueError("Stream offer not found")

        self._create_snapshot(stream_id)

        if stream_offer.status == "removed":
            raise ValueError("Offer is already removed")

        stream_offer.status = "removed"
        stream_offer.weight = 0

        active_stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.status == "active",
            )
            .all()
        )

        weight_data = [
            {
                "id": item.id,
                "weight": item.weight,
                "is_pinned": item.is_pinned,
                "status": item.status,
            }
            for item in active_stream_offers
        ]

        calculate_weights(weight_data)

        for item, data in zip(active_stream_offers, weight_data):
            item.weight = data["weight"]

        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        stream.has_unpublished_changes = True

        return stream_offer

    def restore_offer(self, stream_id: int, offer_id: int):
        stream_offer = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.offer_id == offer_id,
            )
            .first()
        )

        if stream_offer is None:
            raise ValueError("Stream offer not found")

        self._create_snapshot(stream_id)

        if stream_offer.status == "active":
            raise ValueError("Offer is already active")

        stream_offer.status = "active"
        stream_offer.weight = 0

        self.db.flush()

        active_stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.status == "active",
            )
            .all()
        )

        weight_data = [
            {
                "id": item.id,
                "weight": item.weight,
                "is_pinned": item.is_pinned,
                "status": item.status,
            }
            for item in active_stream_offers
        ]

        calculate_weights(weight_data)

        for item, data in zip(active_stream_offers, weight_data):
            item.weight = data["weight"]

        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        stream.has_unpublished_changes = True

        return stream_offer

    def pin_offer(self, stream_id: int, offer_id: int):
        stream_offer = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.offer_id == offer_id,
            )
            .first()
        )

        if stream_offer is None:
            raise ValueError("Stream offer not found")

        if stream_offer.status != "active":
            raise ValueError("Cannot pin removed offer")

        self._create_snapshot(stream_id)

        stream_offer.is_pinned = True

        active_stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.status == "active",
            )
            .all()
        )

        weight_data = [
            {
                "id": item.id,
                "weight": item.weight,
                "is_pinned": item.is_pinned,
                "status": item.status,
            }
            for item in active_stream_offers
        ]

        calculate_weights(weight_data)

        for item, data in zip(active_stream_offers, weight_data):
            item.weight = data["weight"]

        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        stream.has_unpublished_changes = True

        return stream_offer

    def unpin_offer(self, stream_id: int, offer_id: int):
        stream_offer = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.offer_id == offer_id,
            )
            .first()
        )

        if stream_offer is None:
            raise ValueError("Stream offer not found")

        if stream_offer.status != "active":
            raise ValueError("Cannot unpin removed offer")

        self._create_snapshot(stream_id)

        stream_offer.is_pinned = False

        active_stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
                StreamOffer.status == "active",
            )
            .all()
        )

        weight_data = [
            {
                "id": item.id,
                "weight": item.weight,
                "is_pinned": item.is_pinned,
                "status": item.status,
            }
            for item in active_stream_offers
        ]

        calculate_weights(weight_data)

        for item, data in zip(active_stream_offers, weight_data):
            item.weight = data["weight"]

        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        stream.has_unpublished_changes = True

        return stream_offer

    def cancel_changes(self, stream_id: int):
        stream = self.db.get(Stream, stream_id)

        if stream is None:
            raise ValueError("Stream not found")

        snapshots = (
            self.db.query(StreamOfferSnapshot)
            .filter(
                StreamOfferSnapshot.stream_id == stream_id,
            )
            .all()
        )
        if not snapshots:
            if stream.has_unpublished_changes:
                self.db.query(StreamOffer).filter(
                    StreamOffer.stream_id == stream_id,
                ).delete()

            stream.has_unpublished_changes = False
            return

        snapshot_offer_ids = {
            snapshot.offer_id
            for snapshot in snapshots
        }

        current_stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream_id,
            )
            .all()
        )

        for stream_offer in current_stream_offers:
            if stream_offer.offer_id not in snapshot_offer_ids:
                self.db.delete(stream_offer)

        self.db.flush()

        for snapshot in snapshots:
            stream_offer = (
                self.db.query(StreamOffer)
                .filter(
                    StreamOffer.stream_id == stream_id,
                    StreamOffer.offer_id == snapshot.offer_id,
                )
                .first()
            )

            if stream_offer is None:
                stream_offer = StreamOffer(
                    stream_id=stream_id,
                    offer_id=snapshot.offer_id,
                    weight=snapshot.weight,
                    is_pinned=snapshot.is_pinned,
                    status=snapshot.status,
                )
                self.db.add(stream_offer)
            else:
                stream_offer.weight = snapshot.weight
                stream_offer.is_pinned = snapshot.is_pinned
                stream_offer.status = snapshot.status

        self.db.flush()

        self.db.query(StreamOfferSnapshot).filter(
            StreamOfferSnapshot.stream_id == stream_id,
        ).delete()

        stream.has_unpublished_changes = False

        return stream