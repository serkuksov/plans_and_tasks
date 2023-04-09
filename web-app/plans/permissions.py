def user_can_delete_task(request, obj):
    """Проверка прав на удаление бъекта"""
    if request.user.is_authenticated:
        return obj.user_creator == request.user.userdeteil or \
            request.user.is_superuser


def user_can_assign_performer(request, obj):
    """Проверка права на назначение исполнителя задачи"""
    if request.user.is_authenticated:
        return obj.division == request.user.userdeteil.division and \
            request.user.userdeteil.is_manager or request.user.is_superuser


def user_can_execute_task(request, obj):
    """Проверка права на подтверждение выполнения задачи исполнителем"""
    if request.user.is_authenticated:
        return user_can_assign_performer(request, obj) or \
            obj.performer_user == request.user.userdeteil or \
            request.user.is_superuser
