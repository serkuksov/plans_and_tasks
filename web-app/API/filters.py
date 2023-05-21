from django_filters import rest_framework as filters

from accounts.models import UserDeteil


class UserDeteilFilter(filters.FilterSet):
    """Фильтр для отображения списка пользователей"""
    class Meta:
        model = UserDeteil
        fields = (
            'division',
        )
