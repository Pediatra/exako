import pytest

from exako.apps.term.constants import Language, TermLexicalType
from exako.apps.term.models import Term
from exako.core.url import set_url_params
from exako.main import app
from exako.tests.factories.term import (
    TermDefinitionTranslationFactory,
    TermFactory,
    TermLexicalFactory,
)

create_term_route = app.url_path_for('create_term')


def get_term_route(content, language):
    url = app.url_path_for('get_term')
    return set_url_params(
        url,
        content=content,
        language=language,
    )


def search_term_route(content, language):
    url = app.url_path_for('search_term')
    return set_url_params(
        url,
        content=content,
        language=language,
    )


def search_reverse_route(content, language, translation_language):
    url = app.url_path_for('search_reverse')
    return set_url_params(
        url,
        content=content,
        language=language,
        translation_language=translation_language,
    )


def term_index_route(char, language):
    url = app.url_path_for('term_index')
    return set_url_params(
        url,
        char=char,
        language=language,
    )


def test_create_term(client, generate_payload):
    payload = generate_payload(TermFactory)

    response = client.post(
        create_term_route,
        json=payload,
    )

    assert response.status_code == 201
    payload['id'] = response.json()['id']
    assert Term(**response.json()) == Term(**payload)


def test_create_term_already_exists(client, generate_payload):
    payload = generate_payload(TermFactory)
    TermFactory(**payload)

    response = client.post(
        create_term_route,
        json=payload,
    )

    assert response.status_code == 409


def test_get_term(client):
    term = TermFactory(content='ãQübérmäßíg âçãoQã')

    response = client.get(get_term_route('aqubermassig acaoqa', term.language))

    assert response.status_code == 200
    assert Term(**response.json()) == term


def test_get_term_lexical(client):
    term = TermFactory()
    TermLexicalFactory(
        term=term,
        type=TermLexicalType.INFLECTION,
        content='ãQübérmäßíg âçãoQã',
    )

    response = client.get(get_term_route('aqubermassig acaoqa', term.language))

    assert response.status_code == 200
    assert Term(**response.json()) == term


def test_get_term_not_found(client):
    response = client.get(get_term_route('content', Language.PORTUGUESE_BRAZIL))
    assert response.status_code == 404


def test_search_term(client):
    term = TermFactory(content='ãQübérmäßíg âçãoQã')
    TermFactory.create_batch(size=5)

    response = client.get(search_term_route('aqubermassig acaoqa', term.language))

    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert term in [Term(**res) for res in response.json()['items']]


def test_search_term_lexical(client):
    term = TermFactory(content='not a text')
    TermLexicalFactory(
        term=term,
        type=TermLexicalType.INFLECTION,
        content='ãQübérmäßíg âçãoQã',
    )
    TermFactory.create_batch(size=5)

    response = client.get(search_term_route('aqubermassig acaoqa', term.language))

    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert term in [Term(**res) for res in response.json()['items']]


def test_search_term_empty(client):
    TermFactory.create_batch(size=5)

    response = client.get(
        search_term_route('aqubermassig acaoqa', Language.PORTUGUESE_BRAZIL)
    )

    assert response.status_code == 200
    assert len(response.json()['items']) == 0


def test_search_reverse(client):
    term_definition_translation = TermDefinitionTranslationFactory(
        meaning='ãQübérmäßíg âçãoQã'
    )

    response = client.get(
        search_reverse_route(
            'aqubermassig acaoqa',
            term_definition_translation.term_definition.term.language,
            term_definition_translation.language,
        )
    )

    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert term_definition_translation.term_definition.term in [
        Term(**res) for res in response.json()['items']
    ]


def test_search_reverse_empty(client):
    TermFactory.create_batch(size=5)

    response = client.get(
        search_reverse_route(
            'aqubermassig acaoqa',
            Language.PORTUGUESE_BRAZIL,
            Language.ENGLISH_USA,
        )
    )

    assert response.status_code == 200
    assert len(response.json()['items']) == 0


def test_term_index(client):
    terms = [
        TermFactory(content=f'a - {n}', language=Language.PORTUGUESE_BRAZIL)
        for n in range(5)
    ]

    response = client.get(term_index_route('A', Language.PORTUGUESE_BRAZIL))

    assert response.status_code == 200
    assert [term for term in terms] == [Term(**res) for res in response.json()['items']]


@pytest.mark.parametrize('char', [1, 'AC', '#'])
def test_term_index_not_a_char(client, char):
    TermFactory.create_batch(size=5, language=Language.PORTUGUESE_BRAZIL)

    response = client.get(term_index_route(char, Language.PORTUGUESE_BRAZIL))

    assert response.status_code == 422
