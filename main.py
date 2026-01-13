from fastapi import FastAPI
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
    city_from: str = "spb",
):
    # Заглушка с одним примером тура — под фронт можно будет расширить
    return {
        "city_from": city_from,
        "deals": [
            {
                "id": 1,
                "title": "СПб → Байкал, 7 дней, 18 500 ₽",
                "price": 18500,
                "nights": 7,
                "date_from": "2025-02-10",
                "date_to": "2025-02-17",
            }
        ],
    }

