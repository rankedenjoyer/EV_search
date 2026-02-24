from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.event import Event
from app.models.odds import Odds

router = APIRouter()


@router.post("/odds")
async def insert_odds(data: dict, db: AsyncSession = Depends(get_db)):
    event = await db.get(Event, data["event_id"])

    if not event:
        event = Event(
            id=data["event_id"],
            sport="unknown",
            league="unknown",
            event_name="auto-created",
            start_time=None,
        )
        db.add(event)
        await db.flush()

    odds = Odds(
        event_id=data["event_id"],
        bookmaker=data["bookmaker"],
        outcome=data["outcome"],
        odds=data["odds"],
        timestamp=datetime.utcnow(),
    )

    db.add(odds)
    await db.commit()

    return {"status": "inserted"}
