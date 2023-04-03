from http import HTTPStatus

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.tests.constants import (
    SIGNUP_URL_NAME,
    LOGOUT_URL_NAME,
    PASSWORD_CHANGE_URL_NAME,
    PASSWORD_CHANGE_DONE_URL_NAME,
    PASSWORD_RESET_URL_NAME,
    PASSWORD_RESET_DONE_URL_NAME,
    PASSWORD_RESET_COMPLETE_URL_NAME,
    PASSWORD_RESET_CONFIRM_URL_NAME,
    SIGNUP_TEMPLATE,
    LOGIN_TEMPLATE,
    LOGOUT_TEMPLATE,
    PASSWORD_CHANGE_TEMPLATE,
    PASSWORD_CHANGE_DONE_TEMPLATE,
    PASSWORD_RESET_TEMPLATE,
    PASSWORD_RESET_DONE_TEMPLATE,
    PASSWORD_RESET_COMPLETE_TEMPLATE,
    PASSWORD_RESET_CONFIRM_TEMPLATE,
)

User = get_user_model()


class UsersNameTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def test_names_template(self):
        """users:name использует соответствующий шаблон."""
        self.user_client = Client()
        self.user_client.force_login(self.user)
        names_kwargs_templates = {
            SIGNUP_URL_NAME: (
                {},
                SIGNUP_TEMPLATE,
            ),
            settings.LOGIN_URL: (
                {},
                LOGIN_TEMPLATE,
            ),
            PASSWORD_CHANGE_URL_NAME: (
                {},
                PASSWORD_CHANGE_TEMPLATE,
            ),
            PASSWORD_CHANGE_DONE_URL_NAME: (
                {},
                PASSWORD_CHANGE_DONE_TEMPLATE,
            ),
            LOGOUT_URL_NAME: (
                {},
                LOGOUT_TEMPLATE,
            ),
            PASSWORD_RESET_URL_NAME: (
                {},
                PASSWORD_RESET_TEMPLATE,
            ),
            PASSWORD_RESET_DONE_URL_NAME: (
                {},
                PASSWORD_RESET_DONE_TEMPLATE,
            ),
            PASSWORD_RESET_COMPLETE_URL_NAME: (
                {},
                PASSWORD_RESET_COMPLETE_TEMPLATE,
            ),
            PASSWORD_RESET_CONFIRM_URL_NAME: (
                {'uidb64': 'uidb64', 'token': 'token'},
                PASSWORD_RESET_CONFIRM_TEMPLATE,
            ),
        }
        for name, params in names_kwargs_templates.items():
            kwargs, template = params
            with self.subTest(name=name):
                response = self.user_client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_user_create_context(self):
        """Шаблон users:signup сформирован с правильным контекстом."""
        response = self.client.get(reverse(SIGNUP_URL_NAME))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsNotNone(form_field)
                self.assertIsInstance(form_field, expected)
