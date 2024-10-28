import pytest
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, inspect

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


def _include_foreign_keys(model, instance):
    inspector = inspect(model)
    result = dict()
    foreign_keys = [
        column.key for column in inspector.columns.values() if column.foreign_keys
    ]
    for fk in foreign_keys:
        fk_attr = fk.replace('_id', '')
        fk_instance = getattr(instance, fk_attr, None)
        if fk_instance is None:
            continue
        result[fk] = fk_instance.id
    return result


@pytest.fixture
def generate_payload():
    def _generate(factory, exclude=None, include=None, **kwargs):
        instance = factory.build(**kwargs)
        result_dict = instance.model_dump(exclude=exclude, include=include)
        result_dict.update(_include_foreign_keys(factory._meta.model, instance))
        return result_dict

    return _generate
