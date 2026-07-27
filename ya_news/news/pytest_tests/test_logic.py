from http import HTTPStatus

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = "Текст комментария"
NEW_COMMENT_TEXT = "Обновлённый текст"


def test_anonymous_user_cant_create_comment(client, news):
    url = reverse("news:detail", args=(news.id,))
    form_data = {"text": COMMENT_TEXT}
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news):
    url = reverse("news:detail", args=(news.id,))
    form_data = {"text": COMMENT_TEXT}
    response = author_client.post(url, data=form_data)
    comments_url = reverse("news:detail", args=(news.id,)) + "#comments"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT


def test_user_cant_use_bad_words(author_client, news):
    url = reverse("news:detail", args=(news.id,))
    bad_words_data = {"text": f"Текст, {BAD_WORDS[0]}, ещё текст"}
    response = author_client.post(url, data=bad_words_data)
    assert "form" in response.context
    assert response.context["form"].errors["text"] == [WARNING]
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment):
    url = reverse("news:edit", args=(comment.id,))
    form_data = {"text": NEW_COMMENT_TEXT}
    response = author_client.post(url, data=form_data)
    comments_url = reverse(
        "news:detail", args=(
            comment.news.id,)) + "#comments"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_author_can_delete_comment(author_client, comment):
    url = reverse("news:delete", args=(comment.id,))
    response = author_client.delete(url)
    comments_url = reverse(
        "news:detail", args=(
            comment.news.id,)) + "#comments"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url
    assert Comment.objects.count() == 0


def test_user_cant_edit_foreign_comment(reader_client, comment):
    url = reverse("news:edit", args=(comment.id,))
    form_data = {"text": NEW_COMMENT_TEXT}
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT


def test_user_cant_delete_foreign_comment(reader_client, comment):
    url = reverse("news:delete", args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
