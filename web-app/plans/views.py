
from django.views import generic
from django.http import HttpResponse
from django.db.transaction import atomic
from django.db.models import Case, When, Count
from django.db.models.functions import Round
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import *
from . import forms
from .servises import servises, export_in_doc
from .permissions import has_delete_permission, can_assign_perfomer, can_possibility_execute


class PlanListView(generic.ListView):
    model = Plan
    queryset = Plan.objects.annotate(progress=10*Round(10*Count('id', filter=Q(task__is_active=False))/Count('task__id'), 1))
    

class TaskListView(generic.ListView):
    model = Task
    queryset = Task.objects.annotate(overdue=Case(When(completion_date__lt=datetime.datetime.now(), then=1)))
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


class PlanCreateView(LoginRequiredMixin, generic.CreateView):
    model = Plan
    form_class = forms.PlanCreateForm
    template_name = 'plans/plan_form_create.html'

    def get_initial(self):
        initial = super().get_initial()
        initial = initial | {
            'user_creator': self.request.user.userdeteil.id,
            'user_updater': self.request.user.userdeteil.id,
        }
        return initial

    def get_success_url(self):
        return reverse('plans:plan_update', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pattern_plans'] = PatternPlan.objects.all()
        print(context['form'].errors)
        return context
    
    @atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        pattern_tasks = PatternTask.objects.filter(pattern_plan=self.object.pattern_plan).all()
        for pattern_task in pattern_tasks:
            completion_date = self.object.completion_date
            completion_date_for_task = servises.get_completion_date_for_task(completion_date=completion_date,
                                                                            days=pattern_task.days_ofset,
                                                                            months=pattern_task.months_ofset,
                                                                            years=pattern_task.years_ofset,
                                                                            )
            Task.objects.create(
                pattern_task = pattern_task,
                plan = self.object,
                name = pattern_task.name,
                completion_date = completion_date_for_task,
                perfomer = Perfomer.objects.create(division=pattern_task.divisin_perfomer),
                user_creator = self.request.user.userdeteil,
                user_updater = self.request.user.userdeteil,
            )
        return response


class PlanDetailView(generic.DetailView):
    model = Plan
    queryset = Plan.objects.annotate(progress=10*Round(10*Count('id', filter=Q(task__is_active=False))/Count('task__id'), 1))
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = Task.objects.filter(plan=self.object.id).annotate(overdue=Case(When(completion_date__lt=datetime.datetime.now(), then=1))).order_by('-is_active', 'completion_date')
        context['is_delete_permission'] = has_delete_permission(self.request, self.object)
        return context


class PlanDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Plan
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not has_delete_permission(request, obj):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PlanUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Plan
    form_class = forms.PlanUpdateForm
    template_name = 'plans/plan_form_update.html'

    def get_initial(self):
        initial = super().get_initial()
        initial = initial | {
            'user_updater': self.request.user.userdeteil.id,
        }
        return initial

    @atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        tasks = Task.objects.filter(plan=self.object).order_by('-is_active', 'completion_date')
        task_forms = forms.TaskFormSet(self.request.POST)
        for task_form in task_forms:
            completion_date = self.object.completion_date
            completion_date_for_task = servises.get_completion_date_for_task(completion_date=completion_date,
                                                                            days=task_form.instance.pattern_task.days_ofset,
                                                                            months=task_form.instance.pattern_task.months_ofset,
                                                                            years=task_form.instance.pattern_task.years_ofset,
                                                                            )
            task=task_form.save(commit=False)
            task.completion_date = completion_date_for_task
            if task.is_active:
                task.user_updater = self.request.user.userdeteil
            task.save()
        task_forms.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = Task.objects.filter(plan=self.object.id).order_by('-is_active', 'completion_date')
        context['formset'] = forms.TaskFormSet(queryset=tasks)
        return context


class TaskDetailView(generic.DetailView, generic.View):
    model = Task
    queryset = Task.objects.annotate(overdue=Case(When(completion_date__lt=datetime.datetime.now(), then=1))).order_by('-is_active', 'completion_date')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_possibility_execute(self.request, self.object.perfomer):
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
        context['is_assign_perfomer'] = can_assign_perfomer(self.request, self.object.perfomer)
        context['is_possibility_execute'] = can_possibility_execute(self.request, self.object.perfomer)
        return context


def create_word_doc_for_plan_view(request, *args, **kwargs):
    doc = export_in_doc.create_word_doc_for_plan(plan_id=kwargs['pk'])
    name_doc = f'Plan_N{kwargs["pk"]}_ot_{datetime.datetime.now().date()}'
    response = HttpResponse(content_type='application/msword')
    response['Content-Disposition'] = f'attachment; filename="{name_doc}.doc"'
    doc.save(response)
    return response


class PerfomerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Perfomer
    form_class = forms.PerfomerUpdateForm
    template_name = 'plans/task_detail.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        if not can_assign_perfomer(self.request, self.object):
            raise PermissionDenied
        task = form.instance.task_set.first()
        task.user_updater = self.request.user.userdeteil
        task.save()
        return response

    def get_success_url(self):
        return self.object.task_set.all()[0].get_absolute_url()

