from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from . import crud, schemas
from .database import SessionLocal

router = APIRouter(prefix="/movies", tags=["movies"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.MovieRead])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = Query(None),
    studio: Optional[str] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
    min_profitability: Optional[float] = Query(None),
    order_by: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_movies(
        db,
        skip=skip,
        limit=limit,
        genre=genre,
        studio=studio,
        year_min=year_min,
        year_max=year_max,
        min_profitability=min_profitability,
        order_by=order_by,
    )

@router.get("/{movie_id}", response_model=schemas.MovieRead)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    m = crud.get_movie(db, movie_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return m

@router.post("/", response_model=schemas.MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db), response: Response = None):
    m = crud.create_movie(db, movie)
    if m is None:
        raise HTTPException(status_code=400, detail="Movie with same title and year already exists")
    # set Location header
    if response is not None:
        response.headers["Location"] = f"/movies/{m.id}"
    return m

@router.put("/{movie_id}", response_model=schemas.MovieRead)
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db)):
    m = crud.update_movie(db, movie_id, movie)
    if m is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return m

@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_movie(db, movie_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Movie not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
