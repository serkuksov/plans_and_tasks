def has_delete_permission(request, obj):
    """Проверка создателя объекта"""
    if request.user.is_authenticated:
        return obj.user_creator == request.user.userdeteil or request.user.is_superuser


def can_assign_perfomer(request, obj):
    """Проверка права на назначение исполнителя"""
    if request.user.is_authenticated:
        return obj.division == request.user.userdeteil.division and request.user.userdeteil.is_manager or request.user.is_superuser


def can_possibility_execute(request, obj):
    """Проверка права на подтверждение выполнения"""
    if request.user.is_authenticated:
        return can_assign_perfomer(request, obj) or  obj.performer_user == request.user.userdeteil or request.user.is_superuser