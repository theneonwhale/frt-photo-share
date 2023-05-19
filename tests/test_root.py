
from fastapi.testclient import TestClient
# import pytest

import main


client = TestClient(main.app)


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to Photo-Share by Fast Rabbit Team.'}


def test_healthchecker():
    response = client.get('/api/healthchecker')
    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to FastAPI!'}
