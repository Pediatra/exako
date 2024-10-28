import pytest
from sqlmodel import select

from exako.apps.term.constants import Language, Level
from exako.apps.term.models import TermExample, TermExampleLink, TermExampleTranslation
from exako.apps.term.repository import TermExampleLinkRepository
from exako.core.url import set_url_params
from exako.main import app
from exako.tests.factories.term import (
    TermDefinitionFactory,
    TermExampleFactory,
    TermExampleTranslationFactory,
    TermFactory,
    TermLexicalFactory,
)

create_term_example_route = app.url_path_for('create_example')
create_term_example_translation_route = app.url_path_for('create_example_translation')


def list_term_example_route(
    term_id=None,
    term_definition_id=None,
    term_lexical_id=None,
    level=None,
):
    url = app.url_path_for('list_examples')
    return set_url_params(
        url,
        term_id=term_id,
        term_definition_id=term_definition_id,
        term_lexical_id=term_lexical_id,
        level=level,
    )


def get_term_example_translation_route(
    term_example_id,
    language,
    term_id=None,
    term_definition_id=None,
    term_lexical_id=None,
):
    url = app.url_path_for(
        'get_example_translation',
        term_example_id=term_example_id,
        language=language,
    )
    return set_url_params(
        url,
        term_id=term_id,
        term_definition_id=term_definition_id,
        term_lexical_id=term_lexical_id,
    )


@pytest.mark.parametrize(
    'link_factory, link_name',
    [
        (TermFactory, 'term_id'),
        (TermDefinitionFactory, 'term_definition_id'),
        (TermLexicalFactory, 'term_lexical_id'),
    ],
)
def test_create_term_example(
    session,
    client,
    generate_payload,
    link_factory,
    link_name,
):
    payload = generate_payload(TermExampleFactory)
    link_model = link_factory()
    payload.update(
        **{link_name: link_model.id},
        highlight=[[1, 3], [5, 6]],
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 201
    payload['id'] = response.json()['id']
    assert TermExample(**response.json()) == TermExample(**payload)
    assert session.exec(
        select(TermExampleLink).filter_by(
            term_example_id=response.json()['id'],
            **{link_name: link_model.id},
        )
    ).first()


@pytest.mark.parametrize(
    'link_name',
    [
        'term_id',
        'term_definition_id',
        'term_lexical_id',
    ],
)
def test_create_term_example_link_not_found(client, generate_payload, link_name):
    payload = generate_payload(TermExampleFactory)
    payload.update(
        **{link_name: 519027},
        highlight=[[1, 3], [5, 6]],
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'link_factory, link_name',
    [
        (TermFactory, 'term_id'),
        (TermDefinitionFactory, 'term_definition_id'),
        (TermLexicalFactory, 'term_lexical_id'),
    ],
)
def test_create_term_example_with_conflict_link(
    session,
    client,
    generate_payload,
    link_factory,
    link_name,
):
    link_model = link_factory()
    payload = generate_payload(TermExampleFactory)
    example = TermExampleFactory(**payload)
    payload.update(
        **{link_name: link_model.id},
        highlight=[[1, 3], [5, 6]],
    )
    repository = TermExampleLinkRepository(session)
    repository.create(
        **{link_name: link_model.id},
        term_example_id=example.id,
        highlight=[[1, 3], [5, 6]],
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 409
    assert 'example already linked with this model.' in response.json()['detail']


def test_create_term_example_term_lexical_content(client, generate_payload):
    payload = generate_payload(TermExampleFactory)
    term_lexical = TermLexicalFactory(content=None, term_content=TermFactory())
    payload.update(
        term_lexical_id=term_lexical.id,
        highlight=[[1, 3], [5, 6]],
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'lexical with term_content cannot link with this model.'
    )


@pytest.mark.parametrize(
    'link_factory, link_name, language_ref',
    [
        (TermFactory, 'term_id', 'language'),
        (TermDefinitionFactory, 'term_definition_id', 'term__language'),
        (TermLexicalFactory, 'term_lexical_id', 'term__language'),
    ],
)
def test_create_term_example_invalid_language_reference(
    client,
    generate_payload,
    link_factory,
    link_name,
    language_ref,
):
    payload = generate_payload(TermExampleFactory, language=Language.CHINESE_SIMPLIFIED)
    link_model = link_factory(**{language_ref: Language.ARABIC})
    payload.update(
        **{link_name: link_model.id},
        highlight=[[1, 3], [5, 6]],
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'term example language has to be the same as the link model.'
    )


def test_create_term_example_model_link_not_set(client, generate_payload):
    payload = generate_payload(TermExampleFactory)
    payload.update(highlight=[[1, 3], [5, 6]])

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert 'at least one object to link' in response.json()['detail'][0]['msg']


@pytest.mark.parametrize(
    'link_attr',
    [
        {
            'term_definition_id': 123,
            'term_id': 5125,
        },
        {
            'term_definition_id': 123,
            'term_lexical_id': 400,
        },
    ],
)
def test_create_term_example_multiple_models(client, generate_payload, link_attr):
    payload = generate_payload(TermExampleFactory)
    payload.update(link_attr, highlight=[[1, 3], [5, 6]])

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert 'you can reference only one object.' in response.json()['detail'][0]['msg']


def test_create_term_example_invalid_num_highlight(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermExampleFactory)
    payload.update(
        term_id=term.id,
        highlight=[[1, 4, 5], [6, 8]],
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'highlight must consist of pairs of numbers'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'highlight', [[[1, 4], [4, 6]], [[10, 14], [13, 16]], [[0, 3], [0, 9]]]
)
def test_create_term_example_invalid_highlight_interval(
    client, generate_payload, highlight
):
    term = TermFactory()
    payload = generate_payload(TermExampleFactory)
    payload.update(
        term_id=term.id,
        highlight=highlight,
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert 'highlight interval must not overlap' in response.json()['detail'][0]['msg']


@pytest.mark.parametrize('highlight', [[[399, 5]], [[5, 699]]])
def test_create_term_example_invalid_highlight_len(client, generate_payload, highlight):
    term = TermFactory()
    payload = generate_payload(TermExampleFactory)
    payload.update(
        term_id=term.id,
        highlight=highlight,
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'highlight cannot be greater than the length of the example.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize('highlight', [[[-1, 5]], [[-5, -1]]])
def test_create_term_example_invalid_highlight_values_lower_than_0(
    client, generate_payload, highlight
):
    term = TermFactory()
    payload = generate_payload(TermExampleFactory)
    payload.update(
        term_id=term.id,
        highlight=highlight,
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'both highlight values must be greater than or equal to 0.'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_example_invalid_highlight_value1_greater_than_value2(
    client, generate_payload
):
    term = TermFactory()
    payload = generate_payload(TermExampleFactory)
    payload.update(
        term_id=term.id,
        highlight=[[7, 1]],
    )

    response = client.post(
        create_term_example_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        'highlight beginning value cannot be greater than the ending value'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_example_translation(client, generate_payload):
    term_example = TermExampleFactory()
    payload = generate_payload(TermExampleTranslationFactory, term_example=term_example)
    payload.update(highlight=[[1, 3], [5, 7]])

    response = client.post(
        create_term_example_translation_route,
        json=payload,
    )

    assert response.status_code == 201
    assert TermExampleTranslation(**response.json()) == TermExampleTranslation(
        **payload
    )


def test_create_term_example_translation_example_not_found(client, generate_payload):
    payload = generate_payload(TermExampleTranslationFactory)
    payload.update(
        term_example_id=123,
        highlight=[[1, 3], [5, 7]],
    )

    response = client.post(
        create_term_example_translation_route,
        json=payload,
    )

    assert response.status_code == 404


def test_create_term_example_translation_conflict(client, generate_payload):
    example = TermExampleFactory()
    payload = generate_payload(TermExampleTranslationFactory)
    TermExampleTranslationFactory(**payload, term_example=example)
    payload.update(
        term_example_id=example.id,
        highlight=[[1, 3], [5, 7]],
    )

    response = client.post(
        create_term_example_translation_route,
        json=payload,
    )

    assert response.status_code == 409
    assert 'translation already exists for this example.' in response.json()['detail']


def test_create_term_example_translation_same_language(client, generate_payload):
    term_example = TermExampleFactory(language=Language.CHINESE_SIMPLIFIED)
    payload = generate_payload(
        TermExampleTranslationFactory,
        term_example=term_example,
        language=Language.CHINESE_SIMPLIFIED,
    )
    payload.update(highlight=[[1, 3], [5, 7]])

    response = client.post(
        create_term_example_translation_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'translation language reference cannot be same as language.'
    )


@pytest.mark.parametrize(
    'link_factory, link_name',
    [
        (TermFactory, 'term_id'),
        (TermDefinitionFactory, 'term_definition_id'),
        (TermLexicalFactory, 'term_lexical_id'),
    ],
)
def test_list_term_example(session, client, link_factory, link_name):
    link_model = link_factory()
    examples = TermExampleFactory.create_batch(size=5)
    TermExampleFactory.create_batch(size=5)
    repository = TermExampleLinkRepository(session)
    links = [
        repository.create(
            **{link_name: link_model.id},
            term_example_id=example.id,
            highlight=[[1, 5]],
        )
        for example in examples
    ]

    response = client.get(list_term_example_route(**{link_name: link_model.id}))

    assert response.status_code == 200
    assert len(response.json()['items']) == 5
    response_result = [TermExample(**example) for example in response.json()['items']]
    expected_response = [
        TermExample(
            id=example.id,
            language=example.language,
            content=example.content,
            level=example.level,
            highlight=link.highlight,
            additional_content=example.additional_content,
        )
        for example, link in zip(examples, links)
    ]
    assert all([example in response_result for example in expected_response])


def test_list_term_example_empty(client):
    term = TermFactory()
    TermExampleFactory.create_batch(size=10)

    response = client.get(list_term_example_route(term_id=term.id))

    assert response.status_code == 200


@pytest.mark.parametrize(
    'link_factory, link_name',
    [
        (TermFactory, 'term_id'),
        (TermDefinitionFactory, 'term_definition_id'),
        (TermLexicalFactory, 'term_lexical_id'),
    ],
)
def test_list_term_example_filter_level(session, client, link_factory, link_name):
    link_model = link_factory()
    examples1 = TermExampleFactory.create_batch(size=5, level=Level.ADVANCED)
    examples2 = TermExampleFactory.create_batch(size=5, level=Level.BEGINNER)
    TermExampleFactory.create_batch(size=5)
    repository = TermExampleLinkRepository(session)
    links = [
        repository.create(
            **{link_name: link_model.id},
            term_example_id=example.id,
            highlight=[[1, 5]],
        )
        for example in [*examples1, *examples2]
    ]

    response = client.get(
        list_term_example_route(
            **{link_name: link_model.id},
            level=Level.ADVANCED,
        )
    )

    assert response.status_code == 200
    assert len(response.json()['items']) == 5
    response_result = [TermExample(**example) for example in response.json()['items']]
    expected_response = [
        TermExample(
            id=example.id,
            language=example.language,
            content=example.content,
            level=example.level,
            highlight=link.highlight,
            additional_content=example.additional_content,
        )
        for example, link in zip(examples1, links)
    ]
    assert all([example in response_result for example in expected_response])


def test_get_term_example_translation(client):
    example = TermExampleFactory()
    translation = TermExampleTranslationFactory(term_example=example)

    response = client.get(
        get_term_example_translation_route(
            term_example_id=example.id,
            language=translation.language,
        )
    )

    assert response.status_code == 200
    assert TermExampleTranslation(**response.json()) == translation


def test_get_term_example_translation_not_found(client):
    response = client.get(
        get_term_example_translation_route(
            term_example_id=123,
            language=Language.CHINESE_SIMPLIFIED,
        )
    )

    assert response.status_code == 404
