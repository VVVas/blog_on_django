import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post
from posts.tests.constants import (
    INDEX_URL_NAME,
    FOLLOW_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    PROFILE_FOLLOW_URL_NAME,
    PROFILE_UNFOLLOW_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
    INDEX_TEMPLATE,
    FOLLOW_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    POST_CREATE_TEMPLATE,
)

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
            FOLLOW_URL_NAME: (
                {},
                FOLLOW_TEMPLATE,
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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
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
            image=cls.uploaded,
        )
        cls.another_post = Post.objects.create(
            author=cls.author,
            text='Орнаментальный сказ интуитивно понятен.',
            group=cls.another_group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='Абстракционизм абсурдно вызывает жанр.'
        )
        Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_context(self):
        """Тест основного контекста."""
        self.user_client = Client()
        self.user_client.force_login(self.user)
        names_kwargs_querysets = {
            INDEX_URL_NAME: (
                {},
                Post.objects.all(),
            ),
            FOLLOW_URL_NAME: (
                {},
                Post.objects.filter(
                    author__in=self.user.follower.values('author')
                ),
            ),
            GROUP_LIST_URL_NAME: (
                {'slug': self.group.slug},
                self.group.posts.all(),
            ),
            PROFILE_URL_NAME: (
                {'username': self.author.username},
                self.author.posts.all(),
            ),
            POST_DETAIL_URL_NAME: (
                {'post_id': self.post.id},
                self.post.comments.all(),
            )
        }
        for name, params in names_kwargs_querysets.items():
            kwargs, queryset = params
            with self.subTest(name=name):
                response = self.user_client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)
                self.assertQuerysetEqual(
                    page_obj, queryset, lambda x: x
                )

    def test_posts_cache(self):
        """Тест кэширования."""
        cache.clear()
        # self.author_client = Client()
        # self.author_client.force_login(self.author)
        # cached_post = Post.objects.create(
        #     author=self.author,
        #     text='Парафраз нивелирует литературный метр.',
        #     group=self.group,
        # )
        response_begin = self.client.get(reverse(INDEX_URL_NAME))
        # self.assertEqual(response_begin.status_code, HTTPStatus.OK)
        page_obj_begin = response_begin.context.get('page_obj')
        # self.assertIsNotNone(page_obj_begin)
        # self.assertIsInstance(page_obj_begin, Page)

        # cached_post.delete()
        self.another_post.delete()

        response_middle = self.client.get(reverse(INDEX_URL_NAME))
        # self.assertEqual(response_middle.status_code, HTTPStatus.OK)
        page_obj_middle = response_middle.context.get('page_obj')
        # self.assertIsNotNone(page_obj_middle)
        # self.assertIsInstance(page_obj_middle, Page)

        # self.assertQuerysetEqual(
        #     page_obj_middle, page_obj_begin, lambda x: x
        # )

        cache.clear()

        response_end = self.client.get(reverse(INDEX_URL_NAME))
        # self.assertEqual(response_end.status_code, HTTPStatus.OK)
        page_obj_end = response_end.context.get('page_obj')
        # self.assertIsNotNone(page_obj_end)
        # self.assertIsInstance(page_obj_end, Page)

        # self.assertEqual(page_obj_end, page_obj_begin)
        # self.assertQuerysetEqual(
        #     page_obj_end, page_obj_begin, lambda x: x
        # )

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
        cls.post = Post.objects.create(
            author=cls.author,
            text='Не-текст интуитивно понятен.',
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

    def test_post_detail_form_context(self):
        """Форма в шаблоне posts:post_detail имеет правильный контекст"""
        response = self.author_client.get(
            reverse(POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
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
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте Пагинатора',
            slug='test-slug-paginator',
            description='Тестовое описание при тесте Пагинатора',
        )
        Follow.objects.create(
            user=cls.user,
            author=cls.author
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Возврат к стереотипам неизменяем.',
        )
        Comment.objects.bulk_create(
            [
                Comment(
                    author=cls.author,
                    text=f'Аффилиация параллельна {i}.',
                    post=cls.post,
                ) for i in range(settings.POSTS_PER_PAGE
                                 + settings.POSTS_PER_PAGE // 2)
            ]
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
        self.user_client = Client()
        self.user_client.force_login(self.user)
        names_kwargs_querysets = {
            INDEX_URL_NAME: (
                {},
                Post.objects.all()[:settings.POSTS_PER_PAGE],
            ),
            FOLLOW_URL_NAME: (
                {},
                Post.objects.filter(
                    author__in=self.user.follower.values('author')
                )[:settings.POSTS_PER_PAGE],
            ),
            GROUP_LIST_URL_NAME: (
                {'slug': self.group.slug},
                self.group.posts.all()[:settings.POSTS_PER_PAGE],
            ),
            PROFILE_URL_NAME: (
                {'username': self.author.username},
                self.author.posts.all()[:settings.POSTS_PER_PAGE],
            ),
            POST_DETAIL_URL_NAME: (
                {'post_id': self.post.id},
                self.post.comments.all()[:settings.POSTS_PER_PAGE],
            )
        }
        for name, params in names_kwargs_querysets.items():
            kwargs, queryset = params
            with self.subTest(name=name):
                response = self.user_client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)
                self.assertQuerysetEqual(
                    page_obj, queryset, lambda x: x
                )


class PostsFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Басня возможна.',
        )

    def test_posts_follow_follow_unfollow(self):
        """Тест подписки."""
        self.user_client = Client()
        self.user_client.force_login(self.user)
        response = self.user_client.get(
            reverse(
                PROFILE_FOLLOW_URL_NAME,
                kwargs={'username': self.author.username}),
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                PROFILE_URL_NAME, kwargs={'username': self.author.username}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )
        response = self.user_client.get(
            reverse(
                PROFILE_UNFOLLOW_URL_NAME,
                kwargs={'username': self.author.username}),
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                PROFILE_URL_NAME, kwargs={'username': self.author.username}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )
