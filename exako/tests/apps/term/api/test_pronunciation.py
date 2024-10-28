import pytest

from exako.apps.term.models import TermPronunciation
from exako.core.url import set_url_params
from exako.main import app
from exako.tests.factories.term import (
    TermExampleFactory,
    TermFactory,
    TermLexicalFactory,
    TermPronunciationFactory,
)

create_pronunciation_route = app.url_path_for('create_pronunciation')


def get_pronunciation_route(
    term_id=None,
    term_example_id=None,
    term_lexical_id=None,
):
    url = app.url_path_for('get_pronunciation')
    return set_url_params(
        url,
        term_id=term_id,
        term_example_id=term_example_id,
        term_lexical_id=term_lexical_id,
    )


@pytest.mark.parametrize(
    'factory, link_name',
    [
        (TermFactory, 'term'),
        (TermExampleFactory, 'term_example'),
        (TermLexicalFactory, 'term_lexical'),
    ],
)
def test_create_term_pronunciation(client, generate_payload, factory, link_name):
    instance = factory()
    payload = generate_payload(TermPronunciationFactory, **{link_name: instance})

    response = client.post(
        create_pronunciation_route,
        json=payload,
    )

    assert response.status_code == 201
    payload['id'] = response.json()['id']
    assert TermPronunciation(**response.json()) == TermPronunciation(**payload)


@pytest.mark.parametrize(
    'model',
    [
        {'term_id': 12515},
        {'term_example_id': 1241245},
        {'term_lexical_id': 15661},
    ],
)
def test_create_term_pronunciation_model_link_not_found(
    client, generate_payload, model
):
    payload = generate_payload(TermPronunciationFactory)
    payload.update(**model)

    response = client.post(
        create_pronunciation_route,
        json=payload,
    )

    assert response.status_code == 404


def test_create_term_pronunciation_already_exists(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermPronunciationFactory, term=term)
    TermPronunciationFactory(**payload, term=term)

    response = client.post(
        create_pronunciation_route,
        json=payload,
    )

    assert response.status_code == 409


def test_create_term_pronunciation_model_link_attribute_not_set(
    client, generate_payload
):
    payload = generate_payload(TermPronunciationFactory, term_id=None)

    response = client.post(
        create_pronunciation_route,
        json=payload,
    )

    assert response.status_code == 422
    assert 'at least one object to link' in response.json()['detail'][0]['msg']


@pytest.mark.parametrize(
    'link_attr',
    [
        {
            'term_example_id': 123,
            'term_id': 616,
        },
        {
            'term_example_id': 123,
            'term_lexical_id': 400,
        },
    ],
)
def test_create_term_pronunciation_multiple_models(client, generate_payload, link_attr):
    payload = generate_payload(TermPronunciationFactory)
    payload.update(link_attr)

    response = client.post(
        create_pronunciation_route,
        json=payload,
    )

    assert response.status_code == 422
    assert 'you can reference only one object.' in response.json()['detail'][0]['msg']


def test_create_term_pronunciation_lexical_term_content(client, generate_payload):
    term_content = TermFactory()
    term_lexical = TermLexicalFactory(term_content=term_content, content=None)
    payload = generate_payload(TermPronunciationFactory, term_lexical=term_lexical)

    response = client.post(
        create_pronunciation_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'lexical with term_content cannot link with this model.'
        in response.json()['detail']
    )


@pytest.mark.parametrize(
    'factory, link_name',
    [
        (TermFactory, 'term'),
        (TermExampleFactory, 'term_example'),
        (TermLexicalFactory, 'term_lexical'),
    ],
)
def test_get_term_pronunciation(client, factory, link_name):
    instance = factory()
    pronunciation = TermPronunciationFactory(**{link_name: instance})
    TermPronunciationFactory.create_batch(5)

    response = client.get(get_pronunciation_route(**{f'{link_name}_id': instance.id}))

    assert response.status_code == 200
    assert TermPronunciation(**response.json()) == pronunciation


@pytest.mark.parametrize(
    'model',
    [
        {'term_id': 12515},
        {'term_example_id': 1241245},
        {'term_lexical_id': 15661},
    ],
)
def test_get_term_pronunciation_not_found(client, model):
    TermPronunciationFactory.create_batch(5)

    response = client.get(get_pronunciation_route(**model))

    assert response.status_code == 404


def test_get_term_pronunciation_model_not_set(client):
    response = client.get(get_pronunciation_route())

    assert response.status_code == 422
    assert (
        'you need to provide at least one object to link.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'link_attr',
    [
        {
            'term_example_id': 123,
            'term_id': 616,
        },
        {
            'term_example_id': 123,
            'term_lexical_id': 400,
        },
    ],
)
def test_get_term_pronunciation_model_multiple_invalid(client, link_attr):
    response = client.get(get_pronunciation_route(**link_attr))

    assert response.status_code == 422
    assert 'you can reference only one object.' in response.json()['detail'][0]['msg']
