from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fief_client import FiefUserInfo
from sqlalchemy.exc import IntegrityError

from exako.apps.term import constants, schema
from exako.apps.term.repository import TermRepository
from exako.apps.term.routers.definition import definition_router
from exako.apps.term.routers.example import example_router
from exako.apps.term.routers.image import image_router
from exako.apps.term.routers.lexical import lexical_router
from exako.apps.term.routers.pronunciation import pronunciation_router
from exako.auth import current_admin_user
from exako.core import schema as core_schema
from exako.core.pagination import Page

term_router = APIRouter()

term_router.include_router(lexical_router, prefix='/lexical')
term_router.include_router(pronunciation_router, prefix='/pronunciation')
term_router.include_router(example_router, prefix='/example')
term_router.include_router(definition_router, prefix='/definition')
term_router.include_router(image_router, prefix='/image')


@term_router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    response_model=schema.TermView,
    responses={
        **core_schema.PERMISSION_DENIED,
        status.HTTP_409_CONFLICT: {
            'content': {
                'application/json': {
                    'example': {'detail': 'term already exists in this language.'}
                }
            },
        },
    },
    summary='Criação de um novo termo.',
    description="""
        Endpoint utilizado para a criação de um termo, palavra ou expressão de um certo idioma.
        A princípio, poderá existir somente um termo com o mesmo valor de expressão de texto para cada idioma.
    """,
)
def create_term(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    repository: Annotated[TermRepository, Depends(TermRepository)],
    term_schema: schema.TermSchema,
):
    try:
        return repository.create(**term_schema.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail='term already exists in this language.',
        )


@term_router.get(
    path='',
    response_model=schema.TermView,
    responses={
        **core_schema.OBJECT_NOT_FOUND,
    },
    summary='Consulta de um termo existente.',
    description='Endpoint utilizado para a consultar um termo, palavra ou expressão específica de um certo idioma.',
)
def get_term(
    repository: Annotated[TermRepository, Depends(TermRepository)],
    content: str,
    language: constants.Language,
):
    return repository.get_or_404(
        statement=TermRepository.get_term_by_content_statement(
            content=content,
            language=language,
        ),
    )


@term_router.get(
    path='/search',
    summary='Procura de termos.',
    description='Endpoint utilizado para procurar um termo, palavra ou expressão específica de um certo idioma de acordo com o valor enviado.',
)
def search_term(
    repository: Annotated[TermRepository, Depends(TermRepository)],
    content: str,
    language: constants.Language,
) -> Page[schema.TermView]:
    return repository.list(
        statement=TermRepository.search_term_statement(content, language),
        paginate=True,
    )


@term_router.get(
    path='/search/reverse',
    summary='Procura de termos por significados.',
    description='Endpoint utilizado para procurar um termo, palavra ou expressão de um certo idioma pelo seu significado na linguagem de tradução e termo especificados.',
)
def search_reverse(
    repository: Annotated[TermRepository, Depends(TermRepository)],
    content: str,
    language: constants.Language,
    translation_language: constants.Language,
) -> Page[schema.TermView]:
    return repository.list(
        statement=TermRepository.search_reverse_term_statement(
            content, language, translation_language
        ),
        paginate=True,
    )


@term_router.get(
    path='/index',
    summary='Listagem dos termos por ordem alfabética.',
    description='Endpoint utilizado para listar todos os termos de uma linguagem em ordem alfabética.',
)
def term_index(
    repository: Annotated[TermRepository, Depends(TermRepository)],
    char: str = Query(pattern=r'^[a-zA-Z]$'),
    language: constants.Language = Query(...),
) -> Page[schema.TermView]:
    return repository.list(
        statement=TermRepository.index_term_statement(char, language),
        paginate=True,
    )
