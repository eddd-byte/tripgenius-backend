# schemas.py
from datetime import date
from typing import Optional, Literal, Dict, Any, List
from pydantic import BaseModel

DealType = Literal["tour", "flight", "excursion", "train", "bus"]

class Deal(BaseModel):
    id: str
    type: DealType = "tour"

    city_from: str
    city_to: Optional[str] = None
    country_to: Optional[str] = None

    title: str
    subtitle: Optional[str] = None

    price: int
    currency: str = "RUB"

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    nights: Optional[int] = None
    people: Optional[int] = None  # пока в БД нет, останется None

    provider: str
    deep_link: str  # в БД пока нет, позже добавим колонку

    image_url: Optional[str] = None
    meta: Dict[str, Any] = {}

class DealsFilters(BaseModel):
    city_from: Optional[str] = None
    country_to: Optional[str] = None
    type: Optional[DealType] = None

class DealsV2Response(BaseModel):
    deals: List[Deal]
    filters: DealsFilters

