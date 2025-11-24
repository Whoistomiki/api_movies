from pydantic import BaseModel, conint, confloat, constr
from typing import Optional

class MovieBase(BaseModel):
    title: constr(min_length=1)
    genre: constr(min_length=1)
    studio: Optional[str] = None
    audience_score: Optional[conint(ge=0, le=100)] = None
    profitability: Optional[confloat(ge=0)] = None
    rotten_tomatoes: Optional[conint(ge=0, le=100)] = None
    worldwide_gross: Optional[confloat(ge=0)] = None
    year: Optional[conint(ge=1900)] = None

class MovieCreate(MovieBase):
    pass

class MovieRead(MovieBase):
    id: int

    class Config:
        from_attributes = True

class MovieUpdate(BaseModel):
    title: Optional[constr(min_length=1)] = None
    genre: Optional[constr(min_length=1)] = None
    studio: Optional[str] = None
    audience_score: Optional[conint(ge=0, le=100)] = None
    profitability: Optional[confloat(ge=0)] = None
    rotten_tomatoes: Optional[conint(ge=0, le=100)] = None
    worldwide_gross: Optional[confloat(ge=0)] = None
    year: Optional[conint(ge=1900)] = None
