from enum import Enum, IntEnum


class Choices(Enum):
    """Base class for creating enumerated choices with labels."""

    def __new__(cls, value, label):
        obj = super().__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @classmethod
    def choices(cls):
        """Returns a list of tuples with all choices in the format (value, label)."""
        return [(member.value, member.label) for member in cls]

    @classmethod
    def labels(cls):
        """Returns a list of all labels."""
        return [member.label for member in cls]

    @classmethod
    def values(cls):
        """Returns a list of all values."""
        return [member.value for member in cls]

    def __str__(self):
        return str(self.label)


class IntegerChoices(Choices, IntEnum):
    """Class for creating enumerated integer choices with labels."""

    pass


class TextChoices(Choices, Enum):
    """Class for creating enumerated string choices with labels."""

    pass
