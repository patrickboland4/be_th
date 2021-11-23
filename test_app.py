import os
import pdb
import tempfile

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


def test_empty_db_response_message(client):
    '''
    Test blank database

    Args:
        client ([type]): [description]
    '''
    response = client.get('/rates')
    assert response.is_json
    assert b'No data found' in response.data


def test_non_empty_db_response_message(client):
    client.put("/rates", json={
        "rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1500},{"days":"fri,sat,sun","times":"0900-2100","tz":"America/Chicago","price":2100}]
    })
    response = client.get('/rates')
    expected_response = [[1, 'mon,tues,thurs', '0900-2100', 'America/Chicago', 1500], [2, 'fri,sat,sun', '0900-2100', 'America/Chicago', 2100]]
    assert response.is_json
    assert expected_response == response.json[0].get('rates')

def test_writing_to_db_will_overwrite_existing_data(client):
    client.put("/rates", json={
        "rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1500},{"days":"fri,sat,sun","times":"0900-2100","tz":"America/Chicago","price":2100}]
    })
    client.put("/rates", json={
        "rates":[{"days":"mon,tues,thurs","times":"0900-2100","tz":"America/Chicago","price":1600},{"days":"fri,sat,sun","times":"0900-2100","tz":"America/Chicago","price":2100}]
    })
    response = client.get('/rates')
    expected_response = [[3, 'mon,tues,thurs', '0900-2100', 'America/Chicago', 1600], [4, 'fri,sat,sun', '0900-2100', 'America/Chicago', 2100]]
    assert response.is_json
    assert expected_response == response.json[0].get('rates')

