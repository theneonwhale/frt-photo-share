
from unittest.mock import MagicMock

from datetime import date
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
    # Dependency override
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


# @pytest.fixture(scope="module")
# def get_email_from_token(token):
#     return 'test_email@ukr.com'


@pytest.fixture(scope="module")
def user():
    return {
            'id': 2,
            'username': 'Example_Name',
            'email': 'test_email@ukr.com',
            'password': 'Qwerty@1',
            # 'created_at': f'{date.today()}',
            # 'updated_at': f'{date.today()}',
            # 'avatar': '',
            # 'refresh_token': 'token1',
            'roles': 'user',
            # 'confirmed': 'false',
            'status_active': 'true',
            }


@pytest.fixture(scope="module")
def user_admin():
    return {
            'id': 1,
            'username': 'Example_Name',
            'email': 'test_email@ukr.com',
            'password': 'Qwerty@1',
            # 'created_at': f'{date.today()}',
            # 'updated_at': f'{date.today()}',
            # 'avatar': '',
            # 'refresh_token': 'token1',
            'roles': 'admin',
            # 'confirmed': 'false',
            'status_active': 'true',
            }


@pytest.fixture(scope="module")
def user_moderator():
    return {
            'id': 3,
            'username': 'Example_Name',
            'email': 'test_email@ukr.com',
            'password': 'Qwerty@1',
            # 'created_at': f'{date.today()}',
            # 'updated_at': f'{date.today()}',
            # 'avatar': '',
            # 'refresh_token': 'token1',
            'roles': 'moderator',
            # 'confirmed': 'false',
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
