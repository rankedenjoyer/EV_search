import asyncio
import os

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
POST_ODDS_URL = f"{BACKEND_URL.rstrip('/')}/odds"
INTERVAL_SECONDS = 30
RETRY_DELAY_SECONDS = 5

PAYLOAD = {
    "event_id": 1,
    "bookmaker": "ladbrokes",
    "outcome": "Team A",
    "odds": 2.1,
}


async def wait_for_backend(client: httpx.AsyncClient) -> None:
    health_url = f"{BACKEND_URL.rstrip('/')}/health"

    while True:
        try:
            response = await client.get(health_url, timeout=5.0)
            if response.status_code == 200:
                print(f"[scraper] Backend available at {health_url}")
                return
            print(
                f"[scraper] Backend not ready ({response.status_code}). "
                f"Retrying in {RETRY_DELAY_SECONDS}s..."
            )
        except Exception as exc:
            print(f"[scraper] Backend check failed: {exc}. Retrying in {RETRY_DELAY_SECONDS}s...")

        await asyncio.sleep(RETRY_DELAY_SECONDS)


async def ingestion_loop() -> None:
    async with httpx.AsyncClient() as client:
        await wait_for_backend(client)

        while True:
            try:
                response = await client.post(POST_ODDS_URL, json=PAYLOAD, timeout=10.0)
                if response.status_code == 200:
                    print(f"[scraper] Inserted odds successfully: {PAYLOAD}")
                else:
                    print(
                        f"[scraper] Failed to insert odds. "
                        f"status={response.status_code} body={response.text}"
                    )
            except Exception as exc:
                print(f"[scraper] Error posting odds: {exc}")

            await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(ingestion_loop())
