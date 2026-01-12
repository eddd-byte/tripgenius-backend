from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TripGenius Backend",
    description="API для поиска и выдачи горящих туров",
    version="0.1.0",
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/deals")
def get_deals(city_from: str = "spb"):
    return {
        "city_from": city_from,
        "deals": [
            {
                "id": 1,
                "title": "СПб → Байкал, 7 дней, 18 500 ₽",
                "price": 18500,
                "nights": 7,
            }
        ],
    }

