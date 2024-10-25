from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fief_client import FiefUserInfo
from sqlalchemy.exc import IntegrityError

from exako.apps.term import schema
from exako.apps.term.repository import TermPronunciationRepository
from exako.auth import current_admin_user
from exako.core import schema as core_schema

pronunciation_router = APIRouter()


@pronunciation_router.post(
    path='',
    status_code=201,
    response_model=schema.TermPronunciationView,
    responses={
        **core_schema.PERMISSION_DENIED,
        **core_schema.OBJECT_NOT_FOUND,
    },
    summary='Criação de pronúncia.',
    description="""
        Endpoint utilizado para criar pronúncias com áudio, fonemas e descrição sobre um determinado objeto.
        Só poderá ser enviado um dos 3 objetos para ligação com a pronúncia específica.
        term - Pronúncia para termos
        term_example - Pronúncia para exemplos
        term_lexical - Pronúncia para lexical
    """,
)
def create_pronunciation(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    repository: Annotated[
        TermPronunciationRepository, Depends(TermPronunciationRepository)
    ],
    pronunciation_schema: schema.TermPronunciationSchema,
):
    try:
        return repository.create(**pronunciation_schema.model_dump(exclude_none=True))
    except IntegrityError:
        raise HTTPException(status_code=409, detail='pronunciation already exists.')


@pronunciation_router.get(
    path='',
    response_model=schema.TermPronunciationView,
    response={**core_schema.OBJECT_NOT_FOUND},
    summary='Consulta das pronúncias.',
    description='Endpoint utilizado para consultar pronúncias com áudio, fonemas e descrição sobre um determinado modelo.',
)
def get_pronunciation(
    repository: Annotated[
        TermPronunciationRepository, Depends(TermPronunciationRepository)
    ],
    pronunciation_filter: Annotated[schema.TermPronunciationLinkSchema, Query()],
):
    return repository.get_or_404(pronunciation_filter.model_dump(exclude_none=True))
