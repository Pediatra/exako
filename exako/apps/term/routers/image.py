from typing import Annotated

from fastapi import APIRouter, Depends
from fief_client import FiefUserInfo

from exako.apps.term import schema
from exako.apps.term.repository import TermImageRepository
from exako.auth import current_admin_user
from exako.core import schema as core_schema

image_router = APIRouter()


@image_router.post(
    path='',
    status_code=201,
    response_model=schema.TermImageView,
    responses={
        **core_schema.PERMISSION_DENIED,
        **core_schema.OBJECT_NOT_FOUND,
    },
    summary='Criação de imagem para termo.',
    description='Endpoint utilizado para enviar imagens que serão associadas com termos existentes.',
)
def create_term_image(
    user: Annotated[FiefUserInfo, Depends(current_admin_user)],
    repository: Annotated[TermImageRepository, Depends(TermImageRepository)],
    exercise_schema: schema.TermImageSchema,
):
    return repository.create(**exercise_schema.model_dump())


@image_router.get(
    path='/{term_id}',
    response_model=schema.TermImageView,
    responses={**core_schema.OBJECT_NOT_FOUND},
    summary='Criação de imagem para termo.',
    description='Endpoint utilizado para enviar imagens que serão associadas com termos existentes.',
)
def get_term_image(
    repository: Annotated[TermImageRepository, Depends(TermImageRepository)],
    term_id: int,
):
    return repository.get_or_404(term_id=term_id)
