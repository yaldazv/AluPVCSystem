from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Material, Supplier, Delivery
from .forms import MaterialForm, SupplierForm, DeliveryForm


def material_list(request):
    """Показва всички материали"""
    materials = Material.objects.all().order_by('material_type', 'name')

    context = {
        'materials': materials,
    }
    return render(request, 'inventory/material_list.html', context)


def material_create(request):
    """Създава нов материал (без количество - то се добавя през доставки)"""
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.quantity_in_stock = 0  # Започва с 0, ще се добави през доставки
            material.save()
            form.save_m2m()  # За ManyToMany полета
            messages.success(request,
                             f'Материалът "{material.name}" е добавен успешно! Сега можете да добавите доставка.')
            return redirect('material_list')
    else:
        form = MaterialForm()

    context = {
        'form': form,
        'title': 'Добави нов материал',
    }
    return render(request, 'inventory/material_form.html', context)


def material_update(request, pk):
    """Редактира съществуващ материал"""
    material = get_object_or_404(Material, pk=pk)

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            material = form.save()
            messages.success(request, f'Материалът "{material.name}" е обновен!')
            return redirect('material_list')
    else:
        form = MaterialForm(instance=material)

    context = {
        'form': form,
        'material': material,
        'title': f'Редактирай {material.name}',
    }
    return render(request, 'inventory/material_form.html', context)


def material_delete(request, pk):
    """Изтрива материал"""
    material = get_object_or_404(Material, pk=pk)

    if request.method == 'POST':
        material_name = material.name
        material.delete()
        messages.success(request, f'Материалът "{material_name}" е изтрит!')
        return redirect('material_list')

    context = {
        'material': material,
    }
    return render(request, 'inventory/material_confirm_delete.html', context)


def material_detail(request, pk):
    """Показва детайли за един материал + история на доставките"""
    material = get_object_or_404(Material, pk=pk)
    deliveries = material.deliveries.all()[:10]  # Последните 10 доставки

    context = {
        'material': material,
        'deliveries': deliveries,
    }
    return render(request, 'inventory/material_detail.html', context)


# ============ SUPPLIER VIEWS ============

def supplier_list(request):
    """Показва всички доставчици"""
    suppliers = Supplier.objects.all().order_by('name')

    context = {
        'suppliers': suppliers,
    }
    return render(request, 'inventory/supplier_list.html', context)


def supplier_create(request):
    """Добавяне на нов доставчик"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    context = {
        'form': form,
    }
    return render(request, 'inventory/supplier_form.html', context)


# ============ DELIVERY VIEWS ============

def delivery_list(request):
    """Показва всички доставки"""
    deliveries = Delivery.objects.all().select_related('material', 'supplier')

    context = {
        'deliveries': deliveries,
    }
    return render(request, 'inventory/delivery_list.html', context)


def delivery_create(request):
    """Създава нова доставка (автоматично увеличава наличността)"""
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save()
            messages.success(
                request,
                f'Доставката е регистрирана! Добавени {delivery.quantity} {delivery.material.unit} '
                f'от {delivery.material.name}. Обща стойност: {delivery.total_price:.2f} лв'
            )
            return redirect('delivery_list')
    else:
        form = DeliveryForm()

    context = {
        'form': form,
        'title': 'Регистрирай доставка',
    }
    return render(request, 'inventory/delivery_form.html', context)