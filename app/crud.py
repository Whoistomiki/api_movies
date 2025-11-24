from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from . import models, schemas

def get_movie(db: Session, movie_id: int) -> Optional[models.Movie]:
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def get_movies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = None,
    studio: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    min_profitability: Optional[float] = None,
    order_by: Optional[str] = None,
) -> List[models.Movie]:
    q = db.query(models.Movie)
    if genre:
        q = q.filter(models.Movie.genre == genre)
    if studio:
        q = q.filter(models.Movie.studio == studio)
    if year_min is not None:
        q = q.filter(models.Movie.year >= year_min)
    if year_max is not None:
        q = q.filter(models.Movie.year <= year_max)
    if min_profitability is not None:
        q = q.filter(models.Movie.profitability >= min_profitability)

    # ordering
    if order_by:
        col = None
        direction = asc
        if order_by.startswith("-"):
            direction = desc
            key = order_by[1:]
        else:
            key = order_by
        if hasattr(models.Movie, key):
            col = getattr(models.Movie, key)
            q = q.order_by(direction(col))

    return q.offset(skip).limit(limit).all()

def create_movie(db: Session, movie: schemas.MovieCreate) -> Optional[models.Movie]:
    # prevent duplicate title+year
    title = movie.title.strip() if movie.title else ''
    year = movie.year
    if title and year is not None:
        exists = (
            db.query(models.Movie)
            .filter(models.Movie.year == year)
            .filter(models.Movie.title.ilike(title))
            .first()
        )
        if exists:
            return None

    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def update_movie(db: Session, movie_id: int, movie: schemas.MovieUpdate) -> Optional[models.Movie]:
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return None
    update_data = movie.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_movie, k, v)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def delete_movie(db: Session, movie_id: int) -> bool:
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return False
    db.delete(db_movie)
    db.commit()
    return True
