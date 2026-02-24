from datetime import datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.event import Event

router = APIRouter()


@router.get("/events/today")
async def get_today_events(db: AsyncSession = Depends(get_db)):
    today = datetime.utcnow().date()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    query = select(Event).where(Event.start_time >= start, Event.start_time <= end)
    result = await db.execute(query)
    events = result.scalars().all()

    return [
        {
            "id": event.id,
            "sport": event.sport,
            "league": event.league,
            "event_name": event.event_name,
            "start_time": event.start_time,
        }
        for event in events
    ]
