import pytest
from django.conf import settings
from django.urls import reverse


def test_news_count(db, client, many_news):
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(db, client, many_news):
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(db, client, many_comments):
    url = reverse("news:detail", args=(many_comments[0].news.id,))
    response = client.get(url)
    news_obj = response.context["news"]
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    "client_fixture, has_form",
    [
        (pytest.lazy_fixture("client"), False),
        (pytest.lazy_fixture("author_client"), True),
    ],
)
def test_form_availability(client_fixture, has_form, news):
    url = reverse("news:detail", args=(news.id,))
    response = client_fixture.get(url)
    assert ("form" in response.context) == has_form
