from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.stream import Stream
from app.models.offer import Offer
from app.models.stream_offer import StreamOffer
from app.db.session import SessionLocal
from app.models.campaign import Campaign
from app.services.stream_offer_service import StreamOfferService
from app.services.push_service import PushService
from app.services.keitaro_client import KeitaroClient
from app.services.campaign_creator import CampaignCreator
from app.services.sync_service import SyncService

router = APIRouter(
    prefix="/campaigns",
    tags=["campaigns"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_campaigns(
    db: Session = Depends(get_db),
):
    campaigns = (
        db.query(Campaign)
        .order_by(Campaign.id)
        .all()
    )

    return [
        {
            "id": campaign.id,
            "keitaro_id": campaign.keitaro_id,
            "name": campaign.name,
            "domain_id": campaign.domain_id,
            "group_id": campaign.group_id,
            "traffic_source_id": campaign.traffic_source_id,
        }
        for campaign in campaigns
    ]

@router.get("/offers")
async def get_offers():
    async with KeitaroClient() as keitaro:
        return await keitaro.get_offers()


@router.get("/resources")
async def get_resources():
    async with KeitaroClient() as keitaro:
        return {
            "domains": await keitaro.get_domains(),
            "groups": await keitaro.get_groups(),
            "traffic_sources": await keitaro.get_traffic_sources(),
            "offers": await keitaro.get_offers(),
        }


@router.post("")
async def create_campaign(
    name: str,
    geo_code: str,
    offer_keitaro_id: int,
    domain_id: int,
    group_id: int,
    traffic_source_id: int,
    db: Session = Depends(get_db),
):
    async with KeitaroClient() as keitaro:
        creator = CampaignCreator(
            db=db,
            keitaro=keitaro,
        )

        result = await creator.create_campaign(
            name=name,
            geo_code=geo_code,
            offer_keitaro_id=offer_keitaro_id,
            domain_id=domain_id,
            group_id=group_id,
            traffic_source_id=traffic_source_id,
        )

    return result

@router.post("/{campaign_id}/sync")
async def sync_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
):
    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == campaign_id)
        .first()
    )

    if campaign is None:
        raise ValueError("Campaign not found")

    async with KeitaroClient() as keitaro:
        service = SyncService(
            db=db,
            keitaro=keitaro,
        )

        await service.sync_streams(campaign)

        streams = (
            db.query(Stream)
            .filter(Stream.campaign_id == campaign.id)
            .all()
        )

        for stream in streams:
            await service.sync_stream_offers(stream)

    return {
        "status": "synced",
        "campaign_id": campaign.id,
    }

@router.get("/{campaign_id}/streams")
def get_campaign_streams(
    campaign_id: int,
    db: Session = Depends(get_db),
):
    streams = (
        db.query(Stream)
        .filter(Stream.campaign_id == campaign_id)
        .order_by(Stream.position)
        .all()
    )

    result = []

    for stream in streams:
        stream_offers = (
            db.query(StreamOffer)
            .filter(StreamOffer.stream_id == stream.id)
            .all()
        )

        offers = []

        for stream_offer in stream_offers:
            offer = db.get(Offer, stream_offer.offer_id)

            if offer is None:
                continue

            offers.append(
                {
                    "id": offer.id,
                    "keitaro_id": offer.keitaro_id,
                    "name": offer.name,
                    "weight": stream_offer.weight,
                    "is_pinned": stream_offer.is_pinned,
                    "status": stream_offer.status,
                }
            )

        result.append(
            {
                "id": stream.id,
                "keitaro_id": stream.keitaro_id,
                "name": stream.name,
                "position": stream.position,
                "has_unpublished_changes": (
                    stream.has_unpublished_changes
                ),
                "offers": offers,
            }
        )

    return result

@router.post("/{campaign_id}/streams/{stream_id}/offers/{offer_id}")
def add_offer_to_stream(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
):
    stream = (
        db.query(Stream)
        .filter(
            Stream.id == stream_id,
            Stream.campaign_id == campaign_id,
        )
        .first()
    )

    if stream is None:
        raise ValueError("Stream not found")

    service = StreamOfferService(db)

    stream_offer = service.add_offer(
        stream_id=stream_id,
        offer_id=offer_id,
    )

    db.commit()

    return {
        "id": stream_offer.id,
        "stream_id": stream_offer.stream_id,
        "offer_id": stream_offer.offer_id,
        "weight": stream_offer.weight,
        "is_pinned": stream_offer.is_pinned,
        "status": stream_offer.status,
    }

@router.delete("/{campaign_id}/streams/{stream_id}/offers/{offer_id}")
def remove_offer_from_stream(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
):
    stream = (
        db.query(Stream)
        .filter(
            Stream.id == stream_id,
            Stream.campaign_id == campaign_id,
        )
        .first()
    )

    if stream is None:
        raise ValueError("Stream not found")

    service = StreamOfferService(db)

    stream_offer = service.remove_offer(
        stream_id=stream_id,
        offer_id=offer_id,
    )

    db.commit()

    return {
        "id": stream_offer.id,
        "stream_id": stream_offer.stream_id,
        "offer_id": stream_offer.offer_id,
        "weight": stream_offer.weight,
        "is_pinned": stream_offer.is_pinned,
        "status": stream_offer.status,
    }

@router.post("/{campaign_id}/streams/{stream_id}/offers/{offer_id}/restore")
def restore_offer_in_stream(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
):
    stream = (
        db.query(Stream)
        .filter(
            Stream.id == stream_id,
            Stream.campaign_id == campaign_id,
        )
        .first()
    )

    if stream is None:
        raise ValueError("Stream not found")

    service = StreamOfferService(db)

    stream_offer = service.restore_offer(
        stream_id=stream_id,
        offer_id=offer_id,
    )

    db.commit()

    return {
        "id": stream_offer.id,
        "stream_id": stream_offer.stream_id,
        "offer_id": stream_offer.offer_id,
        "weight": stream_offer.weight,
        "is_pinned": stream_offer.is_pinned,
        "status": stream_offer.status,
    }

@router.post("/{campaign_id}/streams/{stream_id}/offers/{offer_id}/pin")
def pin_offer(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
):
    stream = (
        db.query(Stream)
        .filter(
            Stream.id == stream_id,
            Stream.campaign_id == campaign_id,
        )
        .first()
    )

    if stream is None:
        raise ValueError("Stream not found")

    service = StreamOfferService(db)

    stream_offer = service.pin_offer(
        stream_id=stream_id,
        offer_id=offer_id,
    )

    db.commit()

    return {
        "id": stream_offer.id,
        "stream_id": stream_offer.stream_id,
        "offer_id": stream_offer.offer_id,
        "weight": stream_offer.weight,
        "is_pinned": stream_offer.is_pinned,
        "status": stream_offer.status,
    }

@router.post("/{campaign_id}/streams/{stream_id}/offers/{offer_id}/unpin")
def unpin_offer(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
):
    stream = (
        db.query(Stream)
        .filter(
            Stream.id == stream_id,
            Stream.campaign_id == campaign_id,
        )
        .first()
    )

    if stream is None:
        raise ValueError("Stream not found")

    service = StreamOfferService(db)

    stream_offer = service.unpin_offer(
        stream_id=stream_id,
        offer_id=offer_id,
    )

    db.commit()

    return {
        "id": stream_offer.id,
        "stream_id": stream_offer.stream_id,
        "offer_id": stream_offer.offer_id,
        "weight": stream_offer.weight,
        "is_pinned": stream_offer.is_pinned,
        "status": stream_offer.status,
    }

@router.post("/{campaign_id}/streams/{stream_id}/cancel")
def cancel_stream_changes(
    campaign_id: int,
    stream_id: int,
    db: Session = Depends(get_db),
):
    stream = (
        db.query(Stream)
        .filter(
            Stream.id == stream_id,
            Stream.campaign_id == campaign_id,
        )
        .first()
    )

    if stream is None:
        raise ValueError("Stream not found")

    service = StreamOfferService(db)

    service.cancel_changes(stream_id)

    db.commit()

    return {
        "status": "cancelled",
        "stream_id": stream_id,
        "has_unpublished_changes": stream.has_unpublished_changes,
    }

@router.post("/{campaign_id}/streams/{stream_id}/push")
async def push_stream(
    campaign_id: int,
    stream_id: int,
    db: Session = Depends(get_db),
):
    stream = (
        db.query(Stream)
        .filter(
            Stream.id == stream_id,
            Stream.campaign_id == campaign_id,
        )
        .first()
    )

    if stream is None:
        raise ValueError("Stream not found")

    async with KeitaroClient() as keitaro:
        service = PushService(
            db=db,
            keitaro=keitaro,
        )

        result = await service.push_stream(stream_id)

    db.commit()

    return {
        "status": "pushed",
        "stream_id": stream_id,
        "keitaro_stream_id": stream.keitaro_id,
        "has_unpublished_changes": stream.has_unpublished_changes,
        "keitaro_response": result,
    }
