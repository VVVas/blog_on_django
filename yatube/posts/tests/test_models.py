from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

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

    def test_post_model_str(self):
        """Проверяем __str__ модели Post."""
        post = PostModelTest.post
        ideal_post_str = post.text[:15]
        self.assertEqual(str(post), ideal_post_str)

    def test_group_model_str(self):
        """Проверяем __str__ модели Group."""
        group = PostModelTest.group
        ideal_group_str = group.title
        self.assertEqual(str(group), ideal_group_str)

    def test_post_verbose_name(self):
        """verbose_name модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        self.assertEqual(post._meta.verbose_name, 'Публикация')

    def test_group_verbose_name(self):
        """verbose_name модели Group совпадает с ожидаемым."""
        group = PostModelTest.group
        self.assertEqual(group._meta.verbose_name, 'Сообщество')

    def test_post_field_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        self._check_verbose_name(field_verboses, post)

    def test_group_field_verbose_name(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Уникальный путь',
            'description': 'Описание',
        }
        self._check_verbose_name(field_verboses, group)

    def test_post_field_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст публикации',
            'group': 'Сообщество для публикации',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def _check_verbose_name(self, field_expected, model):
        for field, expected_value in field_expected.items():
            with self.subTest(field=field):
                self.assertEqual(
                    model._meta.get_field(field).verbose_name, expected_value)




# это для проверки функции и сама функция — перепиши для её использования.

    def test_post_field_help_text2(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст публикации',
            'group': 'Сообщество для публикации',
        }
        self._check(field_help_texts, post, 'help_text')

    def _check(self, field_expected, model, attr):
        for field, expected_value in field_expected.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(
                        model._meta.get_field(field), attr), expected_value)
