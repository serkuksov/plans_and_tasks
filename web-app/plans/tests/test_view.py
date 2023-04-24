from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model

from .. import models
from accounts.models import UserDeteil, Division


class ViewBaseTestCase(TestCase):
    """Базовый класс для наполнения БД"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='user', password='123456')
        self.division_1 = Division.objects.create(name='division_1')
        self.division_2 = Division.objects.create(name='division_2')
        UserDeteil.objects.create(
            user=self.user,
            second_name='second_name',
            phone_number=3399,
            division=self.division_1,
        )
        self.plan_1 = models.Plan.objects.create(
            name='plan_name_1',
            description='plan_description_1',
            completion_date=datetime(day=1, month=1, year=2023),
            user_creator=self.user.userdeteil,
            user_updater=self.user.userdeteil,
        )
        self.plan_2 = models.Plan.objects.create(
            name='plan_name_2',
            description='plan_description_2',
            completion_date=datetime(day=24, month=4, year=2025),
            user_creator=self.user.userdeteil,
            user_updater=self.user.userdeteil,
        )
        self.perfomer_1 = models.Perfomer.objects.create(division=self.division_1, performer_user=self.user.userdeteil)
        self.perfomer_2 = models.Perfomer.objects.create(division=self.division_2)
        self.perfomer_3 = models.Perfomer.objects.create(division=self.division_1)
        self.taskgroup = models.TaskGroup.objects.create(name='taskgroup')
        self.pattern_plan = models.PatternPlan.objects.create(
            name='name_pattern_plan',
            description='description_pattern_plan',
        )
        self.pattern_task_1 = models.PatternTask.objects.create(
            pattern_plan=self.pattern_plan,
            task_group=self.taskgroup,
            name='name_pattern_task_1',
            divisin_perfomer=self.division_1,
        )
        self.pattern_task_2 = models.PatternTask.objects.create(
            pattern_plan=self.pattern_plan,
            task_group=self.taskgroup,
            name='name_pattern_task_2',
            divisin_perfomer=self.division_2,
        )
        self.task_1 = models.Task.objects.create(
            pattern_task=self.pattern_task_1,
            plan=self.plan_1,
            name='task_1_name',
            completion_date=datetime.now() + timedelta(days=1),
            perfomer=self.perfomer_1,
            user_creator=self.user.userdeteil,
            user_updater=self.user.userdeteil,
            is_active=True,
        )
        self.task_2 = models.Task.objects.create(
            pattern_task=self.pattern_task_2,
            plan=self.plan_1,
            name='task_2_name',
            completion_date=datetime(day=1, month=3, year=2023),
            perfomer=self.perfomer_2,
            user_creator=self.user.userdeteil,
            user_updater=self.user.userdeteil,
            is_active=False,
        )
        self.task_3 = models.Task.objects.create(
            pattern_task=self.pattern_task_1,
            plan=self.plan_2,
            name='task_3_name',
            completion_date=datetime(day=1, month=2, year=2023),
            perfomer=self.perfomer_3,
            user_creator=self.user.userdeteil,
            user_updater=self.user.userdeteil,
            is_active=True,
        )


class PlanListViewTestCase(ViewBaseTestCase):
    """Тестирование отображения списка планов"""
    def test_plan_list_view(self):
        with self.assertNumQueries(1):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 2)
        plan_1 = object_list[0]
        plan_2 = object_list[1]

        self.assertEqual(plan_1.name, 'plan_name_1')
        self.assertEqual(plan_1.progress, 50)

        self.assertEqual(plan_2.name, 'plan_name_2')
        self.assertEqual(plan_2.progress, 0)

        self.assertTemplateUsed(response, 'plans/plan_list.html')


class PlanListViewTestCase(ViewBaseTestCase):
    """Тестирование отображения списка задач"""
    def test_task_list_view(self):
        with self.assertNumQueries(2):
            response = self.client.get('/task_list/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 3)

        self.assertEqual(object_list[0].name, 'task_3_name')
        self.assertIsNotNone(object_list[0].overdue)

        self.assertEqual(object_list[1].name, 'task_1_name')
        self.assertIsNone(object_list[1].overdue)

        self.assertEqual(object_list[2].name, 'task_2_name')
        self.assertIsNotNone(object_list[2].overdue)

        self.assertTemplateUsed(response, 'plans/task_list.html')

    def test_filters_task_list_view(self):
        with self.assertNumQueries(4):
            response = self.client.get('/task_list/?division=1')
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 2)

        self.assertEqual(object_list[0].name, 'task_3_name')
        self.assertEqual(object_list[1].name, 'task_1_name')

        with self.assertNumQueries(4):
            response = self.client.get('/task_list/?division=2')
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 1)
        
        self.assertEqual(object_list[0].name, 'task_2_name')

        with self.assertNumQueries(5):
            response = self.client.get('/task_list/?division=1&performer_user=1')
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 1)

        self.assertEqual(object_list[0].name, 'task_1_name')

        with self.assertNumQueries(2):
            response = self.client.get('/task_list/?is_overdue=1')
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 1)

        self.assertEqual(object_list[0].name, 'task_3_name')

        with self.assertNumQueries(2):
            response = self.client.get('/task_list/?is_active=1')
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 2)

        self.assertEqual(object_list[0].name, 'task_3_name')
        self.assertEqual(object_list[1].name, 'task_1_name')


class PlanAndTasksCreateViewTestCase(ViewBaseTestCase):
    """Тестирование создания нового плана и задач"""
    def test_get_create_view(self):
        response = self.client.get('/plan_create/')
        self.assertEqual(response.status_code, 302)

        self.client.login(username='user', password='123456')
        with self.assertNumQueries(4):
            response = self.client.get('/plan_create/')

        self.assertTemplateUsed(response, 'plans/plan_form_create.html')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pattern_plans']), 1)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertEqual(form.initial, {'user_creator': 1, 'user_updater': 1})
