from typing import Callable

from sqlalchemy.event import listen
from sqlmodel import Session, SQLModel


class Validator:
    _registry: dict = {}

    def __init__(self, model: type[SQLModel], validate_strategy: Callable):
        def wrapper(_, connection, instance):
            value = validate_strategy(instance)
            if value not in self._registry:
                return
            with Session(connection) as session:
                for validation_func in self._registry[value]:
                    validation_func(instance=instance, session=session)

        listen(model, 'before_insert', wrapper, propagate=True)

    def register(self, value_list):
        if not isinstance(value_list, list):
            value_list = [value_list]

        def inner(f):
            for value in value_list:
                self._registry.setdefault(value, []).append(f)
            return f

        return inner
