import os
import csv
import logging
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./movies.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# logger
logger = logging.getLogger("app.database")
if not logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(levelname)s:%(name)s: %(message)s")
    h.setFormatter(fmt)
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

def init_db():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)

def _parse_int(value: Optional[str]) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except Exception:
        return None

def _parse_float(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None

def _parse_money(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    # remove $ and commas and spaces
    s = s.replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except Exception:
        return None

def seed_from_csv(csv_path: str, max_inserts: Optional[int] = None):
    """Read CSV and populate the `movies` table.

    - Ignores duplicates (same title case-insensitive + same year)
    - Normalises fields (removes $, converts gross to float, scores to int)
    - Logs invalid rows but continues
    - If `max_inserts` is provided, stops after inserting that many valid rows

    Returns a dict with stats: inserted, skipped_duplicates, invalid
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    # avoid circular import at top-level
    from .models import Movie

    init_db()
    session = SessionLocal()
    inserted = 0
    skipped = 0
    invalid = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                film_raw = row.get('Film')
                if not film_raw:
                    logger.warning(f"Line {i}: missing Film title - skipping")
                    invalid += 1
                    continue
                title = film_raw.strip()
                genre = (row.get('Genre') or '').strip()
                studio = (row.get('Lead Studio') or '').strip()
                audience = _parse_int(row.get('Audience score %'))
                profitability = _parse_float(row.get('Profitability'))
                rotten = _parse_int(row.get('Rotten Tomatoes %'))
                gross = _parse_money(row.get('Worldwide Gross'))
                year = _parse_int(row.get('Year'))

                # Year is required to check duplicates; if missing, log and skip
                if year is None:
                    logger.warning(f"Line {i}: invalid or missing Year for '{title}' - skipping")
                    invalid += 1
                    continue

                # check duplicate (case-insensitive title + same year)
                existing = session.query(Movie).filter(
                    Movie.year == year,
                ).all()
                duplicate_found = False
                title_lower = title.lower()
                for ex in existing:
                    if (ex.title or '').strip().lower() == title_lower:
                        duplicate_found = True
                        break

                if duplicate_found:
                    skipped += 1
                    continue

                m = Movie(
                    title=title,
                    genre=genre,
                    studio=studio,
                    audience_score=audience,
                    profitability=profitability,
                    rotten_tomatoes=rotten,
                    worldwide_gross=gross,
                    year=year,
                )
                session.add(m)
                # if max_inserts is set, stop when reached
                if max_inserts is not None and inserted >= max_inserts:
                    break
                inserted += 1
            except Exception as e:
                logger.warning(f"Line {i}: error parsing row for '{row.get('Film', '')}': {e}")
                invalid += 1
                continue
    session.commit()
    session.close()
    logger.info(f"Seeding complete: inserted={inserted} skipped_duplicates={skipped} invalid={invalid}")
    return {"inserted": inserted, "skipped": skipped, "invalid": invalid}
