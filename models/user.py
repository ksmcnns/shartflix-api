from database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    photo_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())