from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from models.user import User
from models.movie import Movie
from datetime import datetime

Base = declarative_base()

class Favorite(Base):
    __tablename__ = 'favorite_movies'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="favorites")
    movie = relationship("Movie", back_populates="favorites")