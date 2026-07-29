from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

home = pytest.lazy_fixture("home_url")
detail = pytest.lazy_fixture("detail_url")
login = pytest.lazy_fixture("login_url")
signup = pytest.lazy_fixture("signup_url")
logout = pytest.lazy_fixture("logout_url")
edit = pytest.lazy_fixture("edit_url")
delete = pytest.lazy_fixture("delete_url")
client_anon = pytest.lazy_fixture("client")
client_author = pytest.lazy_fixture("author_client")
client_reader = pytest.lazy_fixture("reader_client")
edit_redirect = pytest.lazy_fixture("edit_redirect_url")
delete_redirect = pytest.lazy_fixture("delete_redirect_url")


@pytest.mark.parametrize(
    "url_fixture, client_fixture, expected_status, method",
    [
        (home, client_anon, HTTPStatus.OK, "get"),
        (detail, client_anon, HTTPStatus.OK, "get"),
        (login, client_anon, HTTPStatus.OK, "get"),
        (signup, client_anon, HTTPStatus.OK, "get"),
        (logout, client_anon, HTTPStatus.OK, "post"),
        (edit, client_author, HTTPStatus.OK, "get"),
        (delete, client_author, HTTPStatus.OK, "get"),
        (edit, client_reader, HTTPStatus.NOT_FOUND, "get"),
        (delete, client_reader, HTTPStatus.NOT_FOUND, "get"),
    ],
)
def test_pages_availability(
    url_fixture, client_fixture, expected_status, method
):
    response = getattr(client_fixture, method)(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "url_fixture, expected_redirect_fixture",
    [
        (edit, edit_redirect),
        (delete, delete_redirect),
    ],
)
def test_redirect_for_anonymous_client(
    client, url_fixture, expected_redirect_fixture
):
    response = client.get(url_fixture)
    assertRedirects(response, expected_redirect_fixture)
