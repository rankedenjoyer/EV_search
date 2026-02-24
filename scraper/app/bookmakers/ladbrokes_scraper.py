import re
from datetime import datetime, timezone

from playwright.async_api import async_playwright

from app.bookmakers.base_scraper import BaseScraper
from app.models.normalized_event import NormalizedEvent, NormalizedOutcome


class LadbrokesScraper(BaseScraper):
    URL = "https://www.ladbrokes.com.au/sports/esports"

    @staticmethod
    def _parse_decimal_odds(text: str):
        match = re.search(r"\b(\d+(?:\.\d{1,2})?)\b", text)
        if not match:
            return None
        value = float(match.group(1))
        if value < 1.01:
            return None
        return round(value, 2)

    @staticmethod
    def _parse_teams(text: str):
        cleaned = " ".join(text.split())
        parts = re.split(r"\s(?:vs|v|-)\s", cleaned, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            return [parts[0].strip(), parts[1].strip()]
        return []

    async def fetch_events(self):
        events: list[NormalizedEvent] = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.URL, wait_until="networkidle", timeout=90000)
                await page.wait_for_timeout(2500)

                cards = page.locator(
                    "[data-testid*='event'], [data-testid*='fixture'], "
                    "article, [class*='event'], [class*='fixture']"
                )
                count = await cards.count()

                for idx in range(count):
                    card = cards.nth(idx)
                    try:
                        card_text = await card.inner_text(timeout=2000)
                        if not card_text or len(card_text) < 8:
                            continue

                        teams = []
                        team_candidates = card.locator(
                            "[data-testid*='team'], [class*='team'], [class*='participant']"
                        )
                        team_count = await team_candidates.count()
                        for j in range(min(team_count, 6)):
                            value = (await team_candidates.nth(j).inner_text()).strip()
                            if value and len(value) > 1 and value.lower() not in [t.lower() for t in teams]:
                                teams.append(value)
                            if len(teams) >= 2:
                                break

                        if len(teams) < 2:
                            teams = self._parse_teams(card_text)
                        if len(teams) < 2:
                            continue

                        odds_nodes = card.locator(
                            "button, [data-testid*='price'], [class*='price'], [class*='odds']"
                        )
                        odds_count = await odds_nodes.count()
                        outcomes: list[NormalizedOutcome] = []

                        for j in range(min(odds_count, 12)):
                            node_text = (await odds_nodes.nth(j).inner_text()).strip()
                            if not node_text:
                                continue

                            odd = self._parse_decimal_odds(node_text)
                            if odd is None:
                                continue

                            name = None
                            for team in teams:
                                if team.lower() in node_text.lower():
                                    name = team
                                    break

                            if not name:
                                compact = " ".join(node_text.split())
                                compact = re.sub(r"\b\d+(?:\.\d{1,2})?\b", "", compact).strip(" -:\n\t")
                                name = compact or f"Outcome {len(outcomes) + 1}"

                            outcomes.append(NormalizedOutcome(name=name, odds=odd))

                        deduped: list[NormalizedOutcome] = []
                        seen = set()
                        for out in outcomes:
                            key = (out.name.lower(), out.odds)
                            if key in seen:
                                continue
                            seen.add(key)
                            deduped.append(out)

                        if len(deduped) < 2:
                            continue

                        league = "unknown"
                        league_node = card.locator(
                            "[data-testid*='competition'], [class*='competition'], [class*='league']"
                        )
                        if await league_node.count() > 0:
                            league = (await league_node.first.inner_text()).strip() or "unknown"

                        events.append(
                            NormalizedEvent(
                                sport="esports",
                                league=league,
                                teams=teams[:2],
                                start_time=datetime.now(timezone.utc),
                                bookmaker="ladbrokes",
                                outcomes=deduped[:3],
                            )
                        )
                    except Exception as exc:
                        print(f"[ladbrokes] skip card {idx}: {exc}")
            finally:
                await browser.close()

        print(f"[ladbrokes] scraped {len(events)} events")
        return events
