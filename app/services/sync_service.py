from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.stream import Stream
from app.services.keitaro_client import KeitaroClient
from app.models.offer import Offer
from app.models.stream_offer import StreamOffer

class SyncService:

    def __init__(
        self,
        db: Session,
        keitaro: KeitaroClient,
    ):
        self.db = db
        self.keitaro = keitaro

    async def sync_campaigns(self):
        campaigns = await self.keitaro.get_campaigns()

        for data in campaigns:
            if (
                not data["domain_id"]
                or not data["group_id"]
                or not data["traffic_source_id"]
            ):
                print(
                    f"Пропускаем кампанию {data['id']}: "
                    "не хватает domain/group/traffic source"
                )
                continue

            campaign = (
                self.db.query(Campaign)
                .filter(
                    Campaign.keitaro_id == data["id"],
                )
                .first()
            )

            if campaign is None:
                campaign = Campaign(
                    keitaro_id=data["id"],
                    name=data["name"],
                    domain_id=data["domain_id"],
                    group_id=data["group_id"],
                    traffic_source_id=data["traffic_source_id"],
                )

                self.db.add(campaign)

            else:
                campaign.name = data["name"]
                campaign.domain_id = data["domain_id"]
                campaign.group_id = data["group_id"]
                campaign.traffic_source_id = data["traffic_source_id"]

        self.db.commit()

    async def sync_streams(self, campaign: Campaign):
        streams = await self.keitaro.get_streams(
            campaign.keitaro_id,
        )

        for data in streams:
            stream = (
                self.db.query(Stream)
                .filter(
                    Stream.keitaro_id == data["id"],
                )
                .first()
            )

            if stream is None:
                stream = Stream(
                    keitaro_id=data["id"],
                    campaign_id=campaign.id,
                    name=data["name"],
                    position=data["position"],
                )

                self.db.add(stream)

            else:
                stream.name = data["name"]
                stream.position = data["position"]

        self.db.commit()

    async def sync_stream_offers(self, stream: Stream):
        campaign = self.db.get(
            Campaign,
            stream.campaign_id,
        )

        if campaign is None:
            raise ValueError("Campaign not found")

        streams = await self.keitaro.get_streams(
            campaign.keitaro_id,
        )

        keitaro_stream = next(
            (
                item
                for item in streams
                if item["id"] == stream.keitaro_id
            ),
            None,
        )

        if keitaro_stream is None:
            raise ValueError("Stream not found in Keitaro")

        remote_stream_offers = keitaro_stream.get("offers", [])

        remote_offer_ids = {
            data["offer_id"]
            for data in remote_stream_offers
        }

        local_stream_offers = (
            self.db.query(StreamOffer)
            .filter(
                StreamOffer.stream_id == stream.id,
            )
            .all()
        )

        for stream_offer in local_stream_offers:
            if stream_offer.offer_id:
                offer = self.db.get(
                    Offer,
                    stream_offer.offer_id,
                )

                if (
                    offer is not None
                    and offer.keitaro_id not in remote_offer_ids
                ):
                    stream_offer.status = "removed"
                    stream_offer.weight = 0

        if not remote_stream_offers:
            self.db.commit()
            return

        keitaro_offers = await self.keitaro.get_offers()

        for data in remote_stream_offers:
            offer_data = next(
                (
                    item
                    for item in keitaro_offers
                    if item["id"] == data["offer_id"]
                ),
                None,
            )

            if offer_data is None:
                continue

            offer = (
                self.db.query(Offer)
                .filter(
                    Offer.keitaro_id == data["offer_id"],
                )
                .first()
            )

            if offer is None:
                offer = Offer(
                    keitaro_id=data["offer_id"],
                    name=offer_data["name"],
                )
                self.db.add(offer)
                self.db.flush()

            stream_offer = (
                self.db.query(StreamOffer)
                .filter(
                    StreamOffer.stream_id == stream.id,
                    StreamOffer.offer_id == offer.id,
                )
                .first()
            )

            if stream_offer is None:
                stream_offer = StreamOffer(
                    stream_id=stream.id,
                    offer_id=offer.id,
                    weight=data["share"],
                    is_pinned=False,
                    status="active",
                )
                self.db.add(stream_offer)
            else:
                stream_offer.weight = data["share"]
                stream_offer.status = "active"

        self.db.commit()