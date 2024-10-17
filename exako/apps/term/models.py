from sqlalchemy import (
    ARRAY,
    JSON,
    BigInteger,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from exako.database import table_registry


@table_registry.mapped_as_dataclass
class Term:
    __tablename__ = 'term'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    content: Mapped[str] = mapped_column(String(256), nullable=False)
    language: Mapped[str] = mapped_column(String(7), nullable=False)
    additional_content: Mapped[dict] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        UniqueConstraint('content', 'language', name='uq_content_language'),
        Index(
            'idx_content_language',
            'content',
            'language',
            unique=True,
        ),
    )


@table_registry.mapped_as_dataclass
class TermLexical:
    __tablename__ = 'term_lexical'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    term_id: Mapped[int] = mapped_column(
        ForeignKey('term.id', ondelete='CASCADE'),
    )
    term_content_id: Mapped[int] = mapped_column(
        ForeignKey('term.id', ondelete='CASCADE'),
        nullable=True,
    )
    content: Mapped[str | None] = mapped_column(String(256), nullable=True)
    type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    additional_content: Mapped[dict | None] = mapped_column(JSON, nullable=True)


@table_registry.mapped_as_dataclass
class TermImage:
    __tablename__ = 'term_image'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    term_id: Mapped[int] = mapped_column(
        ForeignKey('term.id', ondelete='CASCADE'),
        unique=True,
    )
    image_url: Mapped[str] = mapped_column(String(256), nullable=False)


@table_registry.mapped_as_dataclass
class TermExample:
    __tablename__ = 'term_example'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    language: Mapped[str] = mapped_column(String(7), nullable=False)
    content: Mapped[str] = mapped_column(String(256), nullable=False)
    level: Mapped[str | None] = mapped_column(String(2), nullable=True)
    additional_content: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )


@table_registry.mapped_as_dataclass
class TermExampleTranslation:
    __tablename__ = 'term_example_translation'

    language: Mapped[str] = mapped_column(String(7), primary_key=True, nullable=False)
    translation: Mapped[str] = mapped_column(String(256), nullable=False)
    term_example_id: Mapped[int] = mapped_column(
        ForeignKey('term_example.id', ondelete='CASCADE'),
        primary_key=True,
    )

    __table_args__ = (
        UniqueConstraint(
            'language', 'term_example_id', name='uq_language_term_example'
        ),
    )


@table_registry.mapped_as_dataclass
class TermDefinition:
    __tablename__ = 'term_definition'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    part_of_speech: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    content: Mapped[str] = mapped_column(String(512), nullable=False)
    level: Mapped[str | None] = mapped_column(String(2), nullable=True)
    term_id: Mapped[int] = mapped_column(ForeignKey('term.id', ondelete='CASCADE'))
    term_lexical_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_lexical.id', ondelete='CASCADE'),
        nullable=True,
    )
    additional_content: Mapped[dict | None] = mapped_column(JSON, nullable=True)


@table_registry.mapped_as_dataclass
class TermDefinitionTranslation:
    __tablename__ = 'term_definition_translation'

    language: Mapped[str] = mapped_column(String(2), primary_key=True, nullable=False)
    translation: Mapped[str] = mapped_column(String(512), nullable=False)
    meaning: Mapped[str] = mapped_column(String(256), nullable=False)
    term_definition_id: Mapped[int] = mapped_column(
        ForeignKey('term_definition.id', ondelete='CASCADE'),
        primary_key=True,
    )

    __table_args__ = (
        UniqueConstraint(
            'language',
            'term_definition_id',
            name='uq_language_term_definition',
        ),
    )


@table_registry.mapped_as_dataclass
class TermPronunciation:
    __tablename__ = 'term_pronunciation'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    phonetic: Mapped[str] = mapped_column(String(256), nullable=False)
    audio_url: Mapped[str | None] = mapped_column(String(256), nullable=True)
    term_id: Mapped[int | None] = mapped_column(
        ForeignKey('term.id', ondelete='CASCADE'),
        nullable=True,
        unique=True,
    )
    term_example_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_example.id', ondelete='CASCADE'),
        nullable=True,
        unique=True,
    )
    term_lexical_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_lexical.id', ondelete='CASCADE'),
        nullable=True,
        unique=True,
    )


@table_registry.mapped_as_dataclass
class TermExampleLink:
    __tablename__ = 'term_example_link'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    highlight: Mapped[list[list[int]]] = mapped_column(
        ARRAY(Integer, dimensions=2), nullable=False
    )
    term_example_id: Mapped[int] = mapped_column(
        ForeignKey('term_example.id', ondelete='CASCADE')
    )
    term_id: Mapped[int | None] = mapped_column(
        ForeignKey('term.id', ondelete='CASCADE'),
        nullable=True,
    )
    term_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_definition.id', ondelete='CASCADE'),
        nullable=True,
    )
    term_lexical_id: Mapped[int | None] = mapped_column(
        ForeignKey('term_lexical.id', ondelete='CASCADE'),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint('term_id', 'term_example_id', name='uq_term_term_example'),
        UniqueConstraint(
            'term_definition_id',
            'term_example_id',
            name='uq_term_definition_term_example',
        ),
        UniqueConstraint(
            'term_lexical_id',
            'term_example_id',
            name='uq_term_lexical_term_example',
        ),
    )
