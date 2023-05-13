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
        self.user_2 = get_user_model().objects.create_user(username='user_2', password='123456')
        self.division_1 = Division.objects.create(name='division_1')
        self.division_2 = Division.objects.create(name='division_2')
        UserDeteil.objects.create(
            user=self.user,
            second_name='second_name',
            phone_number=3399,
            division=self.division_1,
        )
        UserDeteil.objects.create(
            user=self.user_2,
            second_name='second_name',
            phone_number=3398,
            division=self.division_2,
            is_manager=True,
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
            years_ofset='+1',
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


class TaskListViewTestCase(ViewBaseTestCase):
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

    def test_post_create_view(self):
        data = {
            'user_creator': '',
            'user_updater': '',
            'pattern_plan': '',
            'completion_date': '',
        }
        response = self.client.post('/plan_create/', data=data)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='user', password='123456')
        with self.assertNumQueries(4):
            response = self.client.post('/plan_create/', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'user_creator', ['Обязательное поле.'])
        self.assertFormError(response, 'form', 'user_updater', ['Обязательное поле.'])
        self.assertFormError(response, 'form', 'pattern_plan', ['Обязательное поле.'])
        self.assertFormError(response, 'form', 'completion_date', ['Обязательное поле.'])

        data = {
            'user_creator': 1,
            'user_updater': 1,
            'pattern_plan': 1,
            'completion_date': '2023-01-01',
        }
        with self.assertNumQueries(16):
            response = self.client.post('/plan_create/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/plan_update/3/')
        plan = models.Plan.objects.filter(id=3).first()
        self.assertEqual(plan.completion_date, datetime(2023, 1, 1).date())

        tasks = models.Task.objects.filter(plan=plan).all()
        self.assertEqual(len(tasks), 2)

        self.assertEqual(tasks[0].pattern_task, models.PatternTask.objects.filter(id=1).first())
        self.assertEqual(tasks[0].plan, plan)
        self.assertEqual(tasks[0].name, 'name_pattern_task_1')
        self.assertEqual(tasks[0].completion_date, datetime(2022, 12, 30).date())
        self.assertEqual(tasks[0].perfomer, models.Perfomer.objects.filter(id=4).first())
        self.assertEqual(tasks[0].user_creator, self.user.userdeteil)

        self.assertEqual(tasks[1].pattern_task, models.PatternTask.objects.filter(id=2).first())
        self.assertEqual(tasks[1].plan, plan)
        self.assertEqual(tasks[1].name, 'name_pattern_task_2')
        self.assertEqual(tasks[1].completion_date, datetime(2023, 12, 29).date())
        self.assertEqual(tasks[1].perfomer, models.Perfomer.objects.filter(id=5).first())
        self.assertEqual(tasks[1].user_creator, self.user.userdeteil)


class PlanAndTasksDetailViewTestCase(ViewBaseTestCase):
    """Тестирование просмотра плана и задач"""
    def test_get_plan_and_tasks_detail_view(self):
        with self.assertNumQueries(2):
            response = self.client.get('/plan_detail/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plans/plan_detail.html')

        plan = models.Plan.objects.filter(id=1).first()
        self.assertEqual(response.context['object'], plan)
        self.assertEqual(response.context['object'].progress, 50)

        self.assertIn('task_list', response.context)
        tasks = models.Task.objects.filter(plan=1).all()
        self.assertQuerysetEqual(response.context['task_list'], tasks)
        self.assertEqual(response.context['task_list'][0].name, 'task_1_name')
        self.assertIsNone(response.context['task_list'][0].overdue)
        self.assertIsNotNone(response.context['task_list'][1].overdue)

        self.assertIn('is_delete_permission', response.context)
        self.assertIsNone(response.context['is_delete_permission'])

        self.client.login(username='user', password='123456')
        with self.assertNumQueries(5):
            response = self.client.get('/plan_detail/1/')
        self.assertIsNotNone(response.context['is_delete_permission'])


class PlanAndTasksDeleteViewTestCase(ViewBaseTestCase):
    """Тестирование удаления плана и задач"""
    def test_get_plan_and_tasks_delete_view(self):
        response = self.client.get('/plan_delete/1/')
        self.assertEqual(response.status_code, 405)

    def test_post_plan_and_tasks_delete_view(self):
        response = self.client.post('/plan_delete/1/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='user', password='123456')
        with self.assertNumQueries(13):
            response = self.client.post('/plan_delete/1/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        self.assertFalse(models.Plan.objects.filter(id=1).exists())
        self.assertFalse(models.Task.objects.filter(id=1).exists())
        self.assertFalse(models.Task.objects.filter(id=2).exists())
        self.assertFalse(models.Perfomer.objects.filter(id=1).exists())
        self.assertFalse(models.Perfomer.objects.filter(id=2).exists())

        self.assertTrue(models.Plan.objects.filter(id=2).exists())
        self.assertTrue(models.Task.objects.filter(id=3).exists())


class PlanAndTasksUpdateViewTestCase(ViewBaseTestCase):
    """Тестирование редактирования плана и задач"""
    def test_get_plan_and_tasks_update_view(self):
        response = self.client.get('/plan_update/1/')
        self.assertEqual(response.status_code, 302)

        self.client.login(username='user', password='123456')
        with self.assertNumQueries(9):
            response = self.client.get('/plan_update/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plans/plan_form_update.html')

        self.assertIn('form', response.context)
        form = response.context['form']
        initial = {
            'completion_date': datetime(2023, 1, 1).date(),
            'description': 'plan_description_1',
            'name': 'plan_name_1',
            'user_updater': 1,
            }
        self.assertEqual(form.initial, initial)

        self.assertIn('formset', response.context)
        self.assertEqual(len(response.context['formset']), 2)
        self.assertEqual(response.context['formset'][0].instance, self.task_1)
        self.assertEqual(response.context['formset'][1].instance, self.task_2)

    def test_post_plan_and_tasks_update_view(self):
        response = self.client.post('/plan_update/1/')
        self.assertEqual(response.status_code, 302)

        self.client.login(username='user_2', password='123456')
        with self.assertNumQueries(8):
            response = self.client.post('/plan_update/1/')
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'new_name',
            'description': 'new_description',
            'user_updater': 2,
            'completion_date': '2023-02-01',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': 1,
            'form-0-name': 'task_new',
            'form-1-id': 2,
            'form-1-name': 'test',
            'form-1-DELETE': 'on',
        }
        with self.assertNumQueries(20):
            response = self.client.post('/plan_update/1/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/plan_detail/1/')

        plan = models.Plan.objects.filter(id=1).first()
        self.assertEqual(plan.name, 'new_name')
        self.assertEqual(plan.description, 'new_description')
        self.assertEqual(plan.user_updater, self.user_2.userdeteil)
        self.assertEqual(plan.completion_date, datetime(2023, 2, 1).date())

        tasks = models.Task.objects.filter(plan=plan).all()
        self.assertEqual(len(tasks), 1)

        self.assertEqual(tasks[0].name, 'task_new')
        self.assertEqual(tasks[0].completion_date, datetime(2023, 2, 1).date())
        self.assertEqual(tasks[0].user_updater, self.user_2.userdeteil)

        self.assertFalse(models.Task.objects.filter(id=2).exists())
        self.assertFalse(models.Perfomer.objects.filter(id=2).exists())

        data = {
            'name': 'new_name_2',
            'description': 'new_description',
            'user_updater': 2,
            'completion_date': '2023-02-01',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': 1,
            'form-0-name': 'task_new',
        }
        with self.assertNumQueries(12):
            self.client.post('/plan_update/1/', data=data)
        tasks = models.Task.objects.filter(plan=plan).all()
        self.assertEqual(len(tasks), 1)

        self.assertEqual(tasks[0].name, 'task_new')
        self.assertEqual(tasks[0].completion_date, datetime(2023, 2, 1).date())


class TaskDetailViewTestCase(ViewBaseTestCase):
    """Тестирование детального отоброжения задач"""
    def test_get_context_data(self):
        with self.assertNumQueries(1):
            response = self.client.get('/task_detail/1/')
        self.assertEqual(response.status_code, 200)

        self.assertIn('form', response.context)
        self.assertIn('is_performer_user', response.context)
        self.assertIn('is_assign_perfomer', response.context)
        self.assertIn('is_possibility_execute', response.context)

        form = response.context['form']
        self.assertEqual(form.instance, self.perfomer_1)

        self.assertFalse(response.context['is_performer_user'])
        self.assertIsNone(response.context['is_assign_perfomer'])
        self.assertIsNone(response.context['is_possibility_execute'])

        self.client.login(username='user', password='123456')
        with self.assertNumQueries(5):
            response = self.client.get('/task_detail/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plans/task_detail.html')

        self.assertFalse(response.context['is_performer_user'])
        self.assertFalse(response.context['is_assign_perfomer'])
        self.assertTrue(response.context['is_possibility_execute'])

        self.perfomer_1.performer_user = None
        self.perfomer_1.save()
        self.task_1.is_active = False
        self.task_1.save()
        response = self.client.get('/task_detail/1/')
        self.assertTrue(response.context['is_performer_user'])
        self.assertFalse(response.context['is_possibility_execute'])

        self.client.login(username='user_2', password='123456')
        response = self.client.get('/task_detail/1/')
        self.assertFalse(response.context['is_possibility_execute'])

        response = self.client.get('/task_detail/2/')
        self.assertTrue(response.context['is_performer_user'])
        self.assertTrue(response.context['is_assign_perfomer'])
        self.assertTrue(response.context['is_possibility_execute'])

    def test_post(self):
        response = self.client.post('/task_detail/1/')
        self.assertEqual(response.status_code, 302)

        self.client.login(username='user', password='123456')
        with self.assertNumQueries(6):
            response = self.client.post('/task_detail/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Task.objects.filter(id=1).first().is_active, False)
        self.client.post('/task_detail/1/')
        self.assertEqual(models.Task.objects.filter(id=1).first().is_active, True)

        self.client.login(username='user_2', password='123456')
        response = self.client.post('/task_detail/1/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Task.objects.filter(id=1).first().is_active, True)
