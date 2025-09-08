from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from database import get_db
from models.user import User
from models.movie import Movie
# Model adını düzelt: Eğer dosya favorite.py ise, import Favorite; yoksa FavoriteMovie tut
from models.favorite import Favorite  # Veya from models.favoriteMovie import FavoriteMovie
from routes.auth import get_current_user
from schemas.movie import MovieResponse

router = APIRouter(tags=["movies"])  # Prefix yok

@router.get("/movie/list", response_model=List[MovieResponse])
def get_movie_list(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: str = Depends(get_current_user)  # Eğer patlıyorsa, geçici kaldır
):
    # User kontrolü (eğer dependency patlarsa buraya gelmez)
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    movies = db.query(Movie).offset(skip).limit(limit).all()

    # Favori ID'leri al (model adını uyarla)
    favorite_ids = {
        fav.movie_id for fav in db.query(Favorite.movie_id)  # FavoriteMovie → Favorite
        .filter(Favorite.user_id == user.id)
        .all()
    }

    response_movies = []
    for movie in movies:
        response = MovieResponse(
            id=movie.id,
            title=movie.title,
            poster_url=movie.poster_url,
            overview=movie.overview,
            created_at=movie.created_at,
            is_favorite=movie.id in favorite_ids
        )
        response_movies.append(response)

    return response_movies

# Diğer endpoint'ler aynı, ama model adını düzelt (FavoriteMovie → Favorite)
@router.post("/movie/favorite/{movie_id}")
def toggle_favorite(
    movie_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    existing_fav = db.query(Favorite).filter(  # Düzelt
        Favorite.user_id == user.id,
        Favorite.movie_id == movie_id
    ).first()

    if existing_fav:
        db.delete(existing_fav)
        db.commit()
        return {"message": "Favorite removed"}
    else:
        new_fav = Favorite(
            user_id=user.id,
            movie_id=movie_id,
            created_at=datetime.utcnow()
        )
        db.add(new_fav)
        db.commit()
        db.refresh(new_fav)
        return {"message": "Favorite added"}

@router.get("/movie/favorites", response_model=List[MovieResponse])
def get_favorite_movies(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    favorites = db.query(Favorite).filter(Favorite.user_id == user.id).options(
        joinedload(Favorite.movie)
    ).offset(skip).limit(limit).all()

    response_movies = []
    for fav in favorites:
        if fav.movie:
            response = MovieResponse(
                id=fav.movie.id,
                title=fav.movie.title,
                poster_url=fav.movie.poster_url,
                overview=fav.movie.overview,
                created_at=fav.movie.created_at,
                is_favorite=True
            )
            response_movies.append(response)

    return response_movies