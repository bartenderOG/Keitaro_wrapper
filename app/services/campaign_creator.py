from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.offer import Offer
from app.models.stream import Stream
from app.models.stream_offer import StreamOffer
from app.services.keitaro_client import KeitaroClient


class CampaignCreator:
    def __init__(
        self,
        db: Session,
        keitaro: KeitaroClient,
    ):
        self.db = db
        self.keitaro = keitaro

    def build_google_stream(self, geo_code: str):
        return {
            "name": f"Geo {geo_code} -> Google",
            "schema": "redirect",
            "type": "regular",
            "action_type": "http",
            "action_payload": "https://google.com",
            "filters": [
                {
                    "name": "country",
                    "mode": "accept",
                    "payload": [geo_code],
                }
            ],
            "offers": [],
        }

    def build_offer_stream(self, offer_keitaro_id: int):
        return {
            "name": "Offers",
            "schema": "landings",
            "type": "regular",
            "action_type": "http",
            "action_payload": "",
            "filters": [],
            "offers": [
                {
                    "offer_id": offer_keitaro_id,
                    "share": 100,
                    "state": "active",
                }
            ],
        }

    async def create_campaign(
        self,
        name: str,
        geo_code: str,
        offer_keitaro_id: int,
        domain_id: int,
        group_id: int,
        traffic_source_id: int,
    ):
        if not name.startswith("test_nasirdinov_"):
            raise ValueError(
                "Campaign name must start with test_nasirdinov_"
            )

        keitaro_offers = await self.keitaro.get_offers()

        offer_data = next(
            (
                offer
                for offer in keitaro_offers
                if offer["id"] == offer_keitaro_id
            ),
            None,
        )

        if offer_data is None:
            raise ValueError(
                f"Offer {offer_keitaro_id} not found in Keitaro"
            )

        campaign_data = await self.keitaro.create_campaign(
            name=name,
            alias=name,
            group_id=group_id,
            traffic_source_id=traffic_source_id,
            domain_id=domain_id,
        )

        campaign_id = campaign_data["id"]

        google_stream = await self.keitaro.create_stream(
            campaign_id=campaign_id,
            name=f"Geo {geo_code} -> Google",
            schema="redirect",
            stream_type="regular",
            action_type="http",
            action_payload="https://google.com",
            filters=[
                {
                    "name": "country",
                    "mode": "accept",
                    "payload": [geo_code],
                }
            ],
            offers=[],
        )

        offer_stream = await self.keitaro.create_stream(
            campaign_id=campaign_id,
            name="Offers",
            schema="landings",
            stream_type="regular",
            action_type="http",
            action_payload="",
            filters=[],
            offers=[
                {
                    "offer_id": offer_keitaro_id,
                    "share": 100,
                    "state": "active",
                }
            ],
        )

        campaign = Campaign(
            keitaro_id=campaign_data["id"],
            name=campaign_data["name"],
            domain_id=campaign_data["domain_id"],
            group_id=campaign_data["group_id"],
            traffic_source_id=campaign_data["traffic_source_id"],
        )

        self.db.add(campaign)
        self.db.flush()

        google_stream_db = Stream(
            keitaro_id=google_stream["id"],
            campaign_id=campaign.id,
            name=google_stream["name"],
            position=google_stream["position"],
        )

        offer_stream_db = Stream(
            keitaro_id=offer_stream["id"],
            campaign_id=campaign.id,
            name=offer_stream["name"],
            position=offer_stream["position"],
        )

        self.db.add_all(
            [
                google_stream_db,
                offer_stream_db,
            ]
        )

        self.db.flush()

        offer = (
            self.db.query(Offer)
            .filter(
                Offer.keitaro_id == offer_keitaro_id,
            )
            .first()
        )

        if offer is None:
            offer = Offer(
                keitaro_id=offer_keitaro_id,
                name=offer_data["name"],
            )
            self.db.add(offer)
            self.db.flush()

        stream_offer = StreamOffer(
            stream_id=offer_stream_db.id,
            offer_id=offer.id,
            weight=100,
            is_pinned=False,
            status="active",
        )

        self.db.add(stream_offer)

        self.db.commit()

        return {
            "campaign": campaign_data,
            "google_stream": google_stream,
            "offer_stream": offer_stream,
        }
