# collect_spb.py
"""
Простой скрипт для заполнения offers_raw тестовыми офферами
из СПб в Турцию. Без Travelpayouts, чисто для проверки пайплайна.
"""

from database import insert_raw_offer, init_db


def main():
    # На всякий случай убеждаемся, что таблицы есть
    init_db()

    # Пара фейковых туров, один дешевый (должен пройти фильтр),
    # второй дорогой (отфильтруется по price).
    offers = [
        {
            "city_from": "spb",
            "city_to": "antalya",
            "country_to": "turkey",
            "date_from": "2025-06-10",
            "date_to": "2025-06-17",
            "nights": 7,
            "price": 28000,  # < 30000 → должен попасть в offers_hot
            "source": "test_seed",
        },
        {
            "city_from": "spb",
            "city_to": "istanbul",
            "country_to": "turkey",
            "date_from": "2025-06-12",
            "date_to": "2025-06-20",
            "nights": 8,
            "price": 42000,  # >= 30000 → отсеется
            "source": "test_seed",
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

    print("Inserted test raw offers for spb → turkey")


if __name__ == "__main__":
    main()
