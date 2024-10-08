from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from exako.apps.core import schema as core_schema
from exako.apps.core.permissions import is_admin, permission_required
from exako.apps.exercise.api.routers import exercise_router
from exako.apps.term import constants
from exako.apps.term.api import schema
from exako.apps.term.api.routers.definition import definition_router
from exako.apps.term.api.routers.example import example_router
from exako.apps.term.api.routers.image import image_router
from exako.apps.term.api.routers.lexical import lexical_router
from exako.apps.term.api.routers.pronunciation import pronunciation_router
from exako.apps.term.models import Term
from exako.apps.user.auth.token import AuthBearer

term_router = Router(tags=['Termo'])
term_router.add_router('/pronunciation', pronunciation_router, tags=['Pronúncia'])
term_router.add_router('/definition', definition_router, tags=['Definição'])
term_router.add_router('/example', example_router, tags=['Exemplo'])
term_router.add_router('/lexical', lexical_router, tags=['Léxico'])
term_router.add_router('/exercise', exercise_router, tags=['Exercício'])
term_router.add_router('/image', image_router, tags=['Imagem'])


@term_router.post(
    path='',
    response={
        201: schema.TermView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
    },
    summary='Criação de um novo termo.',
    description="""
        Endpoint utilizado para a criação de um termo, palavra ou expressão de um certo idioma.
        A princípio, poderá existir somente um termo com o mesmo valor de expressão de texto para cada idioma.
        É importante salientar que se o valor do termo enviado for igual a um termo existente no idioma ele será retornado.
        Da mesma forma, se o valor do termo enviado for igual a uma forma idiomática (TermLexical - Type.Form) relacionada a um termo já existente no idioma, esse termo existente será retornado.
    """,
    auth=AuthBearer(),
    openapi_extra={
        'responses': {
            409: {
                'description': 'O termo já existe neste idioma.',
                'content': {
                    'application/json': {
                        'example': {'detail': 'term already exists in this language.'}
                    }
                },
            },
        }
    },
)
@permission_required([is_admin])
def create_term(request, term_schema: schema.TermSchema):
    if Term.objects.filter(
        expression__ct=term_schema.expression,
        language=term_schema.language,
    ).exists():
        raise HttpError(
            status_code=409, message='term already exists in this language.'
        )
    return 201, Term.objects.create(**term_schema.model_dump())


@term_router.get(
    path='',
    response={
        200: schema.TermView,
        404: core_schema.NotFound,
    },
    summary='Consulta de um termo existente.',
    description='Endpoint utilizado para a consultar um termo, palavra ou expressão específica de um certo idioma.',
)
def get_term(
    request,
    expression: str,
    language: constants.Language,
):
    return get_object_or_404(Term.objects.get(expression, language))


@term_router.get(
    path='/id/{term_id}',
    response={
        200: schema.TermView,
        404: core_schema.NotFound,
    },
    summary='Consulta de um termo existente.',
    description='Endpoint utilizado para a consultar um termo, palavra ou expressão específica de um certo idioma.',
)
def get_term_id(request, term_id: int):
    return get_object_or_404(Term, id=term_id)


@term_router.get(
    path='/search',
    response={200: list[schema.TermView]},
    summary='Procura de termos.',
    description='Endpoint utilizado para procurar um termo, palavra ou expressão específica de um certo idioma de acordo com o valor enviado.',
)
@paginate(PageNumberPagination)
def search_term(
    request,
    expression: str,
    language: constants.Language,
):
    return Term.objects.search(expression=expression, language=language)


@term_router.get(
    path='/search/meaning',
    response={200: list[schema.TermView]},
    summary='Procura de termos por significados.',
    description='Endpoint utilizado para procurar um termo, palavra ou expressão de um certo idioma pelo seu significado na linguagem de tradução e termo especificados.',
)
@paginate(PageNumberPagination)
def search_reverse(
    request,
    expression: str,
    language: constants.Language,
    translation_language: constants.Language,
):
    return Term.objects.search_reverse(
        expression=expression,
        language=language,
        translation_language=translation_language,
    )


@term_router.get(
    path='/index',
    response={200: list[schema.TermView]},
    summary='Listagem dos termos por ordem alfabética.',
    description='Endpoint utilizado para listar todos os termos de uma linguagem em ordem alfabética.',
)
@paginate(PageNumberPagination)
def term_index(
    request,
    char: str = Query(pattern=r'^[a-zA-Z]$'),
    language: constants.Language = Query(...),
):
    return Term.objects.filter(
        language=language,
        expression__startswith=char.lower(),
    )
