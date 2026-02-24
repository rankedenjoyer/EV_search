import asyncio
import os

import httpx  # type: ignore[import-not-found]

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
            print(
                f"[scraper] Backend not ready ({response.status_code}). "
                f"Retrying in {RETRY_DELAY_SECONDS}s..."
            )
        except Exception as exc:
            print(f"[scraper] Backend check failed: {exc}. Retrying in {RETRY_DELAY_SECONDS}s...")

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


async def post_startup_test(client: httpx.AsyncClient) -> None:
    test_payload = {
        "canonical_key": "startup__vs__probe",
        "sport": "esports",
        "league": "startup-check",
        "bookmaker": "ladbrokes",
        "outcomes": [
            {"name": "startup", "odds": 2.0},
            {"name": "probe", "odds": 1.8},
        ],
    }

    response = await client.post(POST_ODDS_URL, json=test_payload, timeout=10.0)
    print(f"[scraper] startup POST /odds status={response.status_code} body={response.text}")
    if response.status_code != 200:
        raise RuntimeError(f"startup POST failed with status={response.status_code} body={response.text}")


async def ingestion_loop() -> None:
    print("[scraper] starting up ...")
    print(f"[scraper] BACKEND_URL={BACKEND_URL} POST_ODDS_URL={POST_ODDS_URL}")

    scrapers = [
        LadbrokesScraper(),
    ]

    async with httpx.AsyncClient() as client:
        await wait_for_backend(client)
        await post_startup_test(client)

        while True:
            for scraper in scrapers:
                try:
                    events = await scraper.fetch_events()
                except Exception as exc:
                    print(f"[scraper] fetch failed for {scraper.__class__.__name__}: {exc}")
                    continue

                for event in events:
                    payload = event_to_payload(event)
                    try:
                        response = await client.post(POST_ODDS_URL, json=payload, timeout=10.0)
                        print(
                            f"[scraper] POST /odds status={response.status_code} "
                            f"bookmaker={payload['bookmaker']} key={payload['canonical_key']}"
                        )
                        if response.status_code != 200:
                            print(f"[scraper] POST failure body={response.text}")
                    except Exception as exc:
                        print(f"[scraper] Error posting odds: {exc}")

            await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(ingestion_loop())
