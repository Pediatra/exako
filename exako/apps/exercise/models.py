from datetime import datetime
from typing import Any
from uuid import UUID

import sqlmodel as sm
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB


class Exercise(sm.SQLModel, table=True):
    __tablename__ = 'exercise'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    language: str = sm.Field(max_length=7, nullable=False)
    type: int = sm.Field(nullable=False)
    level: str | None = sm.Field(default=None, max_length=2)
    term_id: int | None = sm.Field(default=None, foreign_key='term.id')
    term_example_id: int | None = sm.Field(default=None, foreign_key='term_example.id')
    term_pronunciation_id: int | None = sm.Field(
        default=None, foreign_key='term_pronunciation.id'
    )
    term_lexical_id: int | None = sm.Field(default=None, foreign_key='term_lexical.id')
    term_definition_id: int | None = sm.Field(
        default=None, foreign_key='term_definition.id'
    )
    term_image_id: int | None = sm.Field(default=None, foreign_key='term_image.id')
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    __table_args__ = (
        sm.Index(
            'unique_order_sentence',
            'type',
            'language',
            'term_example_id',
            unique=True,
            postgresql_where='type = 0',
        ),
        sm.Index(
            'unique_listen_term',
            'type',
            'language',
            'term_id',
            'term_pronunciation_id',
            unique=True,
            postgresql_where='type = 1',
        ),
        sm.Index(
            'unique_listen_term_lexical',
            'type',
            'language',
            'term_lexical_id',
            'term_pronunciation_id',
            unique=True,
            postgresql_where='type = 1',
        ),
        sm.Index(
            'unique_listen_term_mchoice',
            'type',
            'language',
            'term_id',
            'term_pronunciation_id',
            unique=True,
            postgresql_where='type = 2',
        ),
        sm.Index(
            'unique_listen_sentence',
            'type',
            'language',
            'term_example_id',
            'term_pronunciation_id',
            unique=True,
            postgresql_where='type = 3',
        ),
        sm.Index(
            'unique_speak_term',
            'type',
            'language',
            'term_id',
            unique=True,
            postgresql_where='type = 4',
        ),
        sm.Index(
            'unique_speak_term_lexical',
            'type',
            'language',
            'term_lexical_id',
            unique=True,
            postgresql_where='type = 4',
        ),
        sm.Index(
            'unique_speak_sentence',
            'type',
            'language',
            'term_example_id',
            unique=True,
            postgresql_where='type = 5',
        ),
        sm.Index(
            'unique_term_mchoice',
            'type',
            'language',
            'term_id',
            'term_example_id',
            unique=True,
            postgresql_where='type = 6',
        ),
        sm.Index(
            'unique_term_lexical_mchoice',
            'type',
            'language',
            'term_example_id',
            'term_lexical_id',
            unique=True,
            postgresql_where='type = 6',
        ),
        sm.Index(
            'unique_term_definition_mchoice',
            'type',
            'language',
            'term_definition_id',
            'term_id',
            unique=True,
            postgresql_where='type = 7',
        ),
        sm.Index(
            'unique_term_image_mchoice',
            'type',
            'language',
            'term_id',
            'term_image_id',
            'term_pronunciation_id',
            unique=True,
            postgresql_where='type = 8',
        ),
        sm.Index(
            'unique_term_image_mchoice_text',
            'type',
            'language',
            'term_id',
            'term_image_id',
            unique=True,
            postgresql_where='type = 9',
        ),
        sm.Index(
            'unique_term_conection',
            'type',
            'language',
            'term_id',
            unique=True,
            postgresql_where='type = 10',
        ),
    )


class ExerciseHistory(sm.SQLModel, table=True):
    __tablename__ = 'exercise_history'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    exercise_id: int | None = sm.Field(default=None, foreign_key='exercise.id')
    user_id: UUID = sm.Field(nullable=False)
    correct: bool = sm.Field(nullable=False)
    created_at: datetime = sm.Field(default_factory=func.now)
    response: dict[str, Any] | None = sm.Field(default=None, sa_column=sm.Column(JSONB))
    request: dict[str, Any] | None = sm.Field(default=None, sa_column=sm.Column(JSONB))
