from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа при тесте модели',
            slug='test-slug-model',
            description='Тестовое описание при тесте модели группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Парономазия откровенна. Графомания отталкивает дольник.',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Художественная гармония возможна.'
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

    def test_post_verbose_name(self):
        """verbose_name модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        self.assertEqual(post._meta.verbose_name, 'Публикация')

    def test_group_verbose_name(self):
        """verbose_name модели Group совпадает с ожидаемым."""
        group = PostModelTest.group
        self.assertEqual(group._meta.verbose_name, 'Сообщество')

    def test_comment_verbose_name(self):
        """verbose_name модели Comment совпадает с ожидаемым."""
        comment = PostModelTest.comment
        self.assertEqual(comment._meta.verbose_name, 'Комментарий')

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

    def test_post_field_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст публикации',
            'group': 'Сообщество для публикации',
        }
        self._check_field_attr(field_help_texts, post, 'help_text')

    def _check_field_attr(self, field_expected, model, attr):
        for field, expected_value in field_expected.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(
                        model._meta.get_field(field), attr), expected_value)
