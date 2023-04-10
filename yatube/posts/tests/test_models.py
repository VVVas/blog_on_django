from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте модели',
            slug='test-slug-model',
            description='Тестовое описание при тесте модели группы',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Парономазия откровенна. Графомания отталкивает дольник.',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Художественная гармония возможна.'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_posts_model_str(self):
        """Проверяем __str__ моделей."""
        models_ideal_strs = {
            PostModelTest.post: PostModelTest.post.text[:15],
            PostModelTest.group: PostModelTest.group.title,
            PostModelTest.comment: PostModelTest.comment.text[:15],
        }
        for model, ideal_str in models_ideal_strs.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), ideal_str)

    def test_posts_model_verbose_name(self):
        """Проверяем verbose_name моделей."""
        models_verbose_names = {
            PostModelTest.post: 'Публикация',
            PostModelTest.group: 'Сообщество',
            PostModelTest.comment: 'Комментарий',
            PostModelTest.follow: 'Подписка',
        }
        for model, verbose_name in models_verbose_names.items():
            with self.subTest(model=model):
                self.assertEqual(model._meta.verbose_name, verbose_name)

    def test_post_field_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Сообщество',
            'image': 'Изображение',
        }
        self._check_field_attr(field_verboses, post, 'verbose_name')

    def test_group_field_verbose_name(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Уникальный путь',
            'description': 'Описание',
        }
        self._check_field_attr(field_verboses, group, 'verbose_name')

    def test_comment_field_verbose_name(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Публикация',
            'author': 'Автор',
            'text': 'Текст',
            'created': 'Дата',
        }
        self._check_field_attr(field_verboses, comment, 'verbose_name')

    def test_follow_field_verbose_name(self):
        """verbose_name в полях модели Follow совпадает с ожидаемым."""
        follow = PostModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        self._check_field_attr(field_verboses, follow, 'verbose_name')

    def test_post_field_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст публикации',
            'group': 'Сообщество для публикации',
        }
        self._check_field_attr(field_help_texts, post, 'help_text')

    def test_follow_user_author_pair_unique(self):
        """Пары подписчик и автор будут уникальны в модели Follow"""
        with self.assertRaises(IntegrityError):
            Follow.objects.create(
                user=self.user,
                author=self.author,
            )

    def _check_field_attr(self, field_expected, model, attr):
        for field, expected_value in field_expected.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(
                        model._meta.get_field(field), attr), expected_value)
