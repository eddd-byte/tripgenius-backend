from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_hot_offers

init_db()

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


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/deals")
def get_deals(
    city_from: str = Query("spb", description="Код города вылета, например 'spb'"),
    country_to: str = Query("turkey", description="Код страны назначения, например 'turkey'"),
    limit: int = Query(50, ge=1, le=200, description="Максимум офферов в ответе"),
):
    """
    Возвращает горячие туры из offers_hot для заданных city_from и country_to.
    Пример: /api/deals?city_from=spb&country_to=turkey
    """
    deals = get_hot_offers(city_from=city_from, country_to=country_to, limit=limit)

    return {
        "city_from": city_from,
        "country_to": country_to,
        "deals": deals,
    }

