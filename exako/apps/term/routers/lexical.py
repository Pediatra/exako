from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fief_client import FiefUserInfo

from exako.apps.term import schema
from exako.apps.term.repository import TermLexicalRepository
from exako.auth import current_admin_user
from exako.core import schema as core_schema

lexical_router = APIRouter()


@lexical_router.post(
    path='',
    status_code=201,
    response_model=schema.TermLexicalView,
    responses={
        **core_schema.PERMISSION_DENIED,
        **core_schema.OBJECT_NOT_FOUND,
        409: {
            'description': 'O léxico já existe para esse termo.',
            'content': {
                'application/json': {
                    'example': {'detail': 'lexical already exists to this term.'}
                }
            },
        },
    },
    summary='Criação de relação de uma relação lexical.',
    description='Endpoint utilizado para criação de relações lexicais entre termos.',
)
def create_lexical(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    repository: Annotated[TermLexicalRepository, Depends(TermLexicalRepository)],
    lexical_schema: schema.TermLexicalSchema,
):
    return repository.create(**lexical_schema.model_dump())


@lexical_router.get(
    path='',
    response_model=list[schema.TermLexicalView],
    summary='Consulta de relação de uma relação lexical.',
    description='Endpoint utilizado para consultar de relações lexicais entre termos.',
)
def list_lexicals(
    repository: Annotated[TermLexicalRepository, Depends(TermLexicalRepository)],
    filter_query: Annotated[schema.TermLexicalFilter, Query()],
):
    return repository.list(**filter_query.model_dump(exclude_none=True))
