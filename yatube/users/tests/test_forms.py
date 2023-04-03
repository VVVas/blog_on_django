from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.tests.constants import SIGNUP_URL_NAME
from posts.tests.constants import INDEX_URL_NAME

User = get_user_model()


class UsersCreateFormTests(TestCase):

    def test_user_create_form(self):
        """Валидная форма создает пользователя."""
        # Подсчитаем количество пользователей
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'nick',
            'email': 'mail@example.com',
            'password1': 'wP2tWyf5rxZhW2F',
            'password2': 'wP2tWyf5rxZhW2F',
        }
        response = self.client.post(
            reverse(SIGNUP_URL_NAME),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(INDEX_URL_NAME))
        # Проверяем, увеличилось ли число пользователей
        self.assertEqual(User.objects.count(), users_count + 1)
        # Проверяем, что пользователь создался
        self.assertTrue(
            User.objects.filter(
                username='nick',
            ).exists()
        )
