from django.test import TestCase
from django.urls import reverse, resolve

from .. import views


class UrlsTestCase(TestCase):
    """Тесты URL"""

    def test_urls(self):
        self.assertEqual(resolve(reverse('plans:plan_list')).func.view_class, views.PlanListView)
        self.assertEqual(resolve(reverse('plans:task_list')).func.view_class, views.TaskListView)
        self.assertEqual(resolve(reverse('plans:plan_create')).func.view_class, views.PlanAndTasksCreateView)
        self.assertEqual(resolve(reverse('plans:plan_detail', args=(1,))).func.view_class, views.PlanAndTasksDetailView)
        self.assertEqual(resolve(reverse('plans:plan_update', args=(1,))).func.view_class, views.PlanAndTasksUpdateView)
        self.assertEqual(resolve(reverse('plans:plan_delete', args=(1,))).func.view_class, views.PlanAndTasksDeleteView)
        self.assertEqual(resolve(reverse('plans:task_detail', args=(1,))).func.view_class, views.TaskDetailView)
        self.assertEqual(resolve(reverse('plans:create_word_doc_for_plan', args=(1,))).func,
                         views.create_word_doc_for_plan_view)
        self.assertEqual(resolve(reverse('plans:perfomer_update', args=(1,))).func.view_class, views.PerfomerUpdateView)
