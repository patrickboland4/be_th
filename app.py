import pdb
import sqlite3

from flask import Flask, request, jsonify

import database


TABLE_NAME = "rates"


def create_app(db_file, table_name):
    app = Flask(__name__)

    @app.route('/rates', methods=['GET', 'PUT'])
    def rates():
        '''
        takes a PUT where rate information can be updated by submitting a modified rates JSON
        overwrites the stored rates

        rate is comprised of a 
        price, time range the rate is valid, and days of the week the rate applies to

        This path when requested with a GET returns the rates stored.
        '''
        if request.method == "PUT":
            if not request.is_json:
                return jsonify("Request was not JSON", 400)
            delete_records()
            rates = request.get_json().get('rates')
            for rate in rates:
                days = rate.get('days')
                times = rate.get('times')
                tz = rate.get('tz')
                price = rate.get('price')
                try:
                    with sqlite3.connect(db_file) as connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            f"INSERT INTO {TABLE_NAME} (days,times,tz,price) VALUES (?,?,?,?)",(days,times,tz,price) 
                        )
                        connection.commit()
                except:
                    connection.rollback()
                    raise
                finally:
                    connection.close()
            return jsonify("Records updated, 200")
        else:
            try:
                with sqlite3.connect(db_file) as connection:
                    cursor = connection.cursor()
                    cursor.execute(f"SELECT * from {TABLE_NAME}")
                    rows = cursor.fetchall()
                    message = {'rates': []}
                    if rows:
                        for row in rows:
                            message.get('rates').append(row)
                    else:
                        message = "No data found, 404"
            except:
                raise
            finally:
                connection.close()
            return jsonify(message, 200)


    def delete_records():
        try:
            with sqlite3.connect(db_file) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"DELETE FROM {TABLE_NAME}"
                )
                connection.commit()
        except:
            raise
        finally:
            connection.close()


    @app.route('/price')
    def price():
        '''
        [summary]

        Returns:
            [type]: 
                    allows the user to request the price for a requested time

                    It uses query parameters for requesting the price
                    The user specifies input date/times as ISO-8601 with timezones
                    The paramters are start and end.
                    An example query is ?start=2015-07-01T07:00:00-05:00&end=2015-07-01T12:00:00-05:00 
                    Response contains price
        '''
        for k, v in request.args.items():
            print(k, v)
        start, end = [request.args.get(i) for i in ('start', 'end')]
        return f"start: {start}, end: {end}"

    return app


if __name__ == "__main__":
    db_file="./database.db"
    database.setup(db_file, TABLE_NAME)
    create_app(db_file, TABLE_NAME).run()