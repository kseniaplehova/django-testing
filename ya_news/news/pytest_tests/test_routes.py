from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    "name, args",
    [
        ("news:home", None),
        ("news:detail", pytest.lazy_fixture("news_id")),
    ],
)
def test_pages_availability(db, client, name, args):
    url = reverse(name, args=args) if args else reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "name",
    [
        "users:login",
        "users:logout",
        "users:signup",
    ],
)
def test_auth_pages_availability(client, name):
    url = reverse(name)
    response = client.post(url) if name == "users:logout" else client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "name, args",
    [
        ("news:delete", pytest.lazy_fixture("comment_id")),
        ("news:edit", pytest.lazy_fixture("comment_id")),
    ],
)
def test_availability_for_comment_edit_and_delete(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "name, args",
    [
        ("news:delete", pytest.lazy_fixture("comment_id")),
        ("news:edit", pytest.lazy_fixture("comment_id")),
    ],
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse("users:login")
    url = reverse(name, args=args)
    redirect_url = f"{login_url}?next={url}"
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url


@pytest.mark.parametrize(
    "name, args",
    [
        (
            "news:delete",
            pytest.lazy_fixture("comment_id")
        ),
        (
            "news:edit",
            pytest.lazy_fixture("comment_id")
        ),
    ],
)
def test_reader_cannot_edit_delete(reader_client, name, args):
    url = reverse(name, args=args)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
