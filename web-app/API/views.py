from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from API.filters import UserDeteilFilter
from API.serializers import UserDeteilSerializer
from accounts.models import UserDeteil


class UserDeteilListAPIView(generics.ListAPIView):
    """Отображение списка пользователей с фильтрацией по подразделению"""
    queryset = (
        UserDeteil.objects.
        select_related('user', 'division').
        annotate(
            full_name=Concat('user__last_name', Value(' '), 'user__first_name', Value(' '), 'second_name')
        ).
        order_by('full_name')
    )
    serializer_class = UserDeteilSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserDeteilFilter
