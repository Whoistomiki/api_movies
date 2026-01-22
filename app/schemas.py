from pydantic import BaseModel, Field
from typing import Optional

class MovieBase(BaseModel):
    # Validation de format (422 si non respecté)
    title: str = Field(..., min_length=2, max_length=120)
    genre: str 
    studio: str = Field(..., min_length=2)
    # Valeurs par défaut à 0 comme demandé
    audience_score: int = Field(0, ge=0, le=100)
    rotten_tomatoes: int = Field(0, ge=0, le=100)
    year: int = Field(..., ge=1900)
    profitability: Optional[float] = Field(None, ge=0)
    worldwide_gross: Optional[float] = Field(None, ge=0)

class MovieCreate(MovieBase):
    pass

class MovieRead(MovieBase):
    id: int
    class Config:
        from_attributes = True

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=120)
    genre: Optional[str] = None
    studio: Optional[str] = Field(None, min_length=2)
    audience_score: Optional[int] = Field(None, ge=0, le=100)
    rotten_tomatoes: Optional[int] = Field(None, ge=0, le=100)
    year: Optional[int] = Field(None, ge=1900)