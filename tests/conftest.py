from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base, Role, User
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'

engine = create_engine(
                       SQLALCHEMY_DATABASE_URL, 
                       connect_args={'check_same_thread': False}
                      )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='module')
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope='module')
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    
@pytest.fixture(scope='module')
def admin():
    return {
            'id': 1,
            'username': 'admin', 
            'email': 'example@example.com', 
            'password': 'Qwerty@1',
            'roles': 'admin',
            'status_active': 'true',
            }


@pytest.fixture(scope='module')
def user():
    return {
            'id': 2,
            'username': 'user',
            'email': 'example2@example.com',
            'password': 'Qwerty@1',
            'roles': 'user',
            'status_active': 'true',
            }


@pytest.fixture(scope='module')
def comment():
    return {'comment': 'Test comment', 'image_id': '1'}

  
@pytest.fixture(scope='module')
def image():
    return {'description': 'Test image', 'tags': 'test tag'}

  
@pytest.fixture
def admin_token(client, admin, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    client.post('/api/auth/signup', json=admin)

    current_user: User = session.query(User).filter_by(email=admin.get('email')).first()
    current_user.id = 1
    current_user.confirmed = True
    current_user.roles = Role.admin
    session.commit()

    response = client.post(
        '/api/auth/login',
        data={'username': admin.get('email'), 'password': admin.get('password')},
    )
    data = response.json()
    # return data['access_token']
    return {'access_token': data['access_token'], 'refresh_token': data['refresh_token'], 'token_type': 'bearer'}


@pytest.fixture
def user_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    client.post('/api/auth/signup', json=user)

    current_user: User = session.query(User).filter_by(email=user.get('email')).first()
    current_user.id = 2
    current_user.confirmed = True
    current_user.roles = Role.user
    session.commit()

    response = client.post(
        '/api/auth/login',
        data={'username': user.get('email'), 'password': user.get('password')},
    )
    data = response.json()
    # return data['access_token']
    return {'access_token': data['access_token'], 'refresh_token': data['refresh_token'], 'token_type': 'bearer'}


@pytest.fixture(scope='function')
def access_token(client, admin, session, mocker) -> str:
    mocker.patch('src.routes.auth.send_email')  # mocker

    client.post('/api/auth/signup', json=admin)

    current_user: User = session.scalar(select(User).filter(User.email == admin['email']))
    current_user.confirmed = True
    session.commit()

    response = client.post(
                           '/api/auth/login',
                           data={'username': admin.get('email'), 'password': admin.get('password')},
                           )
    return response.json()['access_token']


@pytest.fixture(scope='function')
def access_token_user(client, user, session, mocker) -> str:
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