from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, CustomUserLoginForm, AdminUserCreationForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Чака одобрение!
            user.save()
            messages.success(request, 'Регистрацията е успешна! Очаквайте одобрение от администратор.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def admin_create_user_view(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return HttpResponseForbidden("Нямате права за достъп до тази страница.")

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Управителят директно създава активен профил
            user.save()
            messages.success(request, f'Успешно създадохте профил за {user.username} с роля {user.get_role_display()}!')
            return redirect('home')  # Или към списък с потребители
    else:
        form = AdminUserCreationForm()

    return render(request, 'accounts/admin_create_user.html',
                  {'form': form, 'title': 'Регистрация на нов потребител (Управител)'})


def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
