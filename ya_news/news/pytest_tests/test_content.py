from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, home_url, many_news):
    response = client.get(home_url)
    assert "object_list" in response.context
    object_list = response.context["object_list"]
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, many_news):
    response = client.get(home_url)
    assert "object_list" in response.context
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url_for_many_comments, many_comments):
    response = client.get(detail_url_for_many_comments)
    assert "news" in response.context
    news_obj = response.context["news"]
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_form_availability_for_anonymous(client, detail_url):
    response = client.get(detail_url)
    assert "form" not in response.context


def test_form_availability_for_author(author_client, detail_url):
    response = author_client.get(detail_url)
    assert "form" in response.context
    form = response.context["form"]
    assert isinstance(form, CommentForm)
