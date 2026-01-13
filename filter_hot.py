# filter_hot.py
"""
Фильтрует offers_raw по правилам "горящих" туров
и сохраняет подходящие записи в offers_hot.
Условия:
  - price < 30000
  - 3 <= nights <= 14
"""

from database import init_db, get_raw_offers, insert_hot_offer_from_raw


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


def main():
    init_db()

    # Берем все последние raw-офферы для spb/turkey
    raw_offers = get_raw_offers(city_from="spb", country_to="turkey", limit=100)

    inserted = 0
    for row in raw_offers:
        if is_hot(row):
            insert_hot_offer_from_raw(row)
            inserted += 1

    print(f"Inserted {inserted} hot offers into offers_hot")


if __name__ == "__main__":
    main()
