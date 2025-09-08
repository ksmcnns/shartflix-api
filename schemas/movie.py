from pydantic import BaseModel
from typing import Optional

class MovieCreate(BaseModel):
    id: str
    title: str
    poster_url: Optional[str] = None
    is_favorite: bool = False

class MovieResponse(BaseModel):
    id: str
    title: str
    poster_url: Optional[str] = None
    is_favorite: bool

    class Config:
        orm_mode = True