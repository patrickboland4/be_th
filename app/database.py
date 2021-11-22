import sqlite3


def create_connection(db_file):
    '''
    Create database connection to SQLite database specified by db_file

    Args:
        db_file (string): [description]

    Returns:
        Connection object or None: Connection object or None
    '''
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


def main():
    db_file = "./database.db"

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


if __name__ == "__main__":
    main()