from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Page
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


class PostsNameTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте name',
            slug='test-slug-name',
            description='Тестовое описание при тесте name',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Стихотворение отталкивает сюжетный пастиш.',
            group=cls.group,
        )

    def test_names_template(self):
        """posts:name использует соответствующий шаблон."""
        self.author_client = Client()
        self.author_client.force_login(self.author)
        names_kwargs_templates = {
            INDEX_URL_NAME: (
                {},
                INDEX_TEMPLATE,
            ),
            POST_CREATE_URL_NAME: (
                {},
                POST_CREATE_TEMPLATE,
            ),
            GROUP_LIST_URL_NAME: (
                {'slug': self.group.slug},
                GROUP_LIST_TEMPLATE,
            ),
            PROFILE_URL_NAME: (
                {'username': self.author.username},
                PROFILE_TEMPLATE,
            ),
            POST_DETAIL_URL_NAME: (
                {'post_id': self.post.id},
                POST_DETAIL_TEMPLATE,
            ),
            POST_EDIT_URL_NAME: (
                {'post_id': self.post.id},
                POST_CREATE_TEMPLATE,
            ),
        }
        for name, params in names_kwargs_templates.items():
            kwargs, template = params
            with self.subTest(name=name):
                response = self.author_client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)


class PostsContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте Контекста',
            slug='test-slug-context',
            description='Тестовое описание при тесте Контекста',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа при тесте Контекста',
            slug='another-test-slug-context',
            description='Другое тестовое описание при тесте Контекста',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Подтекст недоступно диссонирует палимпсест.',
            group=cls.group,
        )
        cls.another_post = Post.objects.create(
            author=cls.author,
            text='Орнаментальный сказ интуитивно понятен.',
            group=cls.another_group,
        )

    def test_posts_context(self):
        """Тест основного контекста."""
        names_kwargs_querysets = {
            INDEX_URL_NAME: (
                {},
                Post.objects.all(),
            ),
            GROUP_LIST_URL_NAME: (
                {'slug': self.group.slug},
                self.group.posts.all(),
            ),
            PROFILE_URL_NAME: (
                {'username': self.author.username},
                self.author.posts.all(),
            ),
        }
        for name, params in names_kwargs_querysets.items():
            kwargs, queryset = params
            with self.subTest(name=name):
                response = self.client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)
                self.assertQuerysetEqual(
                    page_obj, queryset, lambda x: x
                )

    def test_group_list_context(self):
        """Шаблон posts:group_list группы сформирован с контекстом, который
        отличается от контекста другой группы и с правильным
        дополнительным контекстом
        """
        response_group = self.client.get(
            reverse(GROUP_LIST_URL_NAME,
                    kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response_group.status_code, HTTPStatus.OK)
        response_another = self.client.get(
            reverse(GROUP_LIST_URL_NAME,
                    kwargs={'slug': self.another_group.slug})
        )
        self.assertEqual(response_another.status_code, HTTPStatus.OK)
        group_object = response_group.context['group']
        self.assertIsNotNone(group_object)
        self.assertIsInstance(group_object, Group)
        self.assertEqual(group_object, self.group)
        obj_group = response_group.context['page_obj']
        self.assertIsNotNone(obj_group)
        self.assertIsInstance(obj_group, Page)
        obj_another = response_another.context['page_obj']
        self.assertIsNotNone(obj_another)
        self.assertIsInstance(obj_another, Page)
        self.assertNotEqual(obj_group, obj_another)

    def test_profile_context(self):
        """Шаблон posts:profile группы сформирован с правильным
        дополнительным контекстом
        """
        response = self.client.get(
            reverse(PROFILE_URL_NAME,
                    kwargs={'username': self.author.username})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        author_object = response.context['author']
        self.assertIsNotNone(author_object)
        self.assertIsInstance(author_object, User)
        self.assertEqual(author_object, self.author)
        post_count_object = response.context['post_count']
        self.assertIsNotNone(post_count_object)
        self.assertEqual(post_count_object, self.author.posts.count())

    def test_post_detail_context(self):
        """Шаблон posts:post_detail сформирован с правильным контекстом."""
        response = self.client.get(
            reverse(POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id})
        )
        post_object = response.context['post']
        self.assertIsNotNone(post_object)
        self.assertIsInstance(post_object, Post)
        self.assertEqual(post_object, self.post)
        post_count_object = response.context['post_count']
        self.assertIsNotNone(post_count_object)
        self.assertEqual(post_count_object, self.author.posts.count())


class PostsCreateEditContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте Контекста',
            slug='test-slug-context',
            description='Тестовое описание при тесте Контекста',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Не-текст интуитивно понятен.',
            group=cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create_context(self):
        """Шаблон posts:post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(POST_CREATE_URL_NAME))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        self._check_form_fields(form_fields, response)

    def test_post_edit_context(self):
        """Шаблон posts:post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id})
        )
        is_edit_object = response.context['is_edit']
        self.assertIsNotNone(is_edit_object)
        self.assertTrue(is_edit_object)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        self._check_form_fields(form_fields, response)

    def _check_form_fields(self, form_fields, response):
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsNotNone(form_field)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте Пагинатора',
            slug='test-slug-paginator',
            description='Тестовое описание при тесте Пагинатора',
        )
        Post.objects.bulk_create(
            [
                Post(
                    author=cls.author,
                    text=f'Механизм сочленений диссонирует размер {i}.',
                    group=cls.group,
                ) for i in range(settings.POSTS_PER_PAGE
                                 + settings.POSTS_PER_PAGE // 2)
            ]
        )

    def test_paginator(self):
        """Тест пагинатора."""
        names_kwargs_querysets = {
            INDEX_URL_NAME: (
                {},
                Post.objects.all()[:settings.POSTS_PER_PAGE],
            ),
            GROUP_LIST_URL_NAME: (
                {'slug': self.group.slug},
                self.group.posts.all()[:settings.POSTS_PER_PAGE],
            ),
            PROFILE_URL_NAME: (
                {'username': self.author.username},
                self.author.posts.all()[:settings.POSTS_PER_PAGE],
            ),
        }
        for name, params in names_kwargs_querysets.items():
            kwargs, queryset = params
            with self.subTest(name=name):
                response = self.client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)
                self.assertQuerysetEqual(
                    page_obj, queryset, lambda x: x
                )
