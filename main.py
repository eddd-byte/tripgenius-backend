from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_hot_offers
from pydantic import BaseModel
from typing import List, Optional


init_db()


class TripCardV1(BaseModel):
    id: int
    raw_id: int

    origin_city_code: str
    origin_city_name: Optional[str] = None

    destination_city_name: Optional[str] = None
    country_to_code: str
    country_to_name: Optional[str] = None

    title: str
    subtitle: Optional[str] = None

    offer_type: str = "package"
    is_direct: Optional[bool] = None

    date_from: Optional[str] = None
    date_to: Optional[str] = None
    nights: Optional[int] = None

    price: int
    old_price: Optional[int] = None
    currency: str = "RUB"
    discount_percent: Optional[int] = None

    published_at: Optional[str] = None

    deal_url: Optional[str] = None
    image_url: Optional[str] = None

    source: Optional[str] = None
    source_label: Optional[str] = None


class DealsResponse(BaseModel):
    city_from: str
    country_to: str
    total: int
    deals: List[TripCardV1]


app = FastAPI(
    title="TripGenius Backend",
    description="API для поиска и выдачи горящих туров",
    version="0.1.0",
)

origins = [
    "http://localhost:3000",
    # сюда потом можно добавить URL фронта на Render или другом хостинге
    # "https://tripgenius-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "TripGenius API is running"}


@app.get("/api/deals", response_model=DealsResponse)
def get_deals(
    city_from: str = Query("spb", description="Код города вылета, например 'spb'"),
    country_to: str = Query("turkey", description="Код страны назначения, например 'turkey'"),
    limit: int = Query(50, ge=1, le=200, description="Максимум офферов в ответе"),
):
    rows = get_hot_offers(city_from=city_from, country_to=country_to, limit=limit)

    # Простые маппинги названий для первой версии
    city_name_map = {
        "spb": "Санкт-Петербург",
        "msk": "Москва",
        "nsk": "Новосибирск",
    }
    country_name_map = {
        "turkey": "Турция",
        "russia": "Россия",
        "egypt": "Египет",
    }

    origin_city_name = city_name_map.get(city_from, city_from)
    country_to_name = country_name_map.get(country_to, country_to)

    deals: List[TripCardV1] = []

    for row in rows:
        # row — dict из get_hot_offers (id, raw_id, city_from, city_to, country_to, ...)

        title = f"Тур из {origin_city_name} в {country_to_name}"
        if row.get("nights"):
            title += f", {row['nights']} ночей"

        subtitle_parts = []
        if row.get("date_from") and row.get("date_to"):
            subtitle_parts.append(f"{row['date_from']} — {row['date_to']}")
        if row.get("city_to"):
            subtitle_parts.append(f"Курорт: {row['city_to'].title()}")
        subtitle = " · ".join(subtitle_parts) if subtitle_parts else None

        deal = TripCardV1(
            id=row["id"],
            raw_id=row["raw_id"],
            origin_city_code=city_from,
            origin_city_name=origin_city_name,
            destination_city_name=row.get("city_to"),
            country_to_code=country_to,
            country_to_name=country_to_name,
            title=title,
            subtitle=subtitle,
            # Пока жёстко: все как пакетные туры, без прямых рейсов
            offer_type="package",
            is_direct=None,
            date_from=row.get("date_from"),
            date_to=row.get("date_to"),
            nights=row.get("nights"),
            price=row["price"],
            old_price=None,
            currency="RUB",
            discount_percent=None,
            published_at=row.get("created_at"),
            deal_url=None,     # позже сюда пойдут партнёрские ссылки Travelpayouts
            image_url=None,    # позже — картинки по направлениям
            source=row.get("source"),
            source_label=None,
        )
        deals.append(deal)

    return DealsResponse(
        city_from=city_from,
        country_to=country_to,
        total=len(deals),
        deals=deals,
    )
