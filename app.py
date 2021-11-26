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
        The /rates endpoint is capable of responding to PUT and GET requests. 

        -- PUT -- 
        PUT requests update rate information. 
        The payload for PUT requests must be JSON. 
        The submitted JSON overwrites the stored rates.
        A rate is comprised of a price, time range the rate is valid, 
        and days of the week the rate applies to.
        The following represents a valid JSON payload. 
        Note that one or more rates may be specified. 
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

        Return values:
        "OK" is returned upon successful loading of the JSON payload. 
        Exceptions may be raised due to problems during data persistence. 
        "INVALID INPUT: ..." is returned to indicate bad payload. 

            responses:
                INVALID INPUT: {descriptive message}:
                    description: the application will respond with
                    "INVALID INPUT:" followed by a descriptive message,
                    indicating to the user why the input was invalid. 
                OK:
                    description: PUT succeeded.
        -- GET --
        GET requests return the rates stored. 
        Sample response:
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
        If no rates are stored, the application responds with "NOT FOUND".
        '''
        if request.method == "PUT":
            if not request.is_json:
                return jsonify("INVALID INPUT: request must be json")
            delete_records()
            rates = request.get_json().get('rates')
            if not rates:
                return jsonify("INVALID INPUT: rates must not be empty")
            for rate in rates:
                days = rate.get('days')
                times = rate.get('times')
                tz = rate.get('tz')
                price = rate.get('price')
                if not all([days, times, tz, price]):
                    return jsonify(
                        "INVALID INPUT: rates missing required field"
                    )
                start, end = [int(i) for i in times.split('-')]
                if end <= start:
                    return jsonify(
                        "INVALID INPUT: end time must be greater than start time"
                    )
                try:
                    with sqlite3.connect(db_file) as connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            f"""INSERT INTO {TABLE_NAME} 
                                (days,times,tz,price,start,end) 
                                VALUES (?,?,?,?,?,?)""",
                            (days,times,tz,price,start,end) 
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
                    cursor.execute(
                        f"SELECT days, times, tz, price FROM {TABLE_NAME}"
                    )
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


    @app.route('/price', methods=['GET'])
    def price():
        '''
        The /price endpoint is capable of responding to GET requests.
        This endpoint allows the user to request the price for a specified time.
        It uses query parameters for requesting the price
        The user specifies input date/times as ISO-8601 with timezones.
        The parameters are start and end.
        An example query is:
            ?start=2015-07-01T07:00:00-05:00&end=2015-07-01T12:00:00-05:00 
        The response contains price, e.g.
            {
                "price": 5000
            }

        This response will return "unavailable" under these conditions:
            - User input spans more than one day.
            - The specified time period contains more than one rate.

        If a rate does not exist for the specified time interval,
        the application will respond with "NOT FOUND".
        '''
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
                    f"""SELECT price FROM {TABLE_NAME} WHERE days LIKE 
                        ? AND start <= ? AND end >= ?""",
                    (day_pattern,start_time,end_time,)
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
    day_converter = dict(
        mon='mon', tue='tues', wed='wed', thu='thurs', fri='fri', 
        sat='sat', sun='sun'
    )
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


def perform_initial_load(app):
    with open("./rates.json") as f:
        payload = json.load(f)
    with app.test_client() as client:
        client.put("/rates", json=payload)


if __name__ == "__main__":
    db_file="./database.db"
    database.setup(db_file, TABLE_NAME)
    app = create_app(db_file, TABLE_NAME)
    perform_initial_load(app)
    app.run()