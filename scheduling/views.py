from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import date
from .models import Installation
from .forms import InstallationForm


def installation_list(request):
    today = date.today()

    # Определяме активния таб (по подразбиране 'upcoming')
    active_tab = request.GET.get('tab', 'upcoming')

    if active_tab == 'past':
        installations = Installation.objects.filter(installation_date__lt=today).order_by('-installation_date')
    elif active_tab == 'today':
        installations = Installation.objects.filter(installation_date=today).order_by('installation_date')
    else:  # upcoming
        installations = Installation.objects.filter(installation_date__gte=today).order_by('installation_date')

    context = {
        'installations': installations,
        'active_tab': active_tab,
        'today': today,
    }
    return render(request, 'scheduling/installation_list.html', context)


def installation_detail(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    return render(request, 'scheduling/installation_detail.html', {'installation': installation})


def installation_create(request):
    if request.method == 'POST':
        form = InstallationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('scheduling:installation-list')
    else:
        form = InstallationForm()

    return render(request, 'scheduling/installation_form.html', {'form': form, 'action': 'Добавяне'})


def installation_update(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    if request.method == 'POST':
        form = InstallationForm(request.POST, instance=installation)
        if form.is_valid():
            form.save()
            return redirect('scheduling:installation-detail', pk=pk)
    else:
        form = InstallationForm(instance=installation)

    return render(request, 'scheduling/installation_form.html', {
        'form': form,
        'action': 'Редакция',
        'installation': installation
    })


def installation_delete_confirm(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    return render(request, 'scheduling/installation_delete_confirm.html', {'installation': installation})


def installation_delete(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    if request.method == 'POST':
        installation.delete()
        return redirect('scheduling:installation-list')
    return redirect('scheduling:installation-delete-confirm', pk=pk)
