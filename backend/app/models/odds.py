from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from app.db.database import Base


class Odds(Base):
    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    bookmaker = Column(String)
    outcome = Column(String)
    odds = Column(Float)
    timestamp = Column(DateTime)
