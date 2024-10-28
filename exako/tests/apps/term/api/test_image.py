import pytest

from exako.apps.term.models import TermImage
from exako.main import app
from exako.tests.factories.term import TermFactory, TermImageFactory

create_term_image_router = app.url_path_for('create_term_image')


def get_term_image_router(term_id):
    return app.url_path_for('get_term_image', term_id=term_id)


def test_create_term_image(client, generate_payload):
    payload = generate_payload(TermImageFactory)
    payload.update(term_id=TermFactory().id)

    response = client.post(
        create_term_image_router,
        json=payload,
    )

    assert response.status_code == 201
    payload['id'] = response.json()['id']
    assert TermImage(**response.json()) == TermImage(**payload)


def test_create_term_image_term_not_found(client, generate_payload):
    payload = generate_payload(TermImageFactory)
    payload.update(term_id=1245)

    response = client.post(
        create_term_image_router,
        json=payload,
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'url',
    [
        '',
        'not_a_url',
        'http://',
        'http:///path.svg',
        'https://domain',
        'file:///path/image.svg',
        'http://example.com/test.png',
    ],
)
def test_create_term_image_invalid_url_format(client, generate_payload, url):
    payload = generate_payload(TermImageFactory, image_url=url)
    payload.update(term_id=TermFactory().id)

    response = client.post(
        create_term_image_router,
        json=payload,
    )

    assert response.status_code == 422


def test_get_term_image(client):
    term_image = TermImageFactory()

    response = client.get(get_term_image_router(term_image.term.id))

    assert response.status_code == 200
    assert TermImage(**response.json()) == term_image


def test_get_term_image_not_found(client):
    response = client.get(get_term_image_router(14580))

    assert response.status_code == 404
