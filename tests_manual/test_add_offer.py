from app.db.session import SessionLocal
from app.models.campaign import Campaign
from app.models.offer import Offer
from app.models.stream import Stream
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

    test_offer = (
        db.query(Offer)
        .filter(Offer.keitaro_id == 999999)
        .first()
    )

    if test_offer is None:
        test_offer = Offer(
            keitaro_id=999999,
            name="TEST LOCAL OFFER",
        )
        db.add(test_offer)
        db.commit()
        db.refresh(test_offer)

    print(
        "Добавляем offer:",
        test_offer.id,
        test_offer.keitaro_id,
    )

    service = StreamOfferService(db)

    service.add_offer(
        stream_id=stream.id,
        offer_id=test_offer.id,
    )

    db.commit()

    print("Offer добавлен")

finally:
    db.close()
