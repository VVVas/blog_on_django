import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post
from posts.tests.constants import (
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    ADD_COMMENT_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
)

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateEditFormTests(TestCase):
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
        cls.not_img_txt = b'not_img'
        cls.not_img_uploaded = SimpleUploadedFile(
            name='not_img.txt',
            content=cls.not_img_txt,
            content_type='not_img_txt'
        )
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create_form(self):
        """Валидная форма создает публикацию"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Цезура абсурдно осознаёт экзистенциальный дискурс.',
        }
        response = self.author_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                PROFILE_URL_NAME, kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Цезура абсурдно осознаёт экзистенциальный дискурс.',
            ).exists()
        )

    def test_post_create_form_not_img(self):
        """Нельзя загрузить некорректный файл"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Цикл полидисперсен.',
            'image': self.not_img_uploaded,
        }
        response = self.author_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        error_msg = ('Загрузите правильное изображение. Файл, который вы '
                     'загрузили, поврежден или не является изображением.')
        self.assertFormError(
            response,
            'form',
            'image',
            error_msg,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text='Цикл полидисперсен.',
            ).exists()
        )

    def test_post_edit_form(self):
        """Валидная форма редактирует публикацию"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Диахрония диссонирует скрытый смысл.',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.author_client.post(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Диахрония диссонирует скрытый смысл.',
                group=self.group.id,
                image=settings.POSTS_UPLOAD_TO + self.uploaded.name,
            ).exists()
        )

    def test_post_detail_comment_form(self):
        """Валидная форма создает комментарий"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Наряду с нейтральной лексикой рифма возможна.',
        }
        response = self.author_client.post(
            reverse(ADD_COMMENT_URL_NAME, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Наряду с нейтральной лексикой рифма возможна.',
            ).exists()
        )
