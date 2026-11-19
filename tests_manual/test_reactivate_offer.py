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

    stream_offer = (
        db.query(StreamOffer)
        .filter(StreamOffer.id == 2)
        .first()
    )

    if stream_offer is None:
        print("StreamOffer не найден")
        raise SystemExit

    stream_offer.status = "removed"
    db.commit()

    print("Offer переведен в removed")

    service = StreamOfferService(db)

    service.add_offer(
        stream_id=stream.id,
        offer_id=stream_offer.offer_id,
    )

    db.commit()

    print("Offer снова активирован")

    offers = (
        db.query(StreamOffer)
        .filter(StreamOffer.stream_id == stream.id)
        .all()
    )

    for item in offers:
        print(
            "offer_id:",
            item.offer_id,
            "weight:",
            item.weight,
            "status:",
            item.status,
        )

finally:
    db.close()
