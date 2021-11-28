## System Requirements
- python3
- Windows compatibility is unknown

## Getting up and running
- Create a python3 virtual environment (see note on creating a virtual environment below)
- Run `pip install -r requirements.txt`
- Within the virtual environment at the project root, run `python run.py`
- `* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)` indicates the application has started successfully
- Note that upon application start, the payload located in `rates.json` will be loaded to the database (also provisioned on application start). To modify the data loaded at startup, modify `rates.json`. 

## Testing the app
Ensure `pytest` is installed
```
$ which pytest
```
Run `pytest` at the project root.
```
$ pytest
```

## Interacting with the application
Now that the server is running, we can interact with the application endpoints. One way to achieve this is using `curl`. 

`PUT`
```
$ curl --header "Content-Type: application/json" --request PUT --data '{"rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1500}]}' http://127.0.0.1:5000/rates
```

`GET`
```
$ curl --GET "http://127.0.0.1:5000/price?start=2021-11-22T10:00:00-05:00&end=2021-11-22T12:00:00-05:00"

{"price":1500}
```

More documentation regarding the behavior of these endpoints can be found below in "Endpoint Documentation". 

___
## Creating a virtual environment
There are a variety of ways to create a virtual environment in python. 
One way is to use `pew`. At your terminal, run
``` 
pip install pew
```
Confirm pew is discoverable by running
``` 
which pew
```
Create the virtual environment 
``` 
pew new -p python3 <env_name>
```
Active the virtual environment 
``` 
pew workon <env_name>
```
___

## Endpoint documentation
The `/rates` endpoint is capable of responding to `PUT` and `GET` requests. 

`PUT`

PUT requests update rate information. 
The payload for PUT requests must be JSON. 
The submitted JSON overwrites the stored rates.
A rate is comprised of a price, time range the rate is valid, 
timezone, and days of the week the rate applies to.
The following represents a valid JSON payload. 
Note that one or more rates may be specified. 
```
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
```

`OK` is returned upon successful loading of the JSON payload. 
Exceptions may be raised due to problems during data persistence. 
`INVALID INPUT: ...` is returned to indicate bad payload. 


`GET`

GET requests return the rates stored. 

Sample response:
```
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
```
If no rates are stored, the application responds with `NOT FOUND`.


The `/price` endpoint is capable of responding to `GET` requests.

This endpoint allows the user to request the price for a specified time interval.
It uses query parameters for requesting the price.
The user specifies input date/times as ISO-8601 with timezones.
The parameters are start and end.
An example query is `?start=2015-07-01T07:00:00-05:00&end=2015-07-01T12:00:00-05:00`.
The response contains the price for that interval, e.g.
```
{
    "price": 5000
}
```

This response will return `unavailable` under these conditions:

- User input spans more than one day.
- The specified time period contains more than one rate.

If a rate does not exist for the specified time interval,
the application will respond with `NOT FOUND`.
___

## Development Notes

_Improvements from here_
- include a dockerfile
- metrics for endpoints captured and available to be queried via an endpoint (e.g. avg response time)
- include a swagger spec
- store in persistent data layer like postgres
- use a linter

_Considerations_
- One important piece to consider are the effects of concurrent users.
- how a user may misuse the API (especially around missing or invalid input)
- better input and error handling
- emitting more helpful responses to client
- input handling
- consider how I may handle multiple timezones
- I endeavored to make the code readable, keeping lines below 80 characters. However, certain statements are beyond 80 characters to maintain readability.
- While the application structure can be improved, breaking out the `app` and `tests` is a good start towards allowing this application to scale.
___

## Improving the exercise
The paramters are start and end. --> Parameters
