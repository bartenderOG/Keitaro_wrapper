import asyncio

from app.db.session import SessionLocal
from app.services.campaign_creator import CampaignCreator
from app.services.keitaro_client import KeitaroClient


async def main():
    db = SessionLocal()

    try:
        async with KeitaroClient() as keitaro:
            creator = CampaignCreator(
                db=db,
                keitaro=keitaro,
            )

            result = await creator.create_campaign(
                name="test_nasirdinov_creator_20261119",
                geo_code="AU",
                offer_keitaro_id=18813,
                domain_id=1813,
                group_id=10332,
                traffic_source_id=836,
            )

            print("CAMPAIGN CREATED:")
            print(result["campaign"])

            print("\nGOOGLE STREAM:")
            print(result["google_stream"])

            print("\nOFFER STREAM:")
            print(result["offer_stream"])

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())