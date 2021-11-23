import os
import pdb
import tempfile

import flask
import pytest

from app import create_app
from app import TABLE_NAME as table_name
import database


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    db_path += ".db"
    app = create_app(db_path, table_name)

    with app.test_client() as client:
        with app.app_context():
            database.setup(db_path, table_name)
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_non_json_input_in_rates_put_returns_exp_response(client):
    response = client.put("/rates")
    assert response.is_json
    assert response.json['code'] == 400


def test_empty_db_response_message_on_get(client):
    response = client.get('/rates')
    assert response.is_json
    assert response.json['code'] == 404


def test_non_empty_db_response_message_on_get(client):
    client.put("/rates", json={
        "rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1500},{"days":"fri,sat,sun","times":"0900-2100","tz":"America/Chicago","price":2100}]
    })
    response = client.get('/rates')
    expected_response = [['mon,tues,thurs', '0900-2100', 'America/Chicago', 1500], ['fri,sat,sun', '0900-2100', 'America/Chicago', 2100]]
    assert response.is_json
    assert expected_response == response.json['result']


def test_writing_to_db_will_overwrite_existing_data(client):
    client.put("/rates", json={
        "rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1500},{"days":"fri,sat,sun","times":"0900-2100","tz":"America/Chicago","price":2100}]
    })
    client.put("/rates", json={
        "rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1600},{"days":"fri,sat,sun","times":"0900-2100","tz":"America/Chicago","price":2100}]
    })
    response = client.get('/rates')
    expected_response = [['mon,tues,thurs', '0900-2100', 'America/Chicago', 1600], ['fri,sat,sun', '0900-2100', 'America/Chicago', 2100]]
    assert response.is_json
    assert expected_response == response.json['result']


def test_get_price_with_query_across_multiple_days_returns_expected_response(client):
    response = client.get(
        '/price?start=2021-11-22T07:00:00-05:00&end=2021-11-23T12:00:00-05:00'
    )
    assert "unavailable" == response.json


def test_get_price_with_matching_data_returns_expected_response(client):
    client.put("/rates", json={
        "rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1500},{"days":"fri,sat,sun","times":"0900-2100","tz":"America/Chicago","price":2100}]
    })
    response = client.get(
        '/price?start=2021-11-22T10:00:00-05:00&end=2021-11-22T12:00:00-05:00'
    )
    expected_response = dict(price=1500)
    assert expected_response == response.json


def test_get_price_without_matching_data_returns_expected_response(client):
    # response = client.get('/price?start=2015-07-01T07:00:00-05:00&end=2015-07-01T12:00:00-05:00')
    response = client.get(
        '/price?start=2021-11-22T07:00:00-05:00&end=2021-11-22T12:00:00-05:00'
    )
    assert 404 == response.json['code']

