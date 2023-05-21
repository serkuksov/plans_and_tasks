from django.urls import path

from API import views


urlpatterns = [
    path('user/', views.UserDeteilListAPIView.as_view(), name='user_deteil_list'),
]
