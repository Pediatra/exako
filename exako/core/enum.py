import enum
from typing import Any, List, Tuple


class ChoicesType(enum.EnumMeta):
    """A metaclass for creating a enum choices."""

    def __new__(metacls, classname, bases, classdict, **kwds):
        labels = []
        for key in classdict._member_names:
            value = classdict[key]
            if (
                isinstance(value, (list, tuple))
                and len(value) > 1
                and isinstance(value[-1], str)
            ):
                *value, label = value
                value = tuple(value)
            else:
                label = key.replace('_', ' ').title()
            labels.append(label)
            dict.__setitem__(classdict, key, value)
        cls = super().__new__(metacls, classname, bases, classdict, **kwds)
        for member, label in zip(cls.__members__.values(), labels):
            member._label_ = label
        return enum.unique(cls)

    def __contains__(cls, member):
        if not isinstance(member, enum.Enum):
            return any(x.value == member for x in cls)
        return super().__contains__(member)

    @property
    def names(cls) -> List[str]:
        empty = ['__empty__'] if hasattr(cls, '__empty__') else []
        return empty + [member.name for member in cls]

    @property
    def choices(cls) -> List[Tuple[Any, str]]:
        empty = [(None, cls.__empty__)] if hasattr(cls, '__empty__') else []
        return empty + [(member.value, member.label) for member in cls]

    @property
    def labels(cls) -> List[str]:
        return [label for _, label in cls.choices]

    @property
    def values(cls) -> List[Any]:
        return [value for value, _ in cls.choices]


class Choices(enum.Enum, metaclass=ChoicesType):
    """Class for creating enumerated choices."""

    @property
    def label(self) -> str:
        return self._label_

    def __str__(self) -> str:
        return self.value


class IntegerChoices(Choices, enum.IntEnum):
    """Class for creating enumerated integer choices."""


class TextChoices(Choices, str, enum.Enum):
    """Class for creating enumerated string choices."""
