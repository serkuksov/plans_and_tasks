import datetime

from django import forms

from .models import *
from accounts.models import *


class PlanCreateForm(forms.ModelForm):
    user_creator = forms.ModelChoiceField(queryset=UserDeteil.objects.all(), widget=forms.HiddenInput())
    user_updater = forms.ModelChoiceField(queryset=UserDeteil.objects.all(), widget=forms.HiddenInput())
    completion_date = forms.DateField(
        widget=forms.SelectDateWidget({'class': 'form-select'}), 
        label='Планируямая дата завершения План-графика', 
        label_suffix={'class': 'form-select'}
        )

    class Meta:
        model = Plan
        fields = (
            'user_creator',
            'user_updater',
            'pattern_plan',
            'completion_date',
        )
    
    def save(self):
        super().save(commit=False)
        self.instance.name = self.instance.pattern_plan.name + ' (' + str(datetime.datetime.now()) + ')'
        self.instance.description = self.instance.pattern_plan.description
        self.instance.save()
        return self.instance


class PlanUpdateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput({'class': 'form-control form-control-lg'}))
    description = forms.CharField(widget=forms.Textarea({'class': 'form-control form-control-lg'}))
    user_updater = forms.ModelChoiceField(queryset=UserDeteil.objects.all(), widget=forms.HiddenInput())
    completion_date = forms.DateField(
        widget=forms.SelectDateWidget({'class': 'form-select'}), 
        label='Планируямая дата завершения План-графика', 
        label_suffix={'class': 'form-select'}
        )
    
    class Meta:
        model = Plan
        fields = (
            'name',
            'description',
            'user_updater',
            'completion_date',
        )


class TaskUpdateNameForm(forms.ModelForm):
    name = forms.CharField(widget=forms.Textarea({'class': 'form-control form-control-lg', 'style': 'height:120px;'}))

    class Meta:
        model = Task
        fields = (
            'name',
        )


class BaseTaskFormSet(forms.BaseModelFormSet):
    deletion_widget = forms.CheckboxInput({'class': 'form-check-input is-invalid'})


TaskFormSet = forms.modelformset_factory(model=Task, form=TaskUpdateNameForm, extra=0, can_delete=True, formset=BaseTaskFormSet)


class TaskUpdateIsActiveForm(forms.ModelForm):
    is_active = forms.BooleanField(widget=forms.Select({'class': 'form-select'}, choices=((True, 'В работе'), (False, 'Выполнено'))), required=False)

    class Meta:
        model = Task
        fields = (
            'is_active',
        )



class TaskFilterForm(forms.Form):
    division = forms.ModelChoiceField(queryset=Division.objects.all(), required=False, empty_label='Все', widget=forms.Select({'class': 'form-select form-select-lg'}))
    performer_user = forms.ModelChoiceField(queryset=UserDeteil.objects.none(), required=False, empty_label='Все', widget=forms.Select({'class': 'form-select form-select-lg'}))
    is_overdue = forms.BooleanField(widget=forms.CheckboxInput({'class': 'form-check-input is-invalid'}), required=False)
    is_active = forms.BooleanField(widget=forms.CheckboxInput({'class': 'form-check-input'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        division = args[0].get('division')
        if division:
            self.fields['performer_user'].queryset = (UserDeteil.objects.
                                                      select_related('user', 'division').
                                                      filter(division_id=division).all())


class PerfomerUpdateForm(forms.ModelForm):
    performer_user = forms.ModelChoiceField(queryset=UserDeteil.objects.none(), required=False, empty_label='Выборать работника', widget=forms.Select({'class': 'form-select form-select-lg'}))

    def __init__(self, *args, **kwargs):
        performer = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        division = performer.division
        self.fields['performer_user'].queryset = UserDeteil.objects.filter(division=division).all()

    class Meta:
        model = Perfomer
        fields = (
            'performer_user',
        )