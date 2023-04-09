from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import *


admin.site.unregister([get_user_model()])


class UserDeteilInline(admin.StackedInline):
    model = UserDeteil
    can_delete = False
    verbose_name_plural = 'Дополнительные данные'


@admin.register(get_user_model())
class CastomUserAdmin(UserAdmin):
    inlines = (UserDeteilInline,)   


@admin.register(UserDeteil)
class UserDeteilAdmin(admin.ModelAdmin):
    list_display = (
        'get_name',
        'division',
        'is_manager',
    )


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    pass
