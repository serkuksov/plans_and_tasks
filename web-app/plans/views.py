import datetime

from django.utils.decorators import method_decorator
from django.views import generic
from django.http import HttpResponse
from django.db.transaction import atomic
from django.db.models import Case, When, Count
from django.db.models.functions import Round
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods

from .models import *
from . import tasks
from . import forms
from .servises import offset_date, export_in_doc, send_mail
from .permissions import (user_can_delete_task, user_can_assign_performer,
                          user_can_execute_task, user_can_update_plan_and_tasks)


class PlanListView(generic.ListView):
    """Отображение списка планов"""
    queryset = (Plan.objects.
                annotate(progress=10*Round(10*Count('id', filter=Q(task__is_active=False))/Count('task__id'), 1)))
    

class TaskListView(generic.ListView):
    """Отображение списка задач с возможностью сортировки"""
    queryset = (Task.objects.
                select_related('plan', 'perfomer__division', 'perfomer__performer_user__user').
                annotate(overdue=Case(When(completion_date__lt=datetime.datetime.now(), then=1))))
    ordering = ('-is_active', 'completion_date',)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET:
            form = forms.TaskFilterForm(self.request.GET)
            if form.is_valid():
                if form.cleaned_data.get('division'):
                    queryset = queryset.filter(perfomer__division=form.cleaned_data.get('division'))
                if form.cleaned_data.get('performer_user'):
                    queryset = queryset.filter(perfomer__performer_user=form.cleaned_data.get('performer_user'))
                if form.cleaned_data.get('is_overdue'):
                    queryset = queryset.filter(overdue=form.cleaned_data.get('is_overdue')).filter(is_active=True)
                if form.cleaned_data.get('is_active'):
                    queryset = queryset.filter(is_active=form.cleaned_data.get('is_active'))
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)
        context['form'] = forms.TaskFilterForm(self.request.GET)
        return context


class PlanAndTasksCreateView(LoginRequiredMixin, generic.CreateView):
    """Отображение формы создания плана и задач на основе шаблонов"""
    model = Plan
    form_class = forms.PlanCreateForm
    template_name = 'plans/plan_form_create.html'

    def get_initial(self):
        initial = super().get_initial()
        user_id = self.request.user.userdeteil.id
        initial = initial | {
            'user_creator': user_id,
            'user_updater': user_id,
        }
        return initial

    def get_success_url(self):
        return reverse('plans:plan_update', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pattern_plans'] = PatternPlan.objects.all()
        return context
    
    @atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        pattern_tasks = (PatternTask.objects.
                         select_related('divisin_perfomer').
                         filter(pattern_plan=form.cleaned_data['pattern_plan']).
                         all())
        new_tasks = []
        for pattern_task in pattern_tasks:
            completion_date_for_task = offset_date.get_completion_date_for_task(
                completion_date=form.cleaned_data['completion_date'],
                days=pattern_task.days_ofset,
                months=pattern_task.months_ofset,
                years=pattern_task.years_ofset,
                )
            new_tasks.append(Task(
                pattern_task=pattern_task,
                plan=self.object,
                name=pattern_task.name,
                completion_date=completion_date_for_task,
                perfomer=Perfomer.objects.create(division=pattern_task.divisin_perfomer),
                user_creator=form.cleaned_data['user_creator'],
                user_updater=form.cleaned_data['user_updater'],
            ))
        Task.objects.bulk_create(new_tasks)
        return response


class PlanAndTasksDetailView(generic.DetailView):
    """Отображение плана и связанных с ним задач"""
    queryset = (Plan.objects.
                select_related('user_creator__user', 'user_updater__user').
                annotate(progress=10*Round(10*Count('id', filter=Q(task__is_active=False))/Count('task__id'), 1)))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = (Task.objects.
                                select_related('perfomer__division', 'perfomer__performer_user__user').
                                filter(plan=self.object.id).
                                annotate(overdue=Case(When(completion_date__lt=datetime.datetime.now(), then=1))).
                                order_by('-is_active', 'completion_date'))
        context['is_delete_permission'] = user_can_delete_task(self.request, self.object)
        return context


@method_decorator(require_http_methods(['POST']), name='dispatch')
class PlanAndTasksDeleteView(LoginRequiredMixin, generic.DeleteView):
    """Удаление плана и связанных с ним задач"""
    model = Plan
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not user_can_delete_task(request, obj):
            raise PermissionDenied
        send_mail.notify_manager_plan_delete(plan_id=obj.id, plan_description=obj.description)
        return super().dispatch(request, *args, **kwargs)


class PlanAndTasksUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Редактирование плана и связанных с ним задач"""
    model = Plan
    form_class = forms.PlanUpdateForm
    template_name = 'plans/plan_form_update.html'

    def get_queryset_tasks(self):
        """Получить queryset задач текущего плана"""
        return (Task.objects.
                select_related('perfomer__division', 'pattern_task').
                filter(plan=self.object.id))

    def get_queryset_tasks_available_to_the_user(self):
        """Получить queryset задач доступных для редактирования пользователем"""
        task_qs = self.get_queryset_tasks()
        if user_can_update_plan_and_tasks(request=self.request, plan_obj=self.get_object()):
            return task_qs
        else:
            return task_qs.filter(perfomer__division=self.request.user.userdeteil.division)

    def get_initial(self):
        initial = super().get_initial()
        initial = initial | {
            'user_updater': self.request.user.userdeteil.id,
        }
        return initial

    @atomic
    def form_valid(self, form):
        plan = Plan.objects.filter(id=self.object.id).first()
        response = super().form_valid(form)
        task_forms = forms.TaskFormSet(self.request.POST, queryset=Task.objects.filter(plan=self.object.id))
        if task_forms.is_valid():
            instances = task_forms.save(commit=False)
            for task in task_forms.deleted_objects:
                task.delete()
            for task in instances:
                task.user_updater = self.request.user.userdeteil
                task.save()
        if plan.is_new_completion_date(completion_date=form.cleaned_data['completion_date']):
            task_qs = self.get_queryset_tasks()
            for task in task_qs:
                completion_date_for_task = offset_date.get_completion_date_for_task(
                            completion_date=form.cleaned_data['completion_date'],
                            days=task.pattern_task.days_ofset,
                            months=task.pattern_task.months_ofset,
                            years=task.pattern_task.years_ofset,
                            )
                task.completion_date = completion_date_for_task
            Task.objects.bulk_update(task_qs, ['completion_date'])
        if plan.is_new_plan():
            send_mail.notify_manager_plan_creation(plan_id=self.object.id, plan_url=self.request.build_absolute_uri())
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = forms.TaskFormSet(queryset=self.get_queryset_tasks_available_to_the_user())
        return context


class TaskDetailView(generic.DetailView, generic.View):
    """Подробное отображение задачи"""
    model = Task
    queryset = (Task.objects.
                select_related('user_creator__user',
                               'user_updater__user',
                               'plan',
                               'perfomer__performer_user__user',
                               'perfomer__division').
                annotate(overdue=Case(When(completion_date__lt=datetime.datetime.now(), then=1))).
                order_by('-is_active', 'completion_date'))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not user_can_execute_task(self.request, self.object.perfomer):
            raise PermissionDenied
        self.object.user_updater = self.request.user.userdeteil
        if self.object.is_active:
            self.object.is_active = False
        else:
            self.object.is_active = True
        self.object.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)       
        context['form'] = forms.PerfomerUpdateForm(instance=self.object.perfomer)
        context['is_performer_user'] = False if self.object.perfomer.performer_user is not None else True
        context['is_assign_perfomer'] = user_can_assign_performer(self.request, self.object.perfomer)
        context['is_possibility_execute'] = user_can_execute_task(self.request, self.object.perfomer)
        return context


def create_word_doc_for_plan_view(request, *args, **kwargs):
    doc = export_in_doc.create_word_doc_for_plan(plan_id=kwargs['pk'])
    name_doc = f'Plan_N{kwargs["pk"]}_ot_{datetime.datetime.now().date()}'
    response = HttpResponse(content_type='application/msword')
    response['Content-Disposition'] = f'attachment; filename="{name_doc}.doc"'
    doc.save(response)
    return response


@method_decorator(require_http_methods(['POST']), name='dispatch')
class PerfomerUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Назначение конкретного исполнителя (или снятие исполнителя) с задачи"""
    model = Perfomer
    queryset = Perfomer.objects.select_related('performer_user', 'division')
    form_class = forms.PerfomerUpdateForm
    template_name = 'plans/task_detail.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        if not user_can_assign_performer(self.request, self.object):
            raise PermissionDenied
        task = form.instance.task_set.first()
        task.user_updater = self.request.user.userdeteil
        task.save()
        return response

    def get_success_url(self):
        return self.object.task_set.all()[0].get_absolute_url()
