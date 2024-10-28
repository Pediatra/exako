from fastapi import HTTPException
from sqlmodel import SQLModel, exists, select, union_all

from exako.apps.term.models import (
    Term,
    TermDefinition,
    TermDefinitionTranslation,
    TermExample,
    TermExampleLink,
    TermExampleTranslation,
    TermLexical,
    TermPronunciation,
)
from exako.core.validator import Validator

term_validator = Validator(SQLModel, lambda instance: instance.__class__)


@term_validator.register(TermLexical)
def validate_term_content_same_as_term(session, instance):
    if not instance.term_content_id:
        return

    if instance.term_content_id == instance.term_id:
        raise HTTPException(
            status_code=422,
            detail='term_content cannot be the same as term lexical reference.',
        )


@term_validator.register(TermLexical)
def validate_term_lexical_term_value_language_ref(session, instance):
    if not instance.term_content_id:
        return

    languages = session.exec(
        select(Term.language).where(
            Term.id.in_([instance.term_content_id, instance.term_id])
        )
    ).all()
    if languages[0] != languages[1]:
        raise HTTPException(
            status_code=422,
            detail='term_content language have to be the same as term lexical reference.',
        )


@term_validator.register(TermDefinition)
def validate_term_definition_lexical_language_ref(session, instance):
    if not instance.term_lexical_id:
        return

    languages = session.exec(
        union_all(
            select(Term.language)
            .join(
                TermLexical,
                TermLexical.term_id == Term.id,
            )
            .where(TermLexical.id == instance.term_lexical_id),
            select(Term.language).where(Term.id == instance.term_id),
        )
    ).all()

    if languages[0] != languages[1]:
        raise HTTPException(
            status_code=422,
            detail='term_lexical language have to be the same as term reference.',
        )


@term_validator.register([TermPronunciation, TermExampleLink])
def validate_pronunciation_lexical_form(session, instance):
    if not instance.term_lexical_id:
        return

    if session.exec(
        select(
            exists().where(
                TermLexical.id == instance.term_lexical_id,
                TermLexical.term_content_id.is_not(None),
            )
        )
    ).first():
        raise HTTPException(
            status_code=422,
            detail='lexical with term_content cannot link with this model.',
        )


@term_validator.register(TermDefinitionTranslation)
def validate_term_definition_translation_language_reference(session, instance):
    language = session.exec(
        select(Term.language).join(
            TermDefinition, TermDefinition.id == instance.term_definition_id
        )
    ).first()
    if instance.language == language:
        raise HTTPException(
            status_code=422,
            detail='translation language reference cannot be same as language.',
        )


@term_validator.register(TermExampleTranslation)
def validate_term_example_translation_language_reference(session, instance):
    language = session.exec(
        select(TermExample.language).where(TermExample.id == instance.term_example_id)
    ).first()
    if instance.language == language:
        raise HTTPException(
            status_code=422,
            detail='translation language reference cannot be same as language.',
        )


@term_validator.register(TermExampleLink)
def validate_term_example_language_reference(session, instance):
    example_language = session.exec(
        select(TermExample.language).where(TermExample.id == instance.term_example_id)
    ).first()
    if instance.term_id:
        language = session.exec(
            select(Term.language).where(Term.id == instance.term_id)
        ).first()
    elif instance.term_definition_id:
        language = session.exec(
            select(Term.language).join(
                TermDefinition, TermDefinition.id == instance.term_definition_id
            )
        ).first()
    else:
        language = session.exec(
            select(Term.language).join(
                TermLexical, TermLexical.id == instance.term_lexical_id
            )
        ).first()

    if example_language != language:
        raise HTTPException(
            status_code=422,
            detail='term example language has to be the same as the link model.',
        )
