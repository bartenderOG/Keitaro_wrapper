import asyncio

from app.db.session import SessionLocal
from app.services.keitaro_client import KeitaroClient
from app.services.sync_service import SyncService


async def main():
    db = SessionLocal()

    try:
        async with KeitaroClient() as keitaro:
            service = SyncService(db, keitaro)

            await service.sync_campaigns()

        print("Синхронизация кампаний завершена")

    finally:
        db.close()


asyncio.run(main())
