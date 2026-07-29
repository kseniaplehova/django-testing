from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author():
    return User.objects.create(username="Автор")


@pytest.fixture
def reader():
    return User.objects.create(username="Читатель")


@pytest.fixture
def news():
    return News.objects.create(title="Заголовок", text="Текст")


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text="Текст комментария"
    )


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def home_url():
    return reverse("news:home")


@pytest.fixture
def detail_url(news):
    return reverse("news:detail", args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse("news:edit", args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse("news:delete", args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse("users:login")


@pytest.fixture
def logout_url():
    return reverse("users:logout")


@pytest.fixture
def signup_url():
    return reverse("users:signup")


@pytest.fixture
def many_news():
    today = datetime.today()
    count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    News.objects.bulk_create(
        News(
            title=f"Новость {i}",
            text="Текст",
            date=today - timedelta(days=i)
        )
        for i in range(count)
    )


@pytest.fixture
def many_comments(news, author):
    now = timezone.now()
    comments = []
    for i in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"Текст {i}",
        )
        comment.created = now + timedelta(days=i)
        comment.save(update_fields=["created"])
        comments.append(comment)
    return comments


@pytest.fixture
def detail_url_for_many_comments(many_comments):
    return reverse("news:detail", args=(many_comments[0].news.id,))


@pytest.fixture
def edit_redirect_url(edit_url, login_url):
    return f"{login_url}?next={edit_url}"


@pytest.fixture
def delete_redirect_url(delete_url, login_url):
    return f"{login_url}?next={delete_url}"
