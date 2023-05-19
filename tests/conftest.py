
from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.db import get_db
from src.database.models import Base


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


@pytest.fixture(scope="module")
def user():
    return {
            'username': 'Example_Name',
            'email': 'test_email@ukr.com',
            'password': 'Qwerty@1',
            'created_at': f'{date.today()}',
            'updated_at': f'{date.today()}',
            'avatar': '',
            'refresh_token': 'token1',
            'roles': 'admin',
            'confirmed': 'false',
            'status_active': 'true',
            }
