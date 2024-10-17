from datetime import datetime

from sqlalchemy import JSON, BigInteger, ForeignKey,  SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from exako.database import table_registry


@table_registry.mapped_as_dataclass
class Exercise:
    __tablename__ = 'exercise'

    id: Mapped[int] = mapped_column(BigInteger,  primary_key=True)
    language: Mapped[str] = mapped_column(String(7), nullable=False)
    type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    level: Mapped[str | None] = mapped_column(String(2), nullable=True)
    term_id: Mapped[int | None] = mapped_column(
        ForeignKey('term.id', ondelete='CASCADE'),
        nullable=True,
    )
    term_example_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_example.id', ondelete='CASCADE'),
        nullable=True,
    )
    term_pronunciation_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_pronunciation.id', ondelete='CASCADE'),
        nullable=True,
    )
    term_lexical_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_lexical.id', ondelete='CASCADE'),
        nullable=True,
    )
    term_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_definition.id', ondelete='CASCADE'),
        nullable=True,
    )
    term_image_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_image.id', ondelete='CASCADE'),
        nullable=True,
    )
    additional_content: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )


@table_registry.mapped_as_dataclass
class ExerciseHistory:
    __tablename__ = 'exercise_history'

    id: Mapped[int] = mapped_column(BigInteger,  primary_key=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey('exercise.id', ondelete='SET NULL')
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='SET NULL')
    )
    correct: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    response: Mapped[dict | None] = mapped_column(
        JSON, default=None, nullable=True
    )
    request: Mapped[dict | None] = mapped_column(
        JSON, default=None, nullable=True
    )
