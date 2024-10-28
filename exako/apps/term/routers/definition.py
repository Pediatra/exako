from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fief_client import FiefUserInfo
from sqlalchemy.exc import IntegrityError

from exako.apps.term import constants, schema
from exako.apps.term.repository import (
    TermDefinitionRepository,
    TermDefinitionTranslationRepository,
)
from exako.auth import current_admin_user
from exako.core import schema as core_schema

definition_router = APIRouter()


@definition_router.post(
    path='',
    status_code=201,
    response_model=schema.TermDefinitionView,
    responses={
        **core_schema.PERMISSION_DENIED,
        **core_schema.OBJECT_NOT_FOUND,
        409: {
            'description': 'A definição já existe para esse termo.',
            'content': {
                'application/json': {
                    'example': {'detail': 'definition already exists to this term.'}
                }
            },
        },
    },
    summary='Criação das definições de um termo.',
    description='Endpoint utilizado para criar uma definição de um certo termo de um determinado idioma.',
)
def create_definition(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    repository: Annotated[TermDefinitionRepository, Depends(TermDefinitionRepository)],
    definition_schema: schema.TermDefinitionSchema,
):
    return repository.create(**definition_schema.model_dump())


@definition_router.post(
    path='/translation',
    status_code=201,
    response_model=schema.TermDefinitionTranslationView,
    responses={
        **core_schema.PERMISSION_DENIED,
        **core_schema.OBJECT_NOT_FOUND,
        409: {
            'description': 'A tradução nesse idioma enviada para essa definição já existe.',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'translation language for this definition is already registered.'
                    }
                }
            },
        },
    },
    summary='Criação da tradução das definições de um termo.',
    description='Endpoint utilizado para criar uma tradução para uma definição de um certo termo de um determinado idioma.',
)
def create_definition_translation(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    repository: Annotated[
        TermDefinitionTranslationRepository,
        Depends(TermDefinitionTranslationRepository),
    ],
    translation_schema: schema.TermDefinitionTranslationSchema,
):
    try:
        return repository.create(**translation_schema.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail='translation language for this definition is already registered.',
        )


@definition_router.get(
    path='',
    summary='Consulta das definições de um termo.',
    description='Endpoint utilizado para consultar as definição de um certo termo de um determinado idioma.',
)
def list_definitions(
    repository: Annotated[TermDefinitionRepository, Depends(TermDefinitionRepository)],
    filter_schema: Annotated[schema.ListTermDefintionFilter, Query()],
):
    return repository.list(**filter_schema.model_dump(exclude_none=True))


@definition_router.get(
    path='/translation/{term_definition_id}/{language}',
    response_model=schema.TermDefinitionTranslationView,
    responses={**core_schema.OBJECT_NOT_FOUND},
    summary='Consulta a tradução da definição de um termo.',
    description='Endpoint utilizado para consultar a tradução das definições de um certo termo de um determinado idioma.',
)
def get_definition_translation(
    repository: Annotated[
        TermDefinitionTranslationRepository,
        Depends(TermDefinitionTranslationRepository),
    ],
    term_definition_id: int,
    language: constants.Language,
):
    return repository.get_or_404(
        term_definition_id=term_definition_id,
        language=language,
    )


@definition_router.get(
    'meaning/{term_id}/{translation_language}',
    response_model=schema.TermMeaningView,
    summary='Consulta as traduções de um termo.',
)
def list_term_meanings(
    translation_repository: Annotated[
        TermDefinitionTranslationRepository,
        Depends(TermDefinitionTranslationRepository),
    ],
    term_id: int,
    translation_language: constants.Language,
):
    return schema.TermMeaningView(
        meanings=translation_repository.list_meaning(
            term_id,
            translation_language,
        )
    )
