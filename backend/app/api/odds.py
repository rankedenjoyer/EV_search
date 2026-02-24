from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.odds import Odds

router = APIRouter()


@router.post("/odds")
async def insert_odds(data: dict, db: AsyncSession = Depends(get_db)):
    odds = Odds(
        event_id=data["event_id"],
        bookmaker=data["bookmaker"],
        outcome=data["outcome"],
        odds=data["odds"],
        timestamp=datetime.utcnow()
    )

    db.add(odds)
    await db.commit()

    return {"status": "inserted"}
