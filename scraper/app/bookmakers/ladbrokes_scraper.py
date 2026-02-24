import re
from datetime import datetime, timezone

from playwright.async_api import async_playwright  # type: ignore[import-not-found]

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
        patterns = [
            r"([A-Za-z0-9 .&'-]{2,})\s+vs\s+([A-Za-z0-9 .&'-]{2,})",
            r"([A-Za-z0-9 .&'-]{2,})\s+v\s+([A-Za-z0-9 .&'-]{2,})",
            r"([A-Za-z0-9 .&'-]{2,})\s+-\s+([A-Za-z0-9 .&'-]{2,})",
        ]
        for pattern in patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                return [match.group(1).strip(), match.group(2).strip()]
        return []

    @staticmethod
    def _extract_outcomes_from_buttons(button_texts, teams):
        outcomes: list[NormalizedOutcome] = []
        for raw in button_texts:
            text = " ".join(raw.split())
            odd = LadbrokesScraper._parse_decimal_odds(text)
            if odd is None:
                continue

            label = re.sub(r"\b\d+(?:\.\d{1,2})?\b", "", text).strip(" -:\n\t")
            if not label:
                label = f"Outcome {len(outcomes) + 1}"

            if teams:
                for team in teams:
                    if team.lower() in text.lower():
                        label = team
                        break

            outcomes.append(NormalizedOutcome(name=label, odds=odd))

        deduped = []
        seen = set()
        for outcome in outcomes:
            key = (outcome.name.lower(), outcome.odds)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(outcome)
        return deduped

    async def fetch_events(self):
        events: list[NormalizedEvent] = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.URL, wait_until="domcontentloaded", timeout=90000)
                try:
                    await page.wait_for_load_state("networkidle", timeout=30000)
                except Exception:
                    pass

                # Dismiss cookie/promo banners where possible.
                for selector in ["button:has-text('Accept')", "button:has-text('I Agree')", "button:has-text('Got it')"]:
                    try:
                        button = page.locator(selector).first
                        if await button.count() > 0:
                            await button.click(timeout=1000)
                    except Exception:
                        pass

                await page.wait_for_timeout(2000)

                # Scroll to trigger lazy rendering.
                for _ in range(3):
                    await page.mouse.wheel(0, 2500)
                    await page.wait_for_timeout(800)

                card_selector = ", ".join(
                    [
                        "[data-testid*='event']",
                        "[data-testid*='fixture']",
                        "[data-testid*='market-card']",
                        "[class*='event-card']",
                        "[class*='fixture']",
                        "article",
                    ]
                )
                cards = page.locator(card_selector)
                count = await cards.count()
                print(f"[ladbrokes] candidate cards={count}")

                for idx in range(count):
                    card = cards.nth(idx)
                    try:
                        card_text = await card.inner_text(timeout=2000)
                        if not card_text or len(card_text.strip()) < 8:
                            continue

                        teams = []
                        team_nodes = card.locator("[data-testid*='team'], [class*='team'], [class*='participant']")
                        team_count = await team_nodes.count()
                        for j in range(min(team_count, 8)):
                            value = (await team_nodes.nth(j).inner_text()).strip()
                            if value and value.lower() not in [t.lower() for t in teams]:
                                teams.append(value)
                            if len(teams) >= 2:
                                break

                        if len(teams) < 2:
                            teams = self._parse_teams(card_text)

                        if len(teams) < 2:
                            continue

                        button_nodes = card.locator("button, [data-testid*='price'], [class*='price'], [class*='odds']")
                        button_count = await button_nodes.count()
                        button_texts = []
                        for j in range(min(button_count, 16)):
                            txt = (await button_nodes.nth(j).inner_text()).strip()
                            if txt:
                                button_texts.append(txt)

                        outcomes = self._extract_outcomes_from_buttons(button_texts, teams)

                        # fallback: extract first decimal odds from card text and map to teams.
                        if len(outcomes) < 2:
                            odds = [float(x) for x in re.findall(r"\b\d+\.\d{1,2}\b", card_text) if float(x) >= 1.01]
                            if len(odds) >= 2:
                                outcomes = [
                                    NormalizedOutcome(name=teams[0], odds=round(odds[0], 2)),
                                    NormalizedOutcome(name=teams[1], odds=round(odds[1], 2)),
                                ]

                        if len(outcomes) < 2:
                            continue

                        league = "unknown"
                        league_nodes = card.locator("[data-testid*='competition'], [class*='competition'], [class*='league']")
                        if await league_nodes.count() > 0:
                            league = (await league_nodes.first.inner_text()).strip() or "unknown"

                        events.append(
                            NormalizedEvent(
                                sport="esports",
                                league=league,
                                teams=teams[:2],
                                start_time=datetime.now(timezone.utc),
                                bookmaker="ladbrokes",
                                outcomes=outcomes[:3],
                            )
                        )
                    except Exception as exc:
                        print(f"[ladbrokes] skip card {idx}: {exc}")
            finally:
                await browser.close()

        print(f"[ladbrokes] scraped {len(events)} events")
        return events
