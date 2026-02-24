from fastapi import FastAPI
from sqlalchemy import text

from app.api.events import router as events_router
from app.api.odds import router as odds_router
from app.db.database import engine, Base
from app.models.event import Event  # noqa: F401
from app.models.odds import Odds  # noqa: F401

app = FastAPI()
app.include_router(odds_router)
app.include_router(events_router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"status": "backend running"}


@app.get("/health")
async def health():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}
