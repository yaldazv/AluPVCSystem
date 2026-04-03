from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('Customer', 'Клиент'),
        ('Supplier', 'Доставчик'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='Customer',
        label="Тип профил",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'company_name', 'role')

class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'company_name', 'role')

class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
