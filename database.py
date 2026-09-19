import os
import sqlite3
from datetime import datetime

# Если DATABASE_URL есть — используем PostgreSQL.
# Если его нет — используем локальный SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE = "logistics.db"


def get_connection():
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        connection = psycopg2.connect(DATABASE_URL)
        return connection, RealDictCursor

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection, None


def init_db():
    connection, cursor_factory = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=cursor_factory)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id BIGSERIAL PRIMARY KEY,
                created_at TEXT NOT NULL,

                route TEXT,

                distance REAL,
                return_percent REAL,
                rate REAL,
                target_margin REAL,
                monthly_distance REAL,

                consumption REAL,
                fuel_price REAL,
                driver_per_km REAL,
                repair_per_km REAL,
                tires_per_km REAL,
                depreciation_per_km REAL,

                osago REAL,
                kasko REAL,
                tax REAL,
                leasing REAL,
                parking REAL,
                washing REAL,
                dispatcher REAL,

                toll REAL,
                loading REAL,
                other REAL,

                return_distance REAL,
                total_distance REAL,
                liters REAL,
                fuel_cost REAL,
                driver_cost REAL,
                repair_cost REAL,
                tires_cost REAL,
                depreciation_cost REAL,
                fixed_cost REAL,
                total_cost REAL,

                revenue REAL,
                profit REAL,
                cost_per_km REAL,
                margin REAL,

                minimum_rate REAL,
                target_rate REAL,
                target_revenue REAL,
                target_profit REAL,
                rate_reserve REAL
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

    else:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,

                route TEXT,

                distance REAL,
                return_percent REAL,
                rate REAL,
                target_margin REAL,
                monthly_distance REAL,

                consumption REAL,
                fuel_price REAL,
                driver_per_km REAL,
                repair_per_km REAL,
                tires_per_km REAL,
                depreciation_per_km REAL,

                osago REAL,
                kasko REAL,
                tax REAL,
                leasing REAL,
                parking REAL,
                washing REAL,
                dispatcher REAL,

                toll REAL,
                loading REAL,
                other REAL,

                return_distance REAL,
                total_distance REAL,
                liters REAL,
                fuel_cost REAL,
                driver_cost REAL,
                repair_cost REAL,
                tires_cost REAL,
                depreciation_cost REAL,
                fixed_cost REAL,
                total_cost REAL,

                revenue REAL,
                profit REAL,
                cost_per_km REAL,
                margin REAL,

                minimum_rate REAL,
                target_rate REAL,
                target_revenue REAL,
                target_profit REAL,
                rate_reserve REAL
            )
        """)

        connection.commit()
        connection.close()


def save_trip(data):
    connection, cursor_factory = get_connection()

    values = (
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        data.get("route", ""),

        data.get("distance", 0),
        data.get("return_percent", 0),
        data.get("rate", 0),
        data.get("target_margin", 0),
        data.get("monthly_distance", 0),

        data.get("consumption", 0),
        data.get("fuel_price", 0),
        data.get("driver_per_km", 0),
        data.get("repair_per_km", 0),
        data.get("tires_per_km", 0),
        data.get("depreciation_per_km", 0),

        data.get("osago", 0),
        data.get("kasko", 0),
        data.get("tax", 0),
        data.get("leasing", 0),
        data.get("parking", 0),
        data.get("washing", 0),
        data.get("dispatcher", 0),

        data.get("toll", 0),
        data.get("loading", 0),
        data.get("other", 0),

        data.get("return_distance", 0),
        data.get("total_distance", 0),
        data.get("liters", 0),
        data.get("fuel_cost", 0),
        data.get("driver_cost", 0),
        data.get("repair_cost", 0),
        data.get("tires_cost", 0),
        data.get("depreciation_cost", 0),
        data.get("fixed_cost", 0),
        data.get("total_cost", 0),

        data.get("revenue", 0),
        data.get("profit", 0),
        data.get("cost_per_km", 0),
        data.get("margin", 0),

        data.get("minimum_rate", 0),
        data.get("target_rate", 0),
        data.get("target_revenue", 0),
        data.get("target_profit", 0),
        data.get("rate_reserve", 0)
    )

    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=cursor_factory)

        cursor.execute("""
            INSERT INTO trips (
                created_at,
                route,

                distance,
                return_percent,
                rate,
                target_margin,
                monthly_distance,

                consumption,
                fuel_price,
                driver_per_km,
                repair_per_km,
                tires_per_km,
                depreciation_per_km,

                osago,
                kasko,
                tax,
                leasing,
                parking,
                washing,
                dispatcher,

                toll,
                loading,
                other,

                return_distance,
                total_distance,
                liters,
                fuel_cost,
                driver_cost,
                repair_cost,
                tires_cost,
                depreciation_cost,
                fixed_cost,
                total_cost,

                revenue,
                profit,
                cost_per_km,
                margin,

                minimum_rate,
                target_rate,
                target_revenue,
                target_profit,
                rate_reserve
            )
            VALUES (
                %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            RETURNING id
        """, values)

        trip_id = cursor.fetchone()["id"]

        connection.commit()
        cursor.close()
        connection.close()

        return trip_id

    else:
        cursor = connection.execute("""
            INSERT INTO trips (
                created_at,
                route,

                distance,
                return_percent,
                rate,
                target_margin,
                monthly_distance,

                consumption,
                fuel_price,
                driver_per_km,
                repair_per_km,
                tires_per_km,
                depreciation_per_km,

                osago,
                kasko,
                tax,
                leasing,
                parking,
                washing,
                dispatcher,

                toll,
                loading,
                other,

                return_distance,
                total_distance,
                liters,
                fuel_cost,
                driver_cost,
                repair_cost,
                tires_cost,
                depreciation_cost,
                fixed_cost,
                total_cost,

                revenue,
                profit,
                cost_per_km,
                margin,

                minimum_rate,
                target_rate,
                target_revenue,
                target_profit,
                rate_reserve
            )
            VALUES (
                ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
        """, values)

        connection.commit()
        trip_id = cursor.lastrowid
        connection.close()

        return trip_id


def get_trips():
    connection, cursor_factory = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=cursor_factory)

        cursor.execute("""
            SELECT *
            FROM trips
            ORDER BY id DESC
        """)

        trips = cursor.fetchall()

        cursor.close()
        connection.close()

        return trips

    trips = connection.execute("""
        SELECT *
        FROM trips
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return trips


def get_trip(trip_id):
    connection, cursor_factory = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor(cursor_factory=cursor_factory)

        cursor.execute("""
            SELECT *
            FROM trips
            WHERE id = %s
        """, (trip_id,))

        trip = cursor.fetchone()

        cursor.close()
        connection.close()

        return trip

    trip = connection.execute("""
        SELECT *
        FROM trips
        WHERE id = ?
    """, (trip_id,)).fetchone()

    connection.close()

    return trip


def delete_trip(trip_id):
    connection, cursor_factory = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM trips
            WHERE id = %s
        """, (trip_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return

    connection.execute("""
        DELETE FROM trips
        WHERE id = ?
    """, (trip_id,))

    connection.commit()
    connection.close()
