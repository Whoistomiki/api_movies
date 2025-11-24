from sqlalchemy import Column, Integer, String, Float, CheckConstraint
from .database import Base

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String, index=True)
    studio = Column(String, index=True)
    audience_score = Column(Integer, nullable=True)
    profitability = Column(Float, nullable=True)
    rotten_tomatoes = Column(Integer, nullable=True)
    worldwide_gross = Column(Float, nullable=True)
    year = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint('year >= 1900', name='ck_year_min'),
        CheckConstraint('audience_score >= 0 AND audience_score <= 100', name='ck_audience_range'),
        CheckConstraint('rotten_tomatoes >= 0 AND rotten_tomatoes <= 100', name='ck_rotten_range'),
        CheckConstraint('profitability >= 0', name='ck_profitability_nonneg'),
    )
