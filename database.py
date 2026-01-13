import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent / "tripgenius.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS offers_raw (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_from TEXT NOT NULL,
            city_to TEXT NOT NULL,
            country_to TEXT NOT NULL,
            date_from TEXT NOT NULL,
            date_to TEXT NOT NULL,
            nights INTEGER NOT NULL,
            price INTEGER NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS offers_hot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_id INTEGER NOT NULL,
            city_from TEXT NOT NULL,
            city_to TEXT NOT NULL,
            country_to TEXT NOT NULL,
            date_from TEXT NOT NULL,
            date_to TEXT NOT NULL,
            nights INTEGER NOT NULL,
            price INTEGER NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (raw_id) REFERENCES offers_raw(id)
        );
        """
    )

    conn.commit()
    conn.close()


def insert_raw_offer(
    *,
    city_from: str,
    city_to: str,
    country_to: str,
    date_from: str,
    date_to: str,
    nights: int,
    price: int,
    source: str,
    created_at: str,
) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO offers_raw (
            city_from, city_to, country_to,
            date_from, date_to, nights,
            price, source, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            city_from,
            city_to,
            country_to,
            date_from,
            date_to,
            nights,
            price,
            source,
            created_at,
        ),
    )

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_raw_offers(
    *,
    city_from: Optional[str] = None,
    country_to: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM offers_raw WHERE 1=1"
    params: list[Any] = []

    if city_from:
        query += " AND city_from = ?"
        params.append(city_from)

    if country_to:
        query += " AND country_to = ?"
        params.append(country_to)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def insert_hot_offer_from_raw(raw_row: Dict[str, Any]) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO offers_hot (
            raw_id,
            city_from, city_to, country_to,
            date_from, date_to, nights,
            price, source, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            raw_row["id"],
            raw_row["city_from"],
            raw_row["city_to"],
            raw_row["country_to"],
            raw_row["date_from"],
            raw_row["date_to"],
            raw_row["nights"],
            raw_row["price"],
            raw_row["source"],
            raw_row["created_at"],
        ),
    )

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_hot_offers(
    *,
    city_from: Optional[str] = None,
    country_to: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM offers_hot WHERE 1=1"
    params: list[Any] = []

    if city_from:
        query += " AND city_from = ?"
        params.append(city_from)

    if country_to:
        query += " AND country_to = ?"
        params.append(country_to)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]
