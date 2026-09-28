from typing import Any, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class HomeItem(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    quantity: int = Field(ge=1, le=50)

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    room_type: str = Field(min_length=2, max_length=80)
    style: str = Field(default="Modern", max_length=80)
    items: list[HomeItem] = Field(default_factory=list, max_length=30)
    location: str = Field(default="India", max_length=100)
    notes: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(ge=1, le=5000)
    event_type: str = Field(min_length=2, max_length=80)
    venue: str = Field(default="Not decided", max_length=150)
    city: str = Field(default="", max_length=100)
    food_preference: str = Field(default="Mixed", max_length=100)
    notes: str = Field(default="", max_length=1000)

class RecommendationItem(BaseModel):
    category: str
    title: str
    description: str
    estimated_price: float
    quantity: int = 1
    platform: str
    url: str
    why: str

class RecommendationResponse(BaseModel):
    planner: Literal["home", "party", "jewelry"]
    budget: float
    allocated_budget: float
    summary: str
    tips: list[str]
    recommendations: list[RecommendationItem]
    source: Literal["gemini", "fallback"]
    history_id: int | None = None

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(default="Elegant", max_length=100)
    outfit_color: str = Field(default="Not specified", max_length=100)
    jewelry_type: str = Field(default="Any", max_length=100)
    notes: str = Field(default="", max_length=1000)

class SessionInfo(BaseModel):
    logged_in: bool
    user_id: int | None = None
    name: str | None = None
    email: str | None = None
