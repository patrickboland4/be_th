from app import app
from app import database_helpers as dbh
from config import TABLE_NAME as table_name
from config import DB_FILE as db_file


def main():
    dbh.create_table(db_file, table_name)
    dbh.perform_initial_load(app)
    app.run()


if __name__ == "__main__":
    main()