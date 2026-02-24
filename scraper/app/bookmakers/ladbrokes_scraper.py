from datetime import datetime, timezone

from app.bookmakers.base_scraper import BaseScraper
from app.models.normalized_event import NormalizedEvent, NormalizedOutcome


class LadbrokesScraper(BaseScraper):
    async def fetch_events(self):
        # Minimal real-pipeline scaffolding: this should be replaced with actual
        # Ladbrokes DOM/API extraction logic in the next iteration.
        events = [
            NormalizedEvent(
                sport="esports",
                league="LPL",
                teams=["T1", "LNG"],
                start_time=datetime.now(timezone.utc),
                bookmaker="ladbrokes",
                outcomes=[
                    NormalizedOutcome(name="T1", odds=2.1),
                    NormalizedOutcome(name="LNG", odds=1.75),
                ],
            )
        ]
        print(f"[ladbrokes] scraped {len(events)} events")
        return events
