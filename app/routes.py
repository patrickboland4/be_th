from flask import request
from app import app


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
            return "Request was not JSON", 400
        rates = request.get_json().get('rates')
        for rate in rates:
            days = rate.get('days')
            price = rate.get('price')
            times = rate.get('times')
            tz = rate.get('tz')
            print(f"rate: {rate}")
        return "200"
    else:
        return f"'GET' received. rates: \n{request.get_json()}"


'''
'''
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
