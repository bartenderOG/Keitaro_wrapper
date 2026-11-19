import asyncio

from app.db.session import SessionLocal
from app.models.campaign import Campaign
from app.services.keitaro_client import KeitaroClient
from app.services.sync_service import SyncService


async def main():
    db = SessionLocal()

    try:
        campaign = db.query(Campaign).first()

        if campaign is None:
            print("Кампаний в локальной БД нет")
            return

        print(
            f"Синхронизируем streams кампании: "
            f"{campaign.name} "
            f"(Keitaro ID: {campaign.keitaro_id})"
        )

        async with KeitaroClient() as keitaro:
            service = SyncService(db, keitaro)

            await service.sync_streams(campaign)

        print("Синхронизация streams завершена")

    finally:
        db.close()


asyncio.run(main())
