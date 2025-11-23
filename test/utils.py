from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from main import app

from database import Base
from models import Todos, Users
import pytest
from routers.auth import crypt_context

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./testdb.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "jon", "id": 1, "user_role": "admin"}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with test_engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username="jon",
        email="jon@mail.com",
        first_name="Jon",
        last_name="Ahn",
        hashed_password=crypt_context.hash('1234'),
        role='admin',
        phone_number="555-444-3333"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with test_engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()