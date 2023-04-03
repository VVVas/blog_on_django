from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.tests.constants import (
    INDEX_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
    INDEX_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    POST_CREATE_TEMPLATE,
)

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте URL',
            slug='test-slug-url',
            description='Тестовое описание при тесте URL',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Стихотворение отталкивает сюжетный пастиш.',
        )

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_urls_templates(self):
        """URL-адрес доступен и использует соответствующий шаблон."""
        urls_templates = {
            '/': INDEX_TEMPLATE,
            f'/group/{self.group.slug}/': GROUP_LIST_TEMPLATE,
            f'/profile/{self.author.username}/': PROFILE_TEMPLATE,
            f'/posts/{self.post.id}/': POST_DETAIL_TEMPLATE,
            f'/posts/{self.post.id}/edit/': POST_CREATE_TEMPLATE,
            '/create/': POST_CREATE_TEMPLATE,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_public_urls(self):
        """Проверяем доступность публичных страниц."""
        public_names = {
            INDEX_URL_NAME: {},
            GROUP_LIST_URL_NAME: {'slug': self.group.slug},
            PROFILE_URL_NAME: {'username': self.author.username},
            POST_DETAIL_URL_NAME: {'post_id': self.post.id},
        }
        for name, kwargs in public_names.items():
            with self.subTest(name=name):
                response = self.client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_not_found(self):
        """Несуществующая страница возвращает 404."""
        response = self.user_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_edit_url_redirect_anonymous(self):
        """Страницы создания и редактирования публикации перенаправят
        анонимного пользователя на страницу логина.
        """
        user_urls = {
            POST_CREATE_URL_NAME: {},
            POST_EDIT_URL_NAME: {'post_id': self.post.id},
        }
        for name, kwargs in user_urls.items():
            with self.subTest(name=name):
                response = self.client.get(
                    reverse(name, kwargs=kwargs), follow=True
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)
                redirect_url = (
                    reverse(settings.LOGIN_URL) + '?next='
                    + reverse(name, kwargs=kwargs)
                )
                self.assertRedirects(response, redirect_url)

    def test_create_url_user(self):
        """Страница создания публикации доступна пользователю."""
        response = self.user_client.get(reverse(POST_CREATE_URL_NAME))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_user(self):
        """Страница редактирования публикации перенаправит
        пользователя на страницу публикации.
        """
        response = self.user_client.get(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id}),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id})
        )

    def test_edit_url_author(self):
        """Страница редактирования публикации доступна автору."""
        response = self.author_client.get(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
