from functools import cached_property

from fastapi import Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate as paginate_query
from sqlalchemy import Select
from sqlmodel import Column, Session, SQLModel, Table, inspect, select

from exako.database import get_session


def _get_or_404(
    model: type[SQLModel] | Table,
    session: Session,
    statement: Select | None = None,
    **kwargs,
):
    if statement is None:
        statement = select(model)
    if kwargs and hasattr(statement, 'filter_by'):
        statement = statement.filter_by(**kwargs)
    instance = session.exec(statement).first()
    if instance is None:
        class_name = model.__name__ if hasattr(model, '__name__') else model.name
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{class_name.lower()} object does not exists.',
        )
    return instance


class BaseRepository:
    model: type[SQLModel]
    session: Session
    ordering: list[Column]

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    @cached_property
    def _foreign_keys(self):
        inspector = inspect(self.model)
        foreign_keys = {
            column.key: fk.column.table
            for column in inspector.columns.values()
            for fk in column.foreign_keys
        }
        return foreign_keys

    def _validate_foreign_keys(self, **fields):
        for name, value in fields.items():
            if value is None:
                continue
            if name in self._foreign_keys:
                _get_or_404(self._foreign_keys[name], self.session, id=value)

    def create(self, **kwargs):
        self._validate_foreign_keys(**kwargs)

        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: type[SQLModel]):
        self.session.delete(instance)
        self.session.commit()

    def update(self, instance: type[SQLModel], **kwargs):
        self._validate_foreign_keys(**kwargs)

        for field, value in instance.model_dump(exclude_none=True):
            setattr(instance, field, value)

        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get_or_404(
        self,
        *,
        statement: Select | None = None,
        **kwargs,
    ):
        return _get_or_404(
            self.model,
            self.session,
            statement,
            **kwargs,
        )

    def list(self, statement: Select | None = None, paginate: bool = False, **kwargs):
        if statement is None:
            statement = select(self.model)
        if kwargs and hasattr(statement, 'filter_by'):
            statement = statement.filter_by(**kwargs)
        statement = statement.order_by(*self.ordering)
        if paginate:
            return paginate_query(self.session, statement)
        return self.session.exec(statement).all()

    def get_or_create(self, *, statement=None, defaults=None, **kwargs):
        try:
            return self.get_or_404(statement=statement, **kwargs), False
        except HTTPException:
            kwargs |= defaults or {}
            return self.create(**kwargs), True
