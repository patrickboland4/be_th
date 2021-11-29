## System Requirements
- python3
- docker
- Windows compatibility is unknown

## Running the app with docker
- Ensure docker is running
- Run `./start.sh`. Note you may need to make this shell script executable with `chmod +x start.sh`
- See "Interacting with the application", below

## Running the app without docker
- Create a python3 virtual environment (see note on creating a virtual environment below)
- Run `pip install -r requirements.txt`
- Within the virtual environment at the project root, run `python run.py`
- `* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)` indicates the application has started successfully
- Note that upon application start, the payload located in `rates.json` will be loaded to the database (also provisioned on application start). To modify the data loaded at startup, modify `rates.json`. 
- See "Interacting with the application", below

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
Now that the server is running, we can interact with the application endpoints. One way to achieve this is by using `curl`. 

`PUT`
```
$ curl --header "Content-Type: application/json" --request PUT --data '{"rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1500}]}' http://127.0.0.1:5000/rates
```

`GET`
```
$ curl --GET "http://127.0.0.1:5000/price?start=2021-11-22T10:00:00-05:00&end=2021-11-22T12:00:00-05:00"

{"price":1500}
```
We may also interact with the application within our browser. 

To view rates, open `localhost:5000/rates`

To get a price, go to the `/price` endpoint and enter a start and end time, e.g. `localhost:5000/price?start=2021-11-22T10:00:00-05:00&end=2021-11-22T12:00:00-05:00`

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
- Instrumentation (metrics) 
    - Instrumentation is key towards observing the health of a given application. Instrumentation can take place at the host level (e.g. CPU, Memory), and application level (e.g. median response time).
    - For this app, we would start by instrumenting the `price` and `rates` endpoints, and expose instrumentation data at a given endpoint. 
    - We want each metric to possess meaning, and to explain something specific about the application. There are a number of metrics that could be relevant for this app, e.g. average response time, average response size, requests per second. Importantly, we should not forget metrics that indicate `tail latency`, or the worst latency. Tail latency may be expressed in `p` values, e.g. `p99 response time` is the worst 1% of response times. 
    - Using a tool like Grafana, would help us visualize our instrumentation data. 
    - Prometheus seems to be a popular option for instrumenting flask apps. 
- Include a swagger spec
- Load testing, Performance testing
    - One option for performance testing is using a statically-typed client such as Go or Java. The reason for this is because the client can become a bottleneck when we are simulating hundreds or thousands of requests per second, which could yield skewed performance data. Using a statically typed language is one way to accommodate load testing with hundreds or thousands of concurrent requests.
    - One important piece to consider are the effects of concurrent users. We should consider database patterns (Consistency vs Availability) as well as application patterns that will allow concurrent requests to be handled gracefully.
- Databse
    - Our data shouldn't be stored in a file. Instead, it should be stored in a database such as postgresql. 
- Improve the code base
    - Better error handling
    - More helpful feedback for the client to describe certain types of application errors.
    - Handling multiple timezones
    - Use a linter
___

## Improving the exercise
The paramters are start and end. --> Parameters
