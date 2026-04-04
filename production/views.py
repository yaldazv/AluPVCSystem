from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, CustomProduct, ReadyProduct, QuoteRequest
from .forms import OrderForm, OrderUpdateForm, CustomProductForm, ReadyProductForm, QuoteRequestForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer
from django_q.tasks import async_task
from .tasks import send_order_ready_email


# ==========================================
# ЗАЯВКИ ЗА ОГЛЕД (Quote Requests)
# ==========================================

class QuoteRequestCreateView(LoginRequiredMixin, CreateView):
    model = QuoteRequest
    form_class = QuoteRequestForm
    template_name = 'production/quote_request_form.html'
    success_url = reverse_lazy('production:quote-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Заяви оглед / Оферта'
        return context

    def form_valid(self, form):
        form.instance.customer = self.request.user
        messages.success(self.request, "Заявката ви за оглед/оферта беше изпратена успешно! Ще се свържем с вас скоро.")
        return super().form_valid(form)


class QuoteRequestListView(LoginRequiredMixin, ListView):
    model = QuoteRequest
    template_name = 'production/quote_request_list.html'
    context_object_name = 'quotes'

    def get_queryset(self):
        if self.request.user.role in ['Admin', 'Staff']:
            return QuoteRequest.objects.all().order_by('-created_at')
        return QuoteRequest.objects.filter(customer=self.request.user).order_by('-created_at')


class QuoteRequestDetailView(LoginRequiredMixin, DetailView):
    model = QuoteRequest
    template_name = 'production/quote_request_detail.html'
    context_object_name = 'quote'

    def get_queryset(self):
        # Ако е клиент, може да вижда само своите заявки. Ако е админ/персонал - всички.
        if self.request.user.role in ['Admin', 'Staff']:
            return QuoteRequest.objects.all()
        return QuoteRequest.objects.filter(customer=self.request.user)


class QuoteRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = QuoteRequest
    template_name = 'production/quote_request_update.html'
    # Персоналът може да променя само тези две полета:
    fields = ['status', 'notes']

    def dispatch(self, request, *args, **kwargs):
        # Само персонал може да редактира заявките
        if request.user.role not in ['Admin', 'Staff'] and not request.user.is_superuser:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Нямате права за редакция на заявки.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, f"Статусът на заявка #{self.object.id} беше обновен!")
        return reverse('production:quote-detail', kwargs={'pk': self.object.id})


# ==========================================
# ПОРЪЧКИ (Orders)
# ==========================================

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'production/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        if self.request.user.role == 'Customer':
            return Order.objects.filter(customer=self.request.user).order_by('-created_at')
        return Order.objects.all().order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'production/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_products'] = self.object.products.all()
        context['ready_products'] = self.object.ready_products.all()
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'production/order_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Нова поръчка'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request,
                         f'✅ Поръчка #{self.object.id} за {self.object.customer_name} беше успешно създадена!')
        return response

    def get_success_url(self):
        return reverse('production:order-detail', kwargs={'pk': self.object.pk})


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'production/order_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редакция на поръчка #{self.object.id}'
        return context

    def form_valid(self, form):
        # 1. Взимаме стария статус, ПРЕДИ да запишем новия
        old_status = self.get_object().status

        # 2. Запазваме формата (вече обектът има новия статус)
        response = super().form_valid(form)
        new_status = self.object.status

        # 3. Проверяваме дали статусът ТОКУ-ЩО е станал 'ready' (Готова за монтаж)
        if old_status != 'ready' and new_status == 'ready':
            customer_email = self.object.customer.email if self.object.customer else self.object.customer_email
            if not customer_email:
                customer_email = "test@example.com"  # fallback

            customer_name = self.object.customer.username if self.object.customer else (
                        self.object.customer_name or "Клиент")

            # 4. ИЗВИКВАМЕ АСИНХРОННАТА ЗАДАЧА! Тя ще се изпълни на заден план.
            async_task(send_order_ready_email, self.object.id, customer_email, customer_name)

            messages.info(self.request, "Започна асинхронно изпращане на имейл към клиента.")

        messages.success(self.request, f'✅ Поръчка #{self.object.id} беше актуализирана!')
        return response

    def get_success_url(self):
        return reverse('production:order-detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'production/order_confirm_delete.html'
    success_url = reverse_lazy('production:order-list')

    def form_valid(self, form):
        customer_name = self.object.customer_name
        messages.success(self.request, f'🗑️ Поръчка #{self.object.pk} за {customer_name} беше изтрита!')
        return super().form_valid(form)


# ==========================================
# ПРОДУКТИ ПО ПОРЪЧКА (Custom Products)
# ==========================================

class CustomProductCreateView(LoginRequiredMixin, CreateView):
    model = CustomProduct
    form_class = CustomProductForm
    template_name = 'production/custom_product_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=self.kwargs['order_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        context['title'] = 'Добави прозорец/врата'
        return context

    def form_valid(self, form):
        product = form.save(commit=False)
        product.order = self.order

        parts_config = []
        parts_count = product.parts_count

        for i in range(1, parts_count + 1):
            part_type = self.request.POST.get(f'part_{i}_type', 'fix')
            parts_config.append({
                'position': i,
                'type': part_type
            })

        product.parts_config = parts_config

        if not product.is_equal_parts and parts_count > 1:
            custom_widths = {}
            for i in range(1, parts_count):
                width_value = self.request.POST.get(f'part_{i}_width')
                if width_value:
                    custom_widths[f'part{i}_width'] = int(width_value)
            product.custom_widths = custom_widths
        else:
            product.custom_widths = {}

        openable_count = sum(1 for part in parts_config if part['type'] == 'open')
        product.openable_sashes = openable_count
        product.total_sashes = parts_count

        product.save()
        form.save_m2m()
        messages.success(self.request, f'✅ {product.get_product_type_display()} беше добавен към поръчката!')
        return redirect('production:order-detail', pk=self.order.pk)


class CustomProductUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomProduct
    form_class = CustomProductForm
    template_name = 'production/custom_product_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.order
        context['title'] = 'Редактирай продукт'
        return context

    def form_valid(self, form):
        product = form.save(commit=False)

        parts_config = []
        parts_count = product.parts_count

        for i in range(1, parts_count + 1):
            part_type = self.request.POST.get(f'part_{i}_type', 'fix')
            parts_config.append({
                'position': i,
                'type': part_type
            })

        product.parts_config = parts_config

        if not product.is_equal_parts and parts_count > 1:
            custom_widths = {}
            for i in range(1, parts_count):
                width_value = self.request.POST.get(f'part_{i}_width')
                if width_value:
                    custom_widths[f'part{i}_width'] = int(width_value)
            product.custom_widths = custom_widths
        else:
            product.custom_widths = {}

        openable_count = sum(1 for part in parts_config if part['type'] == 'open')
        product.openable_sashes = openable_count
        product.total_sashes = parts_count

        product.save()
        form.save_m2m()
        messages.success(self.request, f'✅ {product.get_product_type_display()} беше актуализиран!')
        return redirect('production:order-detail', pk=product.order.pk)


class CustomProductDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomProduct
    template_name = 'production/custom_product_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.order
        return context

    def form_valid(self, form):
        order_pk = self.object.order.pk
        product_name = str(self.object)
        self.object.delete()
        messages.success(self.request, f'🗑️ {product_name} беше изтрит!')
        return redirect('production:order-detail', pk=order_pk)


# ==========================================
# ГОТОВИ ПРОДУКТИ (Ready Products)
# ==========================================

class ReadyProductCreateView(LoginRequiredMixin, CreateView):
    model = ReadyProduct
    form_class = ReadyProductForm
    template_name = 'production/ready_product_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=self.kwargs['order_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        context['title'] = 'Добави готов продукт'
        return context

    def form_valid(self, form):
        product = form.save(commit=False)
        product.order = self.order
        product.save()
        messages.success(self.request, f'✅ {product.name} беше добавен към поръчката!')
        return redirect('production:order-detail', pk=self.order.pk)


class ReadyProductUpdateView(LoginRequiredMixin, UpdateView):
    model = ReadyProduct
    form_class = ReadyProductForm
    template_name = 'production/ready_product_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.order
        context['title'] = 'Редактирай готов продукт'
        return context

    def form_valid(self, form):
        product = form.save()
        messages.success(self.request, f'✅ {product.name} беше актуализиран!')
        return redirect('production:order-detail', pk=product.order.pk)


class ReadyProductDeleteView(LoginRequiredMixin, DeleteView):
    model = ReadyProduct
    template_name = 'production/ready_product_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.order
        return context

    def form_valid(self, form):
        order_pk = self.object.order.pk
        product_name = self.object.name
        self.object.delete()
        messages.success(self.request, f'🗑️ {product_name} беше изтрит!')
        return redirect('production:order-detail', pk=order_pk)


# ==========================================
# REST API ENDPOINTS (Django Rest Framework)
# ==========================================
class OrderAPIView(APIView):
    """
    API Endpoint, който връща всички поръчки на логнатия потребител в JSON формат.
    Ако потребителят е Staff/Admin, връща всички поръчки.
    """
    permission_classes = [IsAuthenticated]  # Само логнати потребители имат достъп!

    def get(self, request):
        # 1. Извличаме поръчките според ролята
        if request.user.role in ['Admin', 'Staff']:
            orders = Order.objects.all().order_by('-created_at')
        else:
            orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

