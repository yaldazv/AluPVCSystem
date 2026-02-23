from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, CustomProduct, ReadyProduct
from .forms import OrderForm, OrderUpdateForm, CustomProductForm, ReadyProductForm


def order_list(request):
    orders = Order.objects.all()
    return render(request, 'production/order_list.html', {'orders': orders})


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    custom_products = order.products.all()
    ready_products = order.ready_products.all()

    context = {
        'order': order,
        'custom_products': custom_products,
        'ready_products': ready_products,
    }
    return render(request, 'production/order_detail.html', context)


def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f'✅ Поръчка #{order.id} за {order.customer_name} беше успешно създадена!')
            return redirect('production:order-detail', pk=order.pk)
    else:
        form = OrderForm()

    return render(request, 'production/order_form.html', {
        'form': form,
        'title': 'Нова поръчка'
    })


def order_update(request, pk):
    """Редактиране на съществуваща поръчка"""
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Поръчка #{order.id} беше актуализирана!')
            return redirect('production:order-detail', pk=order.pk)
    else:
        form = OrderUpdateForm(instance=order)

    return render(request, 'production/order_form.html', {
        'form': form,
        'order': order,
        'title': f'Редакция на поръчка #{order.id}'
    })


def order_delete(request, pk):
    """Изтриване на поръчка с потвърждение"""
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        customer_name = order.customer_name
        order.delete()
        messages.success(request, f'🗑️ Поръчка #{pk} за {customer_name} беше изтрита!')
        return redirect('production:order-list')

    return render(request, 'production/order_confirm_delete.html', {'order': order})



def custom_product_create(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)

    if request.method == 'POST':
        form = CustomProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.order = order

            # Обработка на конфигурацията за всяка част (ФИКС/ОТВАРЯЕМА)
            parts_config = []
            parts_count = product.parts_count

            for i in range(1, parts_count + 1):
                part_type = request.POST.get(f'part_{i}_type', 'fix')
                parts_config.append({
                    'position': i,
                    'type': part_type
                })

            product.parts_config = parts_config


            if not product.is_equal_parts and parts_count > 1:
                custom_widths = {}
                for i in range(1, parts_count):
                    width_value = request.POST.get(f'part_{i}_width')
                    if width_value:
                        custom_widths[f'part{i}_width'] = int(width_value)
                product.custom_widths = custom_widths
            else:
                product.custom_widths = {}

            # Изчисляване на отваряемите части
            openable_count = sum(1 for part in parts_config if part['type'] == 'open')
            product.openable_sashes = openable_count
            product.total_sashes = parts_count

            product.save()
            form.save_m2m()  # Запазва Many-to-Many връзките
            messages.success(request, f'✅ {product.get_product_type_display()} беше добавен към поръчката!')
            return redirect('production:order-detail', pk=order.pk)
    else:
        form = CustomProductForm()

    return render(request, 'production/custom_product_form.html', {
        'form': form,
        'order': order,
        'title': 'Добави прозорец/врата'
    })


def custom_product_update(request, pk):
    product = get_object_or_404(CustomProduct, pk=pk)

    if request.method == 'POST':
        form = CustomProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)

            parts_config = []
            parts_count = product.parts_count

            for i in range(1, parts_count + 1):
                part_type = request.POST.get(f'part_{i}_type', 'fix')
                parts_config.append({
                    'position': i,
                    'type': part_type
                })

            product.parts_config = parts_config


            if not product.is_equal_parts and parts_count > 1:
                custom_widths = {}
                for i in range(1, parts_count):
                    width_value = request.POST.get(f'part_{i}_width')
                    if width_value:
                        custom_widths[f'part{i}_width'] = int(width_value)
                product.custom_widths = custom_widths
            else:
                product.custom_widths = {}

            # Изчисляване на отваряемите части
            openable_count = sum(1 for part in parts_config if part['type'] == 'open')
            product.openable_sashes = openable_count
            product.total_sashes = parts_count

            product.save()
            form.save_m2m()
            messages.success(request, f'✅ {product.get_product_type_display()} беше актуализиран!')
            return redirect('production:order-detail', pk=product.order.pk)
    else:
        form = CustomProductForm(instance=product)

    return render(request, 'production/custom_product_form.html', {
        'form': form,
        'product': product,
        'order': product.order,
        'title': 'Редактирай продукт'
    })


def custom_product_delete(request, pk):
    product = get_object_or_404(CustomProduct, pk=pk)
    order = product.order

    if request.method == 'POST':
        product_name = str(product)
        product.delete()
        messages.success(request, f'🗑️ {product_name} беше изтрит!')
        return redirect('production:order-detail', pk=order.pk)

    return render(request, 'production/custom_product_confirm_delete.html', {
        'product': product,
        'order': order
    })


def ready_product_create(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)

    if request.method == 'POST':
        form = ReadyProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.order = order
            product.save()
            messages.success(request, f'✅ {product.name} беше добавен към поръчката!')
            return redirect('production:order-detail', pk=order.pk)
    else:
        form = ReadyProductForm()

    return render(request, 'production/ready_product_form.html', {
        'form': form,
        'order': order,
        'title': 'Добави готов продукт'
    })


def ready_product_update(request, pk):
    product = get_object_or_404(ReadyProduct, pk=pk)

    if request.method == 'POST':
        form = ReadyProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ {product.name} беше актуализиран!')
            return redirect('production:order-detail', pk=product.order.pk)
    else:
        form = ReadyProductForm(instance=product)

    return render(request, 'production/ready_product_form.html', {
        'form': form,
        'product': product,
        'order': product.order,
        'title': 'Редактирай готов продукт'
    })


def ready_product_delete(request, pk):
    product = get_object_or_404(ReadyProduct, pk=pk)
    order = product.order

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'🗑️ {product_name} беше изтрит!')
        return redirect('production:order-detail', pk=order.pk)

    return render(request, 'production/ready_product_confirm_delete.html', {
        'product': product,
        'order': order
    })
