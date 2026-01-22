from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from .routes import router as movies_router
from .database import init_db, SessionLocal
from .database import logger as db_logger
from .database import seed_from_csv
import os
import logging
import time

# --- LOGGING D'ERREURS DANS UN FICHIER ---
# Configure le log pour enregistrer les erreurs dans 'errors.log'
logging.basicConfig(
    filename='errors.log',
    level=logging.ERROR,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

app = FastAPI(title="Movies API")

# --- MIDDLEWARE GLOBAL DE GESTION D'ERREURS ---
# Intercepte toute exception Python pour renvoyer un JSON propre
@app.middleware("http")
async def global_exception_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Log les détails demandés : date, endpoint, type d'erreur
        logging.error(f"Endpoint: {request.url} | Type: {type(e).__name__} | Detail: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Une erreur interne est survenue. Consultez le fichier errors.log."}
        )

app.include_router(movies_router)

# --- ENDPOINT /health ---
@app.get("/health", tags=["System"])
def health_check():
    """Renvoie l'état de l'API et le nombre de films."""
    db = SessionLocal()
    try:
        from . import models
        count = db.query(models.Movie).count()
        return {
            "status": "healthy",
            "movies_count": count,
            "server_time": time.ctime()
        }
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()
    from . import models
    db = SessionLocal()
    try:
        count = db.query(models.Movie).count()
    except Exception as e:
        db_logger.warning(f"Could not check movies count: {e}")
        count = 0
    finally:
        db.close()

    if not count:
        project_root = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(project_root, 'data', 'movies.csv')
        try:
            limit_env = os.getenv('AUTO_SEED_LIMIT')
            max_inserts = int(limit_env) if limit_env is not None else None
        except Exception:
            max_inserts = None

        try:
            stats = seed_from_csv(csv_path, max_inserts=max_inserts)
            db_logger.info(f"Auto-seed stats: {stats}")
        except Exception as e:
            db_logger.warning(f"Error during auto-seed: {e}")

@app.get("/")
def root():
    return {"message": "Welcome to the API Movies"}