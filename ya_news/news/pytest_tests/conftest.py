from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create(username="Автор")


@pytest.fixture
def reader(db):
    return User.objects.create(username="Читатель")


@pytest.fixture
def news(db):
    return News.objects.create(title="Заголовок", text="Текст")


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text="Текст комментария")


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def many_news(db):
    today = datetime.today()
    news_list = [
        News(
            title=f"Новость {i}",
            text="Текст",
            date=today
            - timedelta(
                days=i)) for i in range(
            settings.NEWS_COUNT_ON_HOME_PAGE
            + 1)]
    return News.objects.bulk_create(news_list)


@pytest.fixture
def many_comments(news, author):
    from django.utils import timezone

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
