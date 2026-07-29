from http import HTTPStatus

from .common import CommonTestCase


class TestRoutes(CommonTestCase):
    def test_pages_availability(self):
        urls = (
            (self.home_url, self.client, HTTPStatus.OK),
            (self.login_url, self.client, HTTPStatus.OK),
            (self.signup_url, self.client, HTTPStatus.OK),
            (self.logout_url, self.client, HTTPStatus.OK, "post"),
            (self.list_url, self.author_client, HTTPStatus.OK),
            (self.success_url, self.author_client, HTTPStatus.OK),
            (self.add_url, self.author_client, HTTPStatus.OK),
            (self.detail_url, self.author_client, HTTPStatus.OK),
            (self.edit_url, self.author_client, HTTPStatus.OK),
            (self.delete_url, self.author_client, HTTPStatus.OK),
            (self.detail_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.edit_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.delete_url, self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for item in urls:
            if len(item) == 4:
                url, client, expected_status, method = item
            else:
                url, client, expected_status = item
                method = "get"
            with self.subTest(url=url):
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                expected_redirect = f"{self.login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
