from typing import Any

import sqlmodel as sm
from sqlalchemy import ARRAY
from sqlalchemy.dialects.postgresql import JSONB


class Term(sm.SQLModel, table=True):
    __tablename__ = 'term'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    content: str = sm.Field(max_length=256, nullable=False)
    language: str = sm.Field(max_length=7, nullable=False)
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    lexical_contents: list['TermLexical'] | None = sm.Relationship(
        back_populates='term_content',
        sa_relationship_kwargs={'primaryjoin': 'TermLexical.term_content_id==Term.id'},
    )
    lexicals: list['TermLexical'] = sm.Relationship(
        back_populates='term',
        sa_relationship_kwargs={'primaryjoin': 'TermLexical.term_id==Term.id'},
    )
    images: list['TermImage'] = sm.Relationship(back_populates='term')
    definitions: list['TermDefinition'] = sm.Relationship(back_populates='term')
    pronunciations: list['TermPronunciation'] | None = sm.Relationship(
        back_populates='term'
    )

    __table_args__ = (
        sm.Index(
            'idx_content_language',
            'content',
            'language',
            unique=True,
        ),
    )


class TermLexical(sm.SQLModel, table=True):
    __tablename__ = 'term_lexical'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    term_id: int = sm.Field(foreign_key='term.id', nullable=False)
    term_content_id: int | None = sm.Field(
        default=None,
        foreign_key='term.id',
        nullable=True,
    )
    content: str | None = sm.Field(default=None, max_length=256)
    type: int = sm.Field(nullable=False)
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    term: Term = sm.Relationship(
        back_populates='lexicals',
        sa_relationship_kwargs={'primaryjoin': 'TermLexical.term_id==Term.id'},
    )
    term_content: Term | None = sm.Relationship(
        back_populates='lexical_contents',
        sa_relationship_kwargs={'primaryjoin': 'TermLexical.term_content_id==Term.id'},
    )
    definitions: list['TermDefinition'] = sm.Relationship(back_populates='term_lexical')
    pronunciations: list['TermPronunciation'] | None = sm.Relationship(
        back_populates='term_lexical'
    )


class TermImage(sm.SQLModel, table=True):
    __tablename__ = 'term_image'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    term_id: int = sm.Field(foreign_key='term.id', nullable=False, unique=True)
    image_url: str = sm.Field(max_length=256, nullable=False)

    term: Term = sm.Relationship(back_populates='images')


class TermExample(sm.SQLModel, table=True):
    __tablename__ = 'term_example'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    language: str = sm.Field(max_length=7, nullable=False)
    content: str = sm.Field(max_length=256, nullable=False)
    level: str | None = sm.Field(default=None, max_length=2)
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    translations: list['TermExampleTranslation'] = sm.Relationship(
        back_populates='term_example'
    )
    pronunciations: list['TermPronunciation'] | None = sm.Relationship(
        back_populates='term_example'
    )


class TermExampleTranslation(sm.SQLModel, table=True):
    __tablename__ = 'term_example_translation'

    language: str = sm.Field(max_length=7, primary_key=True, nullable=False)
    translation: str = sm.Field(max_length=256, nullable=False)
    term_example_id: int = sm.Field(foreign_key='term_example.id', primary_key=True)
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    term_example: TermExample = sm.Relationship(back_populates='translations')


class TermDefinition(sm.SQLModel, table=True):
    __tablename__ = 'term_definition'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    part_of_speech: int = sm.Field(nullable=False)
    content: str = sm.Field(max_length=512, nullable=False)
    level: str | None = sm.Field(default=None, max_length=2)
    term_id: int = sm.Field(foreign_key='term.id', nullable=False)
    term_lexical_id: int | None = sm.Field(
        default=None, foreign_key='term_lexical.id', nullable=True
    )
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    term: Term = sm.Relationship(back_populates='definitions')
    term_lexical: TermLexical = sm.Relationship(back_populates='definitions')
    translations: list['TermDefinitionTranslation'] = sm.Relationship(
        back_populates='term_definition'
    )


class TermDefinitionTranslation(sm.SQLModel, table=True):
    __tablename__ = 'term_definition_translation'

    language: str = sm.Field(max_length=2, primary_key=True, nullable=False)
    translation: str = sm.Field(max_length=512, nullable=False)
    meaning: str = sm.Field(max_length=256, nullable=False)
    term_definition_id: int = sm.Field(
        foreign_key='term_definition.id', primary_key=True
    )
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    term_definition: TermDefinition = sm.Relationship(back_populates='translations')


class TermPronunciation(sm.SQLModel, table=True):
    __tablename__ = 'term_pronunciation'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    phonetic: str = sm.Field(max_length=256, nullable=False)
    audio_url: str | None = sm.Field(default=None, max_length=256)
    term_id: int | None = sm.Field(default=None, foreign_key='term.id', unique=True)
    term_example_id: int | None = sm.Field(
        default=None, foreign_key='term_example.id', unique=True
    )
    term_lexical_id: int | None = sm.Field(
        default=None, foreign_key='term_lexical.id', unique=True
    )
    additional_content: dict[str, Any] | None = sm.Field(
        default=None, sa_column=sm.Column(JSONB)
    )

    term: Term | None = sm.Relationship(back_populates='pronunciations')
    term_lexical: TermLexical | None = sm.Relationship(back_populates='pronunciations')
    term_example: TermExample | None = sm.Relationship(back_populates='pronunciations')


class TermExampleLink(sm.SQLModel, table=True):
    __tablename__ = 'term_example_link'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    highlight: list[list[int]] | None = sm.Field(
        default=None, sa_column=sm.Column(ARRAY(sm.Integer, dimensions=2))
    )
    term_example_id: int = sm.Field(foreign_key='term_example.id', nullable=False)
    term_id: int | None = sm.Field(default=None, foreign_key='term.id', nullable=True)
    term_definition_id: int | None = sm.Field(
        default=None, foreign_key='term_definition.id', nullable=True
    )
    term_lexical_id: int | None = sm.Field(
        default=None, foreign_key='term_lexical.id', nullable=True
    )

    __table_args__ = (
        sm.UniqueConstraint(
            'term_id',
            'term_example_id',
            name='term_example_link_term_term_example',
        ),
        sm.UniqueConstraint(
            'term_definition_id',
            'term_example_id',
            name='term_example_link_term_definition_term_example',
        ),
        sm.UniqueConstraint(
            'term_lexical_id',
            'term_example_id',
            name='term_example_link_term_lexical_term_example',
        ),
    )
