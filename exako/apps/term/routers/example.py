from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fief_client import FiefUserInfo
from sqlalchemy.exc import IntegrityError

from exako.apps.term import constants, schema
from exako.apps.term.repository import (
    TermExampleLinkRepository,
    TermExampleRepository,
    TermExampleTranslationRepository,
)
from exako.auth import current_admin_user
from exako.core import schema as core_schema
from exako.core.pagination import Page

example_router = APIRouter()


@example_router.post(
    path='',
    status_code=201,
    response_model=schema.TermExampleView,
    responses={
        **core_schema.PERMISSION_DENIED,
        **core_schema.OBJECT_NOT_FOUND,
        409: {
            'description': 'Modelo já fornecido já está ligado com o exemplo específicada.',
            'content': {
                'application/json': {
                    'example': {'detail': 'example already linked with this model.'}
                }
            },
        },
    },
    summary='Criação de exemplos sobre um termo.',
    description="""
        Endpoint utilizado para criação de exemplos para termos ou definições.
        Não poderá constar exemplos repetidos em uma determinada linguagem, para isso se o exemplo enviado já exisitir ele será retornado e não criado.
        Só poderá ser enviado um dos 3 objetos para ligação com o exemplo fornecido.
        term - Exemplo para termos
        term_definition - Exemplo para definições
        term_lexical - Exemplo para lexical
    """,
)
def create_example(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    example_repository: Annotated[
        TermExampleRepository,
        Depends(TermExampleRepository),
    ],
    link_repository: Annotated[
        TermExampleLinkRepository, Depends(TermExampleLinkRepository)
    ],
    example_schema: schema.TermExampleSchema,
):
    example, _ = example_repository.get_or_create(
        defaults=example_schema.model_dump(
            include={
                'level',
                'additional_content',
            }
        ),
        **example_schema.model_dump(
            include={
                'language',
                'example',
            }
        ),
    )

    try:
        link_repository.create(
            term_example_id=example.id,
            **example_schema.model_dump(
                include={
                    'highlight',
                    'term_example',
                    'term',
                    'term_definition',
                    'term_lexical',
                },
            ),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail='example already linked with this model.',
        )

    return {
        **example.model_dump(),
        'highlight': example_schema.highlight,
    }


@example_router.post(
    path='/translation',
    status_code=201,
    response_model=schema.TermExampleTranslationView,
    responses={
        **core_schema.PERMISSION_DENIED,
        **core_schema.OBJECT_NOT_FOUND,
        409: {
            'description': 'Modelo já fornecido já está ligado com a frase específicada.',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'the example is already linked with this model.'
                    }
                }
            },
        },
    },
    summary='Criação de traduções para exemplos sobre um termo.',
    description="""
        Endpoint utilizado para criação tradução para exemplos de termos ou definições.
        Só poderá ser enviado um dos 3 objetos para ligação com o exemplo fornecido.
        expression, language  - Exemplo para termos
        term_definition_id - Exemplo para definições
        term_lexical_id - Exemplo para lexical
    """,
)
def create_example_translation(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    repository: Annotated[
        TermExampleTranslationRepository, Depends(TermExampleTranslationRepository)
    ],
    translation_schema: schema.TermExampleTranslationSchema,
):
    try:
        translation = repository.create(
            **translation_schema.model_dump(
                include={
                    'language',
                    'term_example',
                    'translation',
                    'additional_content',
                }
            ),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail='translation already exists for this example.'
        )

    return {
        **translation.model_dump(),
        'highlight': translation_schema.highlight,
    }


@example_router.get(
    path='',
    summary='Consulta de exemplos sobre um termo.',
    description='Endpoint utilizado para consultar exemplos de termos ou definições.',
)
def list_examples(
    repository: Annotated[TermExampleRepository, Depends(TermExampleRepository)],
    filter_schema: Annotated[schema.TermExampleFilter, Query()],
) -> Page[schema.TermExampleView]:
    return repository.list(
        filter_params=filter_schema.model_dump(include={'level'}, exclude_none=True),
        link_params=filter_schema.model_dump(exclude={'level'}, exclude_none=True),
    )


@example_router.get(
    path='/translation/{term_example}/{language}',
    response_model=schema.TermExampleTranslationView,
    responses={**core_schema.OBJECT_NOT_FOUND},
    summary='Consulta da tradução dos exemplos.',
    description='Endpoint para consultar a tradução da tradução de um determinado exemplo.',
)
def get_example_translation(
    repository: Annotated[
        TermExampleTranslationRepository, Depends(TermExampleTranslationRepository)
    ],
    term_example: int,
    language: constants.Language,
):
    return repository.get_or_404(
        term_example_id=term_example,
        language=language,
    )
