from django.test import TestCase
from django.urls import reverse, resolve

from .. import views


class UrlsTestCase(TestCase):
    """Тесты URL"""

    def test_urls(self):
        self.assertEqual(resolve(reverse('API:user_deteil_list')).func.view_class, views.UserDeteilListAPIView)

    def test_path_urls(self):
        self.assertEqual(reverse('API:user_deteil_list'), '/api/v1/user/')

