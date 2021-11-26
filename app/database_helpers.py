import json
import sqlite3
from config import TABLE_NAME as table_name
from config import DB_FILE as db_file


def create_connection(db_file):
    connection = None

    try:
        connection = sqlite3.connect(db_file)
        return connection
    except:
        raise

    return connection


def create_table(db_file, table_name):
    create_table_sql = f""" CREATE TABLE IF NOT EXISTS {table_name} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    days TEXT NOT NULL,
                                    times TEXT NOT NULL,
                                    tz TEXT NOT NULL,
                                    price INTEGER NOT NULL,
                                    start INTEGER NOT NULL,
                                    end INTEGER NOT NULL
                                ); """

    connection = create_connection(db_file)
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(create_table_sql)
        except:
            raise
    else:
        raise Exception("could not create table")


def delete_records():
    try:
        with sqlite3.connect(db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"DELETE FROM {table_name}"
            )
            connection.commit()
    except:
        raise
    finally:
        connection.close()


def perform_initial_load(app):
    with open("./rates.json") as f:
        payload = json.load(f)
    with app.test_client() as client:
        client.put("/rates", json=payload)