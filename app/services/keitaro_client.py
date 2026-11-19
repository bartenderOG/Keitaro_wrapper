import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class KeitaroClient:
    def __init__(self):
        base_url = os.getenv("KEITARO_BASE_URL")
        api_token = os.getenv("KEITARO_API_TOKEN")

        if not base_url:
            raise RuntimeError("KEITARO_BASE_URL is not set")

        if not api_token:
            raise RuntimeError("KEITARO_API_TOKEN is not set")

        self.http = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/admin_api/v1",
            headers={
                "Api-Key": api_token,
            },
            timeout=20.0,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()



    async def get_campaigns(self):
        response = await self.http.get("/campaigns")
        response.raise_for_status()

        return response.json()

    async def get_streams(self, campaign_id: int):
        response = await self.http.get(
            f"/campaigns/{campaign_id}/streams"
        )
        response.raise_for_status()

        return response.json()

    async def get_domains(self):
        response = await self.http.get("/domains")
        response.raise_for_status()

        return response.json()

    async def get_groups(self, group_type: str = "campaigns"):
        response = await self.http.get(
            "/groups",
            params={"type": group_type},
        )
        response.raise_for_status()

        return response.json()

    async def get_traffic_sources(self):
        response = await self.http.get("/traffic_sources")
        response.raise_for_status()

        return response.json()

    async def get_offers(self):
        response = await self.http.get("/offers")
        response.raise_for_status()

        return response.json()

    async def create_campaign(
        self,
        name: str,
        alias: str,
        group_id: int,
        traffic_source_id: int,
        domain_id: int,
    ):
        response = await self.http.post(
            "/campaigns",
            json={
                "name": name,
                "alias": alias,
                "group_id": group_id,
                "traffic_source_id": traffic_source_id,
                "domain_id": domain_id,
            },
        )
        response.raise_for_status()

        return response.json()

    async def create_stream(
        self,
        campaign_id: int,
        name: str,
        schema: str,
        stream_type: str,
        action_type: str,
        action_payload: str = "",
        filters: list | None = None,
        offers: list | None = None,
    ):
        response = await self.http.post(
            "/streams",
            json={
                "campaign_id": campaign_id,
                "schema": schema,
                "type": stream_type,
                "name": name,
                "action_type": action_type,
                "action_payload": action_payload,
                "filters": filters or [],
                "offers": offers or [],
            },
        )
        response.raise_for_status()

        return response.json()





    async def get_stream_actions(self):
        response = await self.http.get("/streams_actions")
        response.raise_for_status()

        return response.json()

    async def get_stream_filters(self):
        response = await self.http.get("/stream_filters")
        response.raise_for_status()

        return response.json()

    async def update_stream(
        self,
        stream_id: int,
        offers: list[dict],
    ):
        response = await self.http.put(
            f"/streams/{stream_id}",
            json={
                "offers": offers,
            },
        )
        response.raise_for_status()
        return response.json()



    async def close(self):
        await self.http.aclose()
