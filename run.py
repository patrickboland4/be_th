from app import app
from app import database_helpers as dbh
from config import TABLE_NAME as table_name
from config import DB_FILE as db_file


def main(host="127.0.0.1", port=5000, debug=False):
    dbh.create_table(db_file, table_name)
    dbh.perform_initial_load(app)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
