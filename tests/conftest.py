from unittest.mock import MagicMock

import pytest
from sqlalchemy import select
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.db import get_db
from src.database.models import Base, User


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
                       SQLALCHEMY_DATABASE_URL, 
                       connect_args={"check_same_thread": False}
                      )
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {
            'id': 2,
            'username': 'Example_Name',
            'email': 'pwht_12p@meta.ua',
            'password': 'Qwerty@1',
            'roles': 'user',
            'status_active': 'true',
            }


@pytest.fixture(scope="module")
def comment():
    return {"comment": "Test comment", "image_id": "1"}


@pytest.fixture
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)

    current_user: User = session.query(User).filter_by(email=user.get('email')).first()
    current_user.confirmed = True
    session.commit()


    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    # return data["access_token"]
    return {"access_token": data["access_token"], "refresh_token": data['refresh_token'], "token_type": "bearer"}


@pytest.fixture(scope="module")
def user_admin():
    return {
            'id': 1,
            'username': 'Example_Name',
            'email': 'test_email@ukr.com',
            'password': 'Qwerty@1',
            'roles': 'admin',
            'status_active': 'true',
            }


@pytest.fixture(scope="module")
def user_moderator():
    return {
            'id': 3,
            'username': 'Example_Name',
            'email': 'test_email@ukr.com',
            'password': 'Qwerty@1',
            'roles': 'moderator',
            'status_active': 'true',
            }


@pytest.fixture(scope='function')
def access_token(client, user, session, mocker) -> str:
    mocker.patch('src.routes.auth.send_email')  # mocker

    client.post('/api/auth/signup', json=user)

    current_user: User = session.scalar(select(User).filter(User.email == user['email']))
    current_user.confirmed = True
    session.commit()

    response = client.post(
                           '/api/auth/login',
                           data={'username': user.get('email'), 'password': user.get('password')},
                           )
    return response.json()['access_token']