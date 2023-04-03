from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def test_public_urls(self):
        """Проверяем доступность публичных страниц."""
        public_urls = (
            '/auth/signup/',
            '/auth/login/',
            '/auth/logout/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
            '/auth/reset/<uidb64>/<token>/',
        )
        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url(self):
        """Страницы изменения пароля и подтверждения перенаправят анонимного
        пользователя на страницу логина и доступны для пользователя.
        """
        self.user_client = Client()
        self.user_client.force_login(self.user)
        user_urls = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        for url in user_urls:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                response_user = self.user_client.get(url)
                self.assertEqual(response_user.status_code, HTTPStatus.OK)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                redirect_url = (reverse(settings.LOGIN_URL) + '?next=' + url)
                self.assertRedirects(
                    response, redirect_url
                )
