from exako.apps.term.constants import Language, Level, PartOfSpeech
from exako.apps.term.models import TermDefinition, TermDefinitionTranslation
from exako.core.url import set_url_params
from exako.main import app
from exako.tests.factories.term import (
    TermDefinitionFactory,
    TermDefinitionTranslationFactory,
    TermFactory,
    TermLexicalFactory,
)

create_term_definition_route = app.url_path_for('create_definition')
create_term_definition_translation_route = app.url_path_for(
    'create_definition_translation'
)


def list_term_definition_route(
    term_id=None,
    language=None,
    part_of_speech=None,
    level=None,
    term_lexical_id=None,
):
    url = app.url_path_for('list_definitions')
    return set_url_params(
        url,
        term_id=term_id,
        language=language,
        part_of_speech=part_of_speech,
        level=level,
        term_lexical_id=term_lexical_id,
    )


def get_term_definition_translation_route(term_definition_id, language):
    return app.url_path_for(
        'get_definition_translation',
        term_definition_id=term_definition_id,
        language=language,
    )


def list_term_meanings_route(term_id, translation_language):
    return app.url_path_for(
        'list_term_meanings',
        term_id=term_id,
        translation_language=translation_language,
    )


def test_create_term_definition(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermDefinitionFactory, term=term)

    response = client.post(
        create_term_definition_route,
        json=payload,
    )

    assert response.status_code == 201
    payload['id'] = response.json()['id']
    assert TermDefinition(**response.json()) == TermDefinition(**payload)


def test_create_term_definition_for_term_lexical(session, client, generate_payload):
    term = TermFactory()
    term_lexical = TermLexicalFactory(term=term)
    payload = generate_payload(
        TermDefinitionFactory,
        part_of_speech=PartOfSpeech.ADJECTIVE,
        term=term,
        term_lexical=term_lexical,
    )

    response = client.post(
        create_term_definition_route,
        json=payload,
    )

    assert response.status_code == 201
    definition = session.get(TermDefinition, {'id': response.json()['id']})
    assert definition.term_lexical.id == term_lexical.id


def test_create_term_definition_term_not_found(client, generate_payload):
    payload = generate_payload(TermDefinitionFactory)
    payload.update(term_id=1257)

    response = client.post(
        create_term_definition_route,
        json=payload,
    )

    assert response.status_code == 404


def test_create_term_definition_conflict(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermDefinitionFactory, term=term)
    TermDefinitionFactory(**payload)

    response = client.post(
        create_term_definition_route,
        json=payload,
    )

    assert response.status_code == 409
    assert response.json()['detail'] == 'definition already exists to this term.'


def test_create_term_definition_term_lexical_invalid_language_ref(
    client, generate_payload
):
    term = TermFactory(language=Language.ARABIC)
    term_lexical = TermLexicalFactory(term__language=Language.PORTUGUESE_BRAZIL)
    payload = generate_payload(
        TermDefinitionFactory,
        term=term,
        term_lexical=term_lexical,
    )

    response = client.post(
        create_term_definition_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'term_lexical language have to be the same as term reference.'
    )


def test_create_term_definition_translation(client, generate_payload):
    term_definition = TermDefinitionFactory()
    payload = generate_payload(
        TermDefinitionTranslationFactory,
        term_definition=term_definition,
    )

    response = client.post(
        create_term_definition_translation_route,
        json=payload,
    )

    assert response.status_code == 201
    assert TermDefinitionTranslation(**response.json()) == TermDefinitionTranslation(
        **payload
    )


def test_create_term_definition_translation_definition_does_not_exists(
    client, generate_payload
):
    payload = generate_payload(TermDefinitionTranslationFactory)
    payload.update(term_definition_id=51892)

    response = client.post(
        create_term_definition_translation_route,
        json=payload,
    )

    assert response.status_code == 404


def test_create_term_definition_translation_conflict(client, generate_payload):
    term_definition = TermDefinitionFactory()
    payload = generate_payload(
        TermDefinitionTranslationFactory,
        term_definition=term_definition,
    )
    TermDefinitionTranslationFactory(
        **payload,
        term_definition=term_definition,
    )

    response = client.post(
        create_term_definition_translation_route,
        json=payload,
    )

    assert response.status_code == 409
    assert (
        response.json()['detail']
        == 'translation language for this definition is already registered.'
    )


def test_create_term_definition_translation_same_language_reference(
    client, generate_payload
):
    term_definition = TermDefinitionFactory(term__language=Language.ARABIC)
    payload = generate_payload(
        TermDefinitionTranslationFactory,
        term_definition=term_definition,
        language=Language.ARABIC,
    )

    response = client.post(
        create_term_definition_translation_route,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'translation language reference cannot be same as language.'
    )


def test_list_term_definition(client):
    term = TermFactory()
    definitions = TermDefinitionFactory.create_batch(term=term, size=5)
    TermDefinitionFactory.create_batch(size=5)

    response = client.get(list_term_definition_route(term_id=term.id))

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(
        [
            definition in definitions
            for definition in [
                TermDefinition(**definition) for definition in response.json()
            ]
        ]
    )


def test_list_term_definition_empty(client):
    term = TermFactory()
    TermDefinitionFactory.create_batch(size=5)

    response = client.get(list_term_definition_route(term_id=term.id))

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_list_term_definition_filter_part_of_speech(client):
    term = TermFactory()
    definitions = TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        part_of_speech=PartOfSpeech.ADJECTIVE,
    )
    TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        part_of_speech=PartOfSpeech.VERB,
    )

    response = client.get(
        list_term_definition_route(
            term_id=term.id,
            part_of_speech=PartOfSpeech.ADJECTIVE.value,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(
        [
            definition in definitions
            for definition in [
                TermDefinition(**definition) for definition in response.json()
            ]
        ]
    )


def test_list_term_definition_filter_level(client):
    term = TermFactory()
    definitions = TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        level=Level.ADVANCED,
    )
    TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        level=Level.BEGINNER,
    )

    response = client.get(
        list_term_definition_route(
            term_id=term.id,
            level=Level.ADVANCED,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(
        [
            definition in definitions
            for definition in [
                TermDefinition(**definition) for definition in response.json()
            ]
        ]
    )


def test_list_term_definition_filter_term_lexical(client):
    term = TermFactory()
    lexical = TermLexicalFactory()
    definitions = TermDefinitionFactory.create_batch(
        term=term,
        term_lexical=lexical,
        size=5,
    )
    TermDefinitionFactory.create_batch(term=term, size=5)

    response = client.get(
        list_term_definition_route(
            term_id=term.id,
            term_lexical_id=lexical.id,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(
        [
            definition in definitions
            for definition in [
                TermDefinition(**definition) for definition in response.json()
            ]
        ]
    )


def test_get_term_definition_translation(client):
    translation = TermDefinitionTranslationFactory()

    response = client.get(
        get_term_definition_translation_route(
            term_definition_id=translation.term_definition.id,
            language=translation.language,
        )
    )

    assert response.status_code == 200
    assert TermDefinitionTranslation(**response.json()) == translation


def test_get_term_definition_translation_not_found(client):
    TermDefinitionTranslationFactory()

    response = client.get(
        get_term_definition_translation_route(
            term_definition_id=123,
            language=Language.PORTUGUESE_BRAZIL,
        )
    )

    assert response.status_code == 404


def test_list_meanings(client):
    term = TermFactory()
    translations = TermDefinitionTranslationFactory.create_batch(
        language=Language.ARABIC,
        term_definition__term=term,
        size=5,
    )
    meanings = [translation.meaning for translation in translations]

    response = client.get(
        list_term_meanings_route(
            term_id=term.id,
            translation_language=Language.ARABIC,
        )
    )

    assert response.status_code == 200
    assert response.json()['meanings'] == meanings


def test_list_meanings_empty(client):
    term = TermFactory()
    TermDefinitionTranslationFactory.create_batch(
        language=Language.ARABIC,
        term_definition__term=term,
        size=5,
    )

    response = client.get(
        list_term_meanings_route(
            term_id=term.id,
            translation_language=Language.RUSSIAN,
        )
    )

    assert response.status_code == 200
    assert response.json()['meanings'] == []
