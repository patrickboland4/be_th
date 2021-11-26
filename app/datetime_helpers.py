import datetime
import json


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