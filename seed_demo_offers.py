# seed_demo_offers.py
"""
Заполняет БД демо-данными:
- добавляет несколько офферов в offers_raw
- переносит подходящие (горящие) в offers_hot по правилам:
    price < 30000
    3 <= nights <= 14
После запуска /api/deals?city_from=spb&country_to=turkey
должен начать отдавать минимум один реальный оффер.
"""

from database import init_db, insert_raw_offer, get_raw_offers, insert_hot_offer_from_raw


def is_hot(raw_row) -> bool:
    price = raw_row["price"]
    nights = raw_row["nights"]

    if price is None or nights is None:
        return False

    if price >= 30000:
        return False

    if nights < 3 or nights > 14:
        return False

    return True


def seed_raw_offers():
    """
    Добавляет несколько тестовых туров spb -> turkey в offers_raw.
    """
    init_db()

    offers = [
        {
            "city_from": "spb",
            "city_to": "antalya",
            "country_to": "turkey",
            "date_from": "2025-06-10",
            "date_to": "2025-06-17",
            "nights": 7,
            "price": 28500,  # горячий (ниже 30000)
            "source": "demo_seed",
        },
        {
            "city_from": "spb",
            "city_to": "alanya",
            "country_to": "turkey",
            "date_from": "2025-06-20",
            "date_to": "2025-06-30",
            "nights": 10,
            "price": 31500,  # не пройдёт фильтр по цене
            "source": "demo_seed",
        },
        {
            "city_from": "spb",
            "city_to": "istanbul",
            "country_to": "turkey",
            "date_from": "2025-07-01",
            "date_to": "2025-07-05",
            "nights": 4,
            "price": 26000,  # горячий
            "source": "demo_seed",
        },
    ]

    for offer in offers:
        insert_raw_offer(
            city_from=offer["city_from"],
            city_to=offer["city_to"],
            country_to=offer["country_to"],
            date_from=offer["date_from"],
            date_to=offer["date_to"],
            nights=offer["nights"],
            price=offer["price"],
            source=offer["source"],
        )

    print("Inserted demo offers into offers_raw")


def fill_hot_from_raw():
    """
    Берёт последние raw-офферы spb/turkey,
    фильтрует по правилам «горящих» и кладёт в offers_hot.
    """
    init_db()

    raw_offers = get_raw_offers(city_from="spb", country_to="turkey", limit=100)

    inserted = 0
    for row in raw_offers:
        if is_hot(row):
            insert_hot_offer_from_raw(row)
            inserted += 1

    print(f"Inserted {inserted} hot offers into offers_hot")


def main():
    seed_raw_offers()
    fill_hot_from_raw()
    print("Seeding completed. You can now call /api/deals?city_from=spb&country_to=turkey")


if __name__ == "__main__":
    main()
