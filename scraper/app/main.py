import asyncio
import os

import httpx

from app.bookmakers.ladbrokes_scraper import LadbrokesScraper
from app.normalizer import canonical_key

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
POST_ODDS_URL = f"{BACKEND_URL.rstrip('/')}/odds"

INTERVAL_SECONDS = 30
RETRY_DELAY_SECONDS = 5


async def wait_for_backend(client: httpx.AsyncClient) -> None:
    health_url = f"{BACKEND_URL.rstrip('/')}/health"

    while True:
        try:
            response = await client.get(health_url, timeout=5.0)
            if response.status_code == 200:
                print(f"[scraper] Backend available at {health_url}")
                return
        except Exception as exc:
            print(f"[scraper] Backend check failed: {exc}")

        await asyncio.sleep(RETRY_DELAY_SECONDS)


def event_to_payload(event):
    return {
        "canonical_key": canonical_key(event.teams[0], event.teams[1]),
        "sport": event.sport,
        "league": event.league,
        "bookmaker": event.bookmaker,
        "outcomes": [
            {"name": outcome.name, "odds": outcome.odds}
            for outcome in event.outcomes
        ],
    }


async def ingestion_loop():
    scrapers = [
        LadbrokesScraper(),
    ]

    async with httpx.AsyncClient() as client:
        await wait_for_backend(client)

        while True:
            for scraper in scrapers:
                try:
                    events = await scraper.fetch_events()
                except Exception as exc:
                    print(f"[scraper] fetch failed: {exc}")
                    continue

                for event in events:
                    payload = event_to_payload(event)

                    try:
                        response = await client.post(
                            POST_ODDS_URL,
                            json=payload,
                            timeout=10.0,
                        )
                        print(
                            f"[scraper] POST status={response.status_code} "
                            f"key={payload['canonical_key']}"
                        )
                    except Exception as exc:
                        print(f"[scraper] POST error: {exc}")

            await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(ingestion_loop())
