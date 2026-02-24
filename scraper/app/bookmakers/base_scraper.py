class BaseScraper:
    async def fetch_events(self):
        raise NotImplementedError
