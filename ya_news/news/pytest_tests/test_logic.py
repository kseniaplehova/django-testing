from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = "Текст комментария"
NEW_COMMENT_TEXT = "Обновлённый текст"
COMMENT_FORM_DATA = {"text": COMMENT_TEXT}
NEW_COMMENT_FORM_DATA = {"text": NEW_COMMENT_TEXT}


def test_anonymous_user_cant_create_comment(client, detail_url, login_url):
    Comment.objects.all().delete()
    response = client.post(detail_url, data=COMMENT_FORM_DATA)
    expected_url = f"{login_url}?next={detail_url}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, detail_url, news, author):
    Comment.objects.all().delete()
    response = author_client.post(detail_url, data=COMMENT_FORM_DATA)
    expected_url = detail_url + "#comments"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_FORM_DATA["text"]
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize("bad_word", BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    Comment.objects.all().delete()
    bad_data = {"text": f"Это {bad_word} текст"}
    response = author_client.post(detail_url, data=bad_data)
    assert response.status_code == HTTPStatus.OK
    assert "form" in response.context
    form = response.context["form"]
    assert "text" in form.errors
    assert WARNING in form.errors["text"][0]
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, edit_url, comment):
    response = author_client.post(edit_url, data=NEW_COMMENT_FORM_DATA)
    detail_url = reverse("news:detail", args=(comment.news.id,))
    expected_url = f"{detail_url}#comments"
    assertRedirects(response, expected_url)
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == NEW_COMMENT_FORM_DATA["text"]
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author


def test_author_can_delete_comment(author_client, delete_url, comment):
    response = author_client.delete(delete_url)
    detail_url = reverse("news:detail", args=(comment.news.id,))
    expected_url = f"{detail_url}#comments"
    assertRedirects(response, expected_url)
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_user_cant_edit_foreign_comment(reader_client, edit_url, comment):
    original_text = comment.text
    response = reader_client.post(edit_url, data=NEW_COMMENT_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    fresh_comment = Comment.objects.get(pk=comment.pk)
    assert fresh_comment.text == original_text
    assert fresh_comment.news == comment.news
    assert fresh_comment.author == comment.author


def test_user_cant_delete_foreign_comment(reader_client, delete_url, comment):
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
