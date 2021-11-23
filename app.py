import datetime
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
                return create_response("Request must be JSON", 400)
            delete_records()
            rates = request.get_json().get('rates')
            for rate in rates:
                days = rate.get('days')
                times = rate.get('times')
                tz = rate.get('tz')
                price = rate.get('price')
                start, end = [int(i) for i in times.split('-')]
                if end <= start:
                    return create_response("End time must be less than start time", 400)
                try:
                    with sqlite3.connect(db_file) as connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            f"INSERT INTO {TABLE_NAME} (days,times,tz,price,start,end) VALUES (?,?,?,?,?,?)",(days,times,tz,price,start,end) 
                        )
                        connection.commit()
                except:
                    connection.rollback()
                    raise
                finally:
                    connection.close()
            return create_response("OK", 200)
        else:
            try:
                with sqlite3.connect(db_file) as connection:
                    cursor = connection.cursor()
                    cursor.execute(f"SELECT days, times, tz, price FROM {TABLE_NAME}")
                    rows = cursor.fetchall()
                    if rows:
                        result = []
                        for row in rows:
                            result.append(row)
                        response = create_response("OK", 200, result=result)
                    else:
                        response = create_response("DATA NOT FOUND", 404)
            except:
                raise
            finally:
                connection.close()
            return response


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
        start, end = [request.args.get(i) for i in ('start', 'end')]
        start_day, end_day = get_day_of_week_from_timestamp(*[start, end])
        if start_day != end_day:
            return jsonify("unavailable")
        start_time, end_time = get_time_from_timestamp(*[start, end])
        start_day_pattern = f"%{start_day}%"

        try:
            with sqlite3.connect(db_file) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"SELECT price FROM {TABLE_NAME} WHERE days LIKE ? AND start < ? AND end > ?",(start_day_pattern,start_time,end_time,)
                )
                rows = cursor.fetchall()
                if len(rows) > 1:
                    connection.close()
                    return jsonify("unavailable")
                elif len(rows) == 1:
                    return jsonify(dict(price=rows.pop()[0]))
                else:
                    response = create_response("DATA NOT FOUND", 404)
        except:
            raise
        finally:
            connection.close()
        return response

        return create_response("NOT FOUND", 404)

    return app
    

def create_response(message, code, result=None):
    return jsonify(dict(message=message, code=code, result=result))


def get_day_of_week_from_timestamp(*args):
    day_converter = dict(mon='mon', tue='tues', wed='wed', thu='thurs', fri='fri', sat='sat', sun='sun')
    response = []
    for arg in args:
        day_of_week = datetime.datetime.strptime(arg, "%Y-%m-%dT%H:%M:%S%z").strftime('%a').lower()
        response.append(day_converter.get(day_of_week))
    return response


def get_time_from_timestamp(*args):
    response = []
    for arg in args:
        time_as_int = int(datetime.datetime.strptime(arg, "%Y-%m-%dT%H:%M:%S%z").strftime('%H%M'))
        response.append(time_as_int)
    return response


if __name__ == "__main__":
    db_file="./database.db"
    database.setup(db_file, TABLE_NAME)
    create_app(db_file, TABLE_NAME).run()