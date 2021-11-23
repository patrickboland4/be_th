import sqlite3


def create_connection(db_file):
    connection = None

    try:
        connection = sqlite3.connect(db_file)
        return connection
    except:
        raise

    return connection


def create_table(connection, create_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except:
        raise


def setup(db_file, table_name):
    create_table_sql = f""" CREATE TABLE IF NOT EXISTS {table_name} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    days TEXT NOT NULL,
                                    times TEXT NOT NULL,
                                    tz TEXT NOT NULL,
                                    price INTEGER NOT NULL
                                ); """

    connection = create_connection(db_file)
    if connection:
        create_table(connection, create_table_sql)
    else:
        raise Exception("could not create table")