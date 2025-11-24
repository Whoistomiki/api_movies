from fastapi import FastAPI
from .routes import router as movies_router
from .database import init_db, SessionLocal
from .database import logger as db_logger
from .database import seed_from_csv
import os
import typing

app = FastAPI(title="Movies API")
app.include_router(movies_router)

@app.on_event("startup")
def on_startup():
    init_db()
    # auto-seed if table empty (import part of dataset)
    # use ORM count to avoid textual SQL warnings
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
        # assume CSV at project root
        project_root = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(project_root, 'data', 'movies.csv')
        # optionally limit automatic import size via env AUTO_SEED_LIMIT
        try:
            limit_env = os.getenv('AUTO_SEED_LIMIT')
            max_inserts = int(limit_env) if limit_env is not None else None
        except Exception:
            max_inserts = None

        try:
            stats = seed_from_csv(csv_path, max_inserts=max_inserts)
            db_logger.info(f"Auto-seed stats: {stats}")
        except FileNotFoundError:
            db_logger.warning(f"CSV file not found for auto-seed: {csv_path}")
        except Exception as e:
            db_logger.warning(f"Error during auto-seed: {e}")

@app.get("/")
def root():
    return {"message": "Welcome to the API Movies"}
