import asyncio

from app.bookmakers.ladbrokes_scraper import LadbrokesScraper


async def main():
    scraper = LadbrokesScraper()
    events = await scraper.fetch_events()

    print(f"total_events={len(events)}")
    for event in events[:3]:
        print(f"{event.league} | {' vs '.join(event.teams)}")
        for outcome in event.outcomes:
            print(f"  - {outcome.name}: {outcome.odds}")


if __name__ == "__main__":
    asyncio.run(main())
