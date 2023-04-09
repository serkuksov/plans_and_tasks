from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.core import validators

from accounts.models import UserDeteil, Division


class UserDeteilChangeForm(UserChangeForm):
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилие')
    second_name = forms.CharField(label='Отчество')
    phone_number = forms.IntegerField(label='Номер телефона', 
                                      validators=[validators.MinValueValidator(3300),
                                                  validators.MaxValueValidator(3399)])
    division = forms.ModelChoiceField(queryset=Division.objects.all(), label='Подразделение')
    is_manager = forms.BooleanField(label='Руководитель?')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['second_name'].initial = self.instance.userdeteil.second_name
            self.fields['phone_number'].initial = self.instance.userdeteil.phone_number
            self.fields['division'].initial = self.instance.userdeteil.division
            self.fields['is_manager'].initial = self.instance.userdeteil.is_manager
        except Exception as ex:
            print(ex)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if UserDeteil.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Номер телефона используется другим пользователем')
        return phone_number

    class Meta:
        model = get_user_model()
        fields = '__all__'


class UserDeteilCreationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилие')
    second_name = forms.CharField(label='Отчество')
    phone_number = forms.IntegerField(label='Номер телефона', 
                                      validators=[validators.MinValueValidator(3300),
                                                  validators.MaxValueValidator(3399)])
    division = forms.ModelChoiceField(queryset=Division.objects.all(), label='Подразделение')
    is_manager = forms.BooleanField(label='Руководитель')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if UserDeteil.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Номер телефона используется другим пользователем')
        return phone_number

    class Meta:
        model = get_user_model()
        fields = '__all__'


class MyAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True,
                                      'class': 'form-control',
                                      'id': 'floatingInput'}))
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password',
                                          'class': 'form-control',
                                          'id': 'floatingPassword'}),
    )
