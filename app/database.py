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


def start(db_file="./database.db"):
    create_table_sql = """ CREATE TABLE IF NOT EXISTS rates (
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

    print(f"database started successfully")
    return connection


if __name__ == "__main__":
    main()