from exako.apps.term.constants import Language, TermLexicalType
from exako.apps.term.models import TermLexical
from exako.core.url import set_url_params
from exako.main import app
from exako.tests.factories.term import TermFactory, TermLexicalFactory

create_term_lexical_route = app.url_path_for('create_lexical')


def list_term_lexical_route(term_id=None, type=None):
    url = app.url_path_for('list_lexicals')
    return set_url_params(
        url,
        term_id=term_id,
        type=type,
    )


def test_create_term_lexical(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermLexicalFactory, term=term)

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 201
    payload['id'] = response.json()['id']
    assert TermLexical(**response.json()) == TermLexical(**payload)


def test_create_term_lexical_with_term_content(client, session, generate_payload):
    term = TermFactory()
    term_content = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        content=None,
        term_content=term_content,
    )

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 201
    term_lexical = session.get(TermLexical, {'id': response.json()['id']})
    assert term_lexical.term_content_id == term_content.id


def test_create_term_lexical_term_does_not_exists(client, generate_payload):
    payload = generate_payload(TermLexicalFactory)
    payload.update(term_id=1256)

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 404


def test_create_term_content_term_does_not_exists(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermLexicalFactory, term=term)
    payload.update(content=None, term_content_id=414)

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 404


def test_create_term_lexical_conflict(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermLexicalFactory, term=term)
    TermLexicalFactory(**payload, term=term)

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 409


def test_create_term_lexical_conflict_term_content(client, generate_payload):
    term = TermFactory()
    term_content = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        content=None,
        term_content=term_content,
    )
    TermLexicalFactory(**payload, term=term, term_content=term_content)

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 409


def test_create_term_lexical_content_same_as_term(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        content=None,
        term_content=term,
    )

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'term_content cannot be the same as term lexical reference.'
        in response.json()['detail']
    )


def test_create_term_lexical_term_ref_invalid_language_reference(
    client, generate_payload
):
    term = TermFactory(language=Language.JAPANESE)
    payload = generate_payload(
        TermLexicalFactory,
        term=TermFactory(language=Language.GERMAN),
        content=None,
        term_content=term,
    )

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'term_content language have to be the same as term lexical reference.'
        == response.json()['detail']
    )


def test_create_term_lexical_without_content(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        term_content=None,
        content=None,
    )

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'you need to provied at least one content ref.'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_lexical_both_contents(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        term_content=TermFactory(),
    )

    response = client.post(
        create_term_lexical_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'you cannot reference two values at once (content, term_content_id).'
        in response.json()['detail'][0]['msg']
    )


def test_list_term_lexical(client):
    term = TermFactory()
    lexicals = TermLexicalFactory.create_batch(
        term=term,
        type=TermLexicalType.ANTONYM.value,
        size=5,
    )

    response = client.get(
        list_term_lexical_route(
            term_id=term.id,
            type=TermLexicalType.ANTONYM.value,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(
        [
            lexical in lexicals
            for lexical in [TermLexical(**lexical) for lexical in response.json()]
        ]
    )


def test_list_term_lexical_term_content(client):
    term = TermFactory()
    lexicals = [
        TermLexicalFactory(
            term=term,
            type=TermLexicalType.ANTONYM.value,
            content=None,
            term_content=TermFactory(),
        )
        for _ in range(5)
    ]

    response = client.get(
        list_term_lexical_route(
            term_id=term.id,
            type=TermLexicalType.ANTONYM.value,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(
        [
            lexical in lexicals
            for lexical in [TermLexical(**lexical) for lexical in response.json()]
        ]
    )


def test_list_term_lexical_empty(client):
    term = TermFactory()
    TermLexicalFactory.create_batch(
        term=term,
        type=TermLexicalType.INFLECTION,
        size=5,
    )

    response = client.get(
        list_term_lexical_route(
            term_id=term.id,
            type=TermLexicalType.ANTONYM.value,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 0
