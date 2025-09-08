from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    poster_url = Column(String(500), nullable=True)
    overview = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)