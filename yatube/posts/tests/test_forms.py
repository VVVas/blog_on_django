from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.tests.constants import (
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
)

User = get_user_model()


class PostsCreateEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа при создании публикации',
            slug='test-slug-create-post',
            description='Тестовое описание при при создании публикации',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Строфоид отражает генезис свободного стиха.',
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create_form(self):
        """Валидная форма создает публикацию."""
        # Подсчитаем количество публикаций
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Цезура абсурдно осознаёт экзистенциальный дискурс.',
        }
        response = self.author_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                PROFILE_URL_NAME, kwargs={'username': self.author.username}
            )
        )
        # Проверяем, увеличилось ли число публикаций
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что публикаций создалась
        self.assertTrue(
            Post.objects.filter(
                text='Цезура абсурдно осознаёт экзистенциальный дискурс.',
            ).exists()
        )

    def test_post_edit_form(self):
        """Валидная форма редактирует публикацию."""
        # Подсчитаем количество публикаций
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Диахрония диссонирует скрытый смысл.',
            'group': self.group.id
        }
        response = self.author_client.post(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id}
            )
        )
        # Проверяем, не увеличилось ли число публикаций
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что публикация изменилась
        self.assertTrue(
            Post.objects.filter(
                text='Диахрония диссонирует скрытый смысл.',
            ).filter(
                group=self.group.id,
            ).exists()
        )
