from django.urls import path


from . import views

urlpatterns = [
    path('', views.PlanListView.as_view(), name='plan_list'),
    path('task_list/', views.TaskListView.as_view(), name='task_list'),
    path('plan_create/', views.PlanAndTasksCreateView.as_view(), name='plan_create'),
    path('plan_detail/<int:pk>/', views.PlanAndTasksDetailView.as_view(), name='plan_detail'),
    path('plan_update/<int:pk>/', views.PlanAndTasksUpdateView.as_view(), name='plan_update'),
    path('plan_delete/<int:pk>/', views.PlanAndTasksDeleteView.as_view(), name='plan_delete'),
    path('task_detail/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('create_word_doc_for_plan/<int:pk>/', views.create_word_doc_for_plan_view, name='create_word_doc_for_plan'),
    path('perfomer_update/<int:pk>/', views.PerfomerUpdateView.as_view(), name='perfomer_update'),
]
