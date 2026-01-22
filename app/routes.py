from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from . import crud, schemas, models
from .database import SessionLocal

router = APIRouter(prefix="/movies", tags=["movies"])

# Liste des genres autorisés pour la règle métier (400)
ALLOWED_GENRES = ["Action", "Drama", "Comedy", "Sci-Fi", "Romance"]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---

@router.get("/", response_model=List[schemas.MovieRead])
def read_movies(
    # Pagination : /movies?page=1&limit=10
    page: int = Query(1, ge=1, description="Numéro de la page"),
    limit: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page"),
    # Tri : ?sort_by=year&order=asc
    sort_by: str = Query("id", description="Champ sur lequel trier"),
    order: str = Query("asc", regex="^(asc|desc)$", description="Ordre asc ou desc"),
    # Filtres
    min_year: Optional[int] = Query(None, description="Filtrer les films à partir de cette année"),
    genre: Optional[str] = Query(None, description="Filtrer par genre (Option Bonus)"),
    db: Session = Depends(get_db),
):
    """
    Retourne la liste des films avec filtrage, pagination et tri dynamique.
    """
    skip = (page - 1) * limit
    
    # Construction de la requête de base
    query = db.query(models.Movie)
    
    # Application des filtres
    if genre:
        query = query.filter(models.Movie.genre == genre)
    if min_year:
        query = query.filter(models.Movie.year >= min_year)
        
    # Application du tri dynamique
    try:
        column = getattr(models.Movie, sort_by)
        if order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    except AttributeError:
        # Tri par défaut si le champ sort_by est invalide
        query = query.order_by(models.Movie.id.asc())

    return query.offset(skip).limit(limit).all()

@router.get("/{movie_id}", response_model=schemas.MovieRead)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Renvoie 404 si le film est inexistant.
    """
    m = crud.get_movie(db, movie_id)
    if m is None:
        raise HTTPException(status_code=404, detail=f"Film avec l'ID {movie_id} introuvable.")
    return m

@router.post("/", response_model=schemas.MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db), response: Response = None):
    """
    Valide les données, vérifie les doublons (409) et applique les règles métier (400).
    """
    
    # --- VÉRIFIER DOUBLONS (Titre + Année) -> Erreur 409 ---
    existing = db.query(models.Movie).filter(
        models.Movie.title == movie.title, 
        models.Movie.year == movie.year
    ).first()
    if existing:
        raise HTTPException(
            status_code=409, 
            detail=f"Conflit : Le film '{movie.title}' ({movie.year}) existe déjà."
        )

    # --- RÈGLES MÉTIER (Erreurs 400) ---
    
    # 1. Année > année actuelle
    if movie.year > datetime.now().year:
        raise HTTPException(status_code=400, detail="L'année ne peut pas être dans le futur.")
    
    # 2. Genre non autorisé
    if movie.genre not in ALLOWED_GENRES:
        raise HTTPException(status_code=400, detail=f"Genre non autorisé. Liste autorisée : {ALLOWED_GENRES}")

    # 3. Rotten Tomatoes % > 10
    if movie.rotten_tomatoes > 10:
        raise HTTPException(status_code=400, detail="Le score Rotten Tomatoes ne peut pas dépasser 10%.")

    # 4. Audience score = 0 pour un film récent (>= 2024)
    if movie.year >= 2024 and movie.audience_score == 0:
        raise HTTPException(status_code=400, detail="Un film récent ne peut pas avoir un score d'audience de 0%.")

    # --- CRÉATION ---
    m = crud.create_movie(db, movie)
    if response is not None:
        response.headers["Location"] = f"/movies/{m.id}"
    return m

@router.put("/{movie_id}", response_model=schemas.MovieRead)
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db)):
    """
    Mise à jour partielle ou complète avec validation métier (400) et existence (404).
    """
    
    # Validation du genre si fourni dans l'update (Règle 400)
    if movie.genre is not None and movie.genre not in ALLOWED_GENRES:
        raise HTTPException(status_code=400, detail="Genre non autorisé pour la mise à jour.")

    m = crud.update_movie(db, movie_id, movie)
    
    # Erreur 404 si film inexistant
    if m is None:
        raise HTTPException(status_code=404, detail="Modification impossible : film inexistant.")
    return m

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Supprime un film et renvoie 204 No Content.
    """
    ok = crud.delete_movie(db, movie_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Suppression impossible : film inexistant.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/debug-crash")
def cause_error():
    # Force une division par zéro (Error Python brute)
    return 1 / 0