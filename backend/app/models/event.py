from sqlalchemy import Column, Integer, String, DateTime
from app.db.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String)
    league = Column(String)
    event_name = Column(String)
    start_time = Column(DateTime)
