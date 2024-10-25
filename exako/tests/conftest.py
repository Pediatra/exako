import pytest
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from exako.auth import current_admin_user, current_user
from exako.database import get_session
from exako.main import app
from exako.settings import settings


@pytest.fixture
def client(session):
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = lambda: session
        app.dependency_overrides[current_admin_user] = lambda: {}
        app.dependency_overrides[current_user] = lambda: {}
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def engine():
    engine = create_engine(settings.DATABASE_TEST)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    session = Session(engine)

    def set_session(cls):
        for factory in cls.__subclasses__():
            factory._meta.sqlalchemy_session = session
            set_session(factory)

    set_session(SQLAlchemyModelFactory)
    session.begin()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def generate_payload():
    def _generate(factory, exclude=None, include=None, **kwargs):
        result = factory.build(**kwargs)
        return result.model_dump(exclude=exclude, include=include)

    return _generate
