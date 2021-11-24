import datetime
import pdb
import sqlite3
import json

from flask import Flask, request, jsonify

import database


TABLE_NAME = "rates"


def create_app(db_file, table_name):
    app = Flask(__name__)

    @app.route('/rates', methods=['GET', 'PUT'])
    def rates():
        '''
        rates route.

        put:
            summary: rates endpoint
            description: persist rate information.
            payload:
                {
                    "rates": [
                        {
                            "days": "mon,tues,thurs", 
                            "times": "0900-2100", 
                            "tz": "America/Chicago", 
                            "price": 1500
                        },
                        {
                            "days": "fri,sat,sun", 
                            "times": "0900-2100", 
                            "tz": "America/Chicago", 
                            "price": 2000
                        }
                    ]
                }
            responses:
                INVALID INPUT: request must be json:
                    description: the request must be valid json
                INVALID INPUT: end time must be greater than start time:
                    description: times must be a valid string where end time is greater than start time
                OK:
                    description: PUT succeeded.
        get:
            summary: rates endpoint
            description: get existing rates.
            responses:
                {
                    "rates": [
                        {
                            "days": "mon,tues,thurs", 
                            "times": "0900-2100", 
                            "tz": "America/Chicago", 
                            "price": 1500
                        },
                        {
                            "days": "fri,sat,sun", 
                            "times": "0900-2100", 
                            "tz": "America/Chicago", 
                            "price": 2000
                        }
                    ]
                }
                    description: existing rates were returned.
                NOT FOUND:
                    description: no rates are stored.
        '''
        if request.method == "PUT":
            if not request.is_json:
                return jsonify("INVALID INPUT: request must be json")
            delete_records()
            rates = request.get_json().get('rates')
            for rate in rates:
                days = rate.get('days')
                times = rate.get('times')
                tz = rate.get('tz')
                price = rate.get('price')
                start, end = [int(i) for i in times.split('-')]
                if end <= start:
                    return jsonify("INVALID INPUT: end time must be greater than start time")
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
            return jsonify("OK")
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
                        response = jsonify(dict(rates=result))
                    else:
                        response = jsonify("NOT FOUND")
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
        day_pattern = f"%{start_day}%"

        try:
            with sqlite3.connect(db_file) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"SELECT price FROM {TABLE_NAME} WHERE days LIKE ? AND start <= ? AND end >= ?",(day_pattern,start_time,end_time,)
                )
                rows = cursor.fetchall()
                if len(rows) > 1:
                    response = jsonify("unavailable")
                elif len(rows) == 1:
                    response = jsonify(dict(price=rows.pop()[0]))
                else:
                    response = jsonify("NOT FOUND")
        except:
            raise
        finally:
            connection.close()
        return response

    return app
    

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
    app = create_app(db_file, TABLE_NAME)
    with open("./rates.json") as f:
        payload = json.load(f)
    with app.test_client() as client:
        client.put("/rates", json=payload)
    app.run()