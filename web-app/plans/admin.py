from django.contrib import admin

from . import models


@admin.register(models.Perfomer)
class AdminPerfomer(admin.ModelAdmin):
    list_display = (
        'get_task_and_plan',
        'division',
        'performer_user',
    )

    @admin.display(description='План/Задача')
    def get_task_and_plan(self, obj):
        return f'{obj.task_set.all()[0].plan} / {obj.task_set.all()[0]}'


class Tasklnline(admin.StackedInline):
    model = models.Task
    extra = 0


@admin.register(models.Plan)
class AdminPlan(admin.ModelAdmin):
    list_display = (
        'name',
        'completion_date',
    )
    inlines = [Tasklnline]


class PatternTasklnline(admin.StackedInline):
    model = models.PatternTask
    extra = 1


@admin.register(models.PatternPlan)
class AdminPatternPlan(admin.ModelAdmin):
    list_display = (
        'name',
    )
    inlines = [PatternTasklnline]


@admin.register(models.PatternTask)
class AdminPatternTask(admin.ModelAdmin):
    list_display = (
        'name',
        'pattern_plan',
        'divisin_perfomer',
        'days_ofset',
        'months_ofset',
        'years_ofset',
    )


@admin.register(models.Task)
class AdminTask(admin.ModelAdmin):
    list_display = (
        'name',
        'plan',
        'completion_date',
        'is_active',
    )


@admin.register(models.TaskGroup)
class AdminTaskGroup(admin.ModelAdmin):
    pass
