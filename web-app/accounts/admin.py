from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from accounts.forms import UserDeteilChangeForm, UserDeteilCreationForm
from accounts.models import *

#admin.site.unregister([get_user_model(),])

"""
@admin.register(get_user_model())
class UserDeteilAdmin(UserAdmin):
    list_display = ("username", "get_name", "is_active")
    form = UserDeteilChangeForm
    add_form = UserDeteilCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Личные данные"), {"fields": ("first_name", "last_name", "second_name", "phone_number", "email", "division", "is_manager")}),
        (
            ("Разрешения"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (None, {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "first_name", "last_name", "second_name", "phone_number", "division", "is_manager"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        second_name = form.cleaned_data.get('second_name')
        phone_number = form.cleaned_data.get('phone_number')
        if UserDeteil.objects.filter(user=obj).exists():
            obj.userdeteil.second_name = second_name
            obj.userdeteil.phone_number = phone_number
            obj.userdeteil.save()
        else:
            UserDeteil.objects.create(user=obj, second_name=second_name, phone_number=phone_number)
        super().save_model(request, obj, form, change)

    @admin.display(description='ФИО')
    def get_name(self, obj):
        return f'{obj.last_name} {obj.first_name} {obj.userdeteil.second_name}'

"""

admin.site.unregister([get_user_model(),])

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
