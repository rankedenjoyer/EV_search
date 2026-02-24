from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.event import Event
from app.models.odds import Odds

router = APIRouter()


@router.post("/odds")
async def insert_odds(data: dict, db: AsyncSession = Depends(get_db)):
    canonical = data.get("canonical_key")
    outcomes = data.get("outcomes")

    if canonical and outcomes:
        result = await db.execute(select(Event).where(Event.canonical_key == canonical))
        event = result.scalar_one_or_none()

        if not event:
            teams = canonical.split("__vs__")
            event_name = " vs ".join(t.upper() for t in teams)
            event = Event(
                sport=data.get("sport", "unknown"),
                league=data.get("league", "unknown"),
                event_name=event_name,
                start_time=datetime.utcnow(),
                canonical_key=canonical,
            )
            db.add(event)
            await db.flush()

        for outcome in outcomes:
            db.add(
                Odds(
                    event_id=event.id,
                    bookmaker=data["bookmaker"],
                    outcome=outcome["name"],
                    odds=outcome["odds"],
                    timestamp=datetime.utcnow(),
                )
            )

        await db.commit()
        return {"status": "inserted", "event_id": event.id, "outcomes": len(outcomes)}

    event = await db.get(Event, data.get("event_id"))

    if not event:
        raise HTTPException(status_code=400, detail="event_id not found and canonical payload missing")

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
