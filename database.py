# database.py

import sqlite3
from typing import List, Tuple, Optional, Dict, Any

DB_PATH = "tripgenius.db"


def get_connection() -> sqlite3.Connection:
    """
    Возвращает новое подключение к SQLite с включёнными внешними ключами.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # удобнее возвращать dict-подобные строки
    conn.execute("PRAGMA foreign_keys = ON;")  # включаем FOREIGN KEY [web:41][web:42]
    return conn


def init_db() -> None:
    """
    Создаёт файл БД и таблицы, если их ещё нет.
    Таблицы:
      - offers_raw
      - offers_hot (FOREIGN KEY raw_id → offers_raw.id)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Сырые офферы
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS offers_raw (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_from TEXT NOT NULL,
            city_to TEXT,
            country_to TEXT NOT NULL,
            date_from TEXT,
            date_to TEXT,
            nights INTEGER,
            price INTEGER NOT NULL,
            source TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )

    # Горящие офферы
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS offers_hot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_id INTEGER NOT NULL,
            city_from TEXT NOT NULL,
            city_to TEXT,
            country_to TEXT NOT NULL,
            date_from TEXT,
            date_to TEXT,
            nights INTEGER,
            price INTEGER NOT NULL,
            source TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (raw_id) REFERENCES offers_raw(id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    conn.close()


def insert_raw_offer(
    city_from: str,
    country_to: str,
    price: int,
    city_to: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    nights: Optional[int] = None,
    source: Optional[str] = None,
) -> int:
    """
    Вставляет одну запись в offers_raw и возвращает id вставленной строки.

    Даты ожидаются в строковом формате (например, ISO 8601: '2025-01-10'). [web:50]
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO offers_raw (
            city_from, city_to, country_to,
            date_from, date_to, nights,
            price, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (city_from, city_to, country_to, date_from, date_to, nights, price, source),
    )

    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_raw_offers(
    city_from: str,
    country_to: str,
    limit: int = 100,
) -> List[sqlite3.Row]:
    """
    Возвращает список сырых офферов по city_from + country_to.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM offers_raw
        WHERE city_from = ?
          AND country_to = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?;
        """,
        (city_from, country_to, limit),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def insert_hot_offer_from_raw(raw_row: sqlite3.Row) -> int:
    """
    Принимает строку из offers_raw (sqlite3.Row) и вставляет соответствующую запись в offers_hot.
    Возвращает id записи в offers_hot.
    """
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));
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
        ),
    )

    conn.commit()
    hot_id = cur.lastrowid
    conn.close()
    return hot_id


def get_hot_offers(
    city_from: str,
    country_to: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Возвращает список горячих офферов как список dict,
    готовых к JSON-сериализации в FastAPI.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            raw_id,
            city_from,
            city_to,
            country_to,
            date_from,
            date_to,
            nights,
            price,
            source,
            created_at
        FROM offers_hot
        WHERE city_from = ?
          AND country_to = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?;
        """,
        (city_from, country_to, limit),
    )

    rows = cur.fetchall()
    conn.close()

    # Перегоняем sqlite3.Row → обычные словари
    deals: List[Dict[str, Any]] = []
    for row in rows:
        deals.append(
            {
                "id": row["id"],
                "raw_id": row["raw_id"],
                "city_from": row["city_from"],
                "city_to": row["city_to"],
                "country_to": row["country_to"],
                "date_from": row["date_from"],
                "date_to": row["date_to"],
                "nights": row["nights"],
                "price": row["price"],
                "source": row["source"],
                "created_at": row["created_at"],
            }
        )

    return deals
