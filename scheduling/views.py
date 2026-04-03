from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from .models import Installation
from .forms import InstallationForm
from production.models import Order  # ДОБАВЯМЕ ТОВА

def installation_list(request):
    today = date.today()
    active_tab = request.GET.get('tab', 'upcoming')

    past_count = Installation.objects.filter(installation_date__lt=today).count()
    today_count = Installation.objects.filter(installation_date=today).count()
    upcoming_count = Installation.objects.filter(installation_date__gt=today).count()

    if active_tab == 'past':
        installations = Installation.objects.filter(installation_date__lt=today).order_by('-installation_date')
    elif active_tab == 'today':
        installations = Installation.objects.filter(installation_date=today).order_by('installation_date')
    else:  # upcoming
        installations = Installation.objects.filter(installation_date__gt=today).order_by('installation_date')

    unscheduled_orders = Order.objects.filter(status='ready', installations__isnull=True)

    context = {
        'installations': installations,
        'active_tab': active_tab,
        'today': today,
        'past_count': past_count,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'unscheduled_orders': unscheduled_orders,  # ПОДАВАМЕ ГИ ТУК
    }
    return render(request, 'scheduling/installation_list.html', context)


def installation_detail(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    return render(request, 'scheduling/installation_detail.html', {'installation': installation})


def installation_create(request):
    order_id = request.GET.get('order_id')

    if request.method == 'POST':
        form = InstallationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('scheduling:installation-list')
    else:
        initial_data = {}
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                initial_data['orders'] = [order.id]
                initial_data['address'] = order.delivery_address
            except Order.DoesNotExist:
                pass

        form = InstallationForm(initial=initial_data)

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
