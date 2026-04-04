from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth import authenticate


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

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                user = None

            if user is not None and user.check_password(password):
                if not user.is_active:
                    raise forms.ValidationError(
                        "Вашият профил все още чака одобрение от администратор. Моля, опитайте по-късно.",
                        code='inactive',
                    )

            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Моля, проверете въведените данни. Потребителското име или паролата са грешни."
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
