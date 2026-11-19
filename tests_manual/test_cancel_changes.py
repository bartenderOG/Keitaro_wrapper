from app.db.session import SessionLocal
from app.models.campaign import Campaign
from app.models.offer import Offer
from app.models.stream import Stream
from app.models.stream_offer import StreamOffer
from app.services.stream_offer_service import StreamOfferService


db = SessionLocal()

try:
    stream = (
        db.query(Stream)
        .filter(Stream.keitaro_id == 1326838)
        .first()
    )

    if stream is None:
        print("Stream не найден")
        raise SystemExit

    service = StreamOfferService(db)

    print("До Cancel:")

    stream_offers = (
        db.query(StreamOffer)
        .filter(StreamOffer.stream_id == stream.id)
        .all()
    )

    for stream_offer in stream_offers:
        offer = db.get(Offer, stream_offer.offer_id)

        print(
            offer.keitaro_id,
            offer.name,
            "| weight:",
            stream_offer.weight,
            "| status:",
            stream_offer.status,
        )

    service.cancel_changes(stream.id)

    db.commit()

    print("\nПосле Cancel:")

    stream_offers = (
        db.query(StreamOffer)
        .filter(StreamOffer.stream_id == stream.id)
        .all()
    )

    for stream_offer in stream_offers:
        offer = db.get(Offer, stream_offer.offer_id)

        print(
            offer.keitaro_id,
            offer.name,
            "| weight:",
            stream_offer.weight,
            "| status:",
            stream_offer.status,
        )

    db.refresh(stream)

    print(
        "\nhas_unpublished_changes:",
        stream.has_unpublished_changes,
    )

finally:
    db.close()