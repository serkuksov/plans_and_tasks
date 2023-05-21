import tempfile
from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from docx import Document

from accounts.models import UserDeteil, Division


class ViewBaseTestCase(TestCase):
    """Базовый класс для наполнения БД"""
    def setUp(self):
        self.user_1 = get_user_model().objects.create_user(username='user_1',
                                                           password='123456',
                                                           email='assad@mail.ru',
                                                           last_name='b')
        self.user_2 = get_user_model().objects.create_user(username='user_2',
                                                           password='123456',
                                                           last_name='a')
        self.division_1 = Division.objects.create(name='division_1')
        self.division_2 = Division.objects.create(name='division_2')
        UserDeteil.objects.create(
            user=self.user_1,
            second_name='second_name',
            phone_number=3399,
            division=self.division_1,
        )
        UserDeteil.objects.create(
            user=self.user_2,
            second_name='second_name_2',
            phone_number=3398,
            division=self.division_2,
            is_manager=True,
        )


class UserDeteilListAPIViewTestCase(ViewBaseTestCase):
    """Тестирование отображения списка пользователей"""
    def test_get(self):
        with self.assertNumQueries(1):
            response = self.client.get('/api/v1/user/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['user'], self.user_2.username)
        self.assertEqual(response.data[1]['user'], self.user_1.username)

    def test_filter(self):
        with self.assertNumQueries(2):
            response = self.client.get('/api/v1/user/?division=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user_2.username)
