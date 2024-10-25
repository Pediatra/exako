from sqlmodel import Session, create_engine

from exako.settings import settings

engine = create_engine(settings.DATABASE)


def get_session():
    with Session(engine) as session:
        yield session
