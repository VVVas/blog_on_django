from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutTests(TestCase):
    def test_about_url_name_template(self):
        """Проверка доступности url, name и используемого шаблона в About."""
        templates_urls_names = {
            'about/author.html': (
                '/about/author/',
                'about:author',
            ),
            'about/tech.html': (
                '/about/tech/',
                'about:tech',
            ),
        }
        for template, params in templates_urls_names.items():
            url, name = params
            with self.subTest(template=template):
                response_url = self.client.get(url)
                self.assertEqual(response_url.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_url, template)
                response_name = self.client.get(reverse(name))
                self.assertEqual(response_name.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_name, template)
