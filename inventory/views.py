from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Material, Supplier, Delivery
from .forms import MaterialForm, SupplierForm, DeliveryForm


# ============ MATERIAL VIEWS ============

class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'inventory/material_list.html'
    context_object_name = 'materials'

    def get_queryset(self):
        return Material.objects.all().order_by('material_type', 'name')


class MaterialDetailView(LoginRequiredMixin, DetailView):
    model = Material
    template_name = 'inventory/material_detail.html'
    context_object_name = 'material'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Взимаме последните 10 доставки за този материал
        context['deliveries'] = self.object.deliveries.all()[:10]
        return context


class MaterialCreateView(LoginRequiredMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html'
    success_url = reverse_lazy('material_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добави нов материал'
        return context

    def form_valid(self, form):
        material = form.save(commit=False)
        material.quantity_in_stock = 0
        material.save()
        form.save_m2m()  # Задължително за ManyToMany полета
        messages.success(self.request,
                         f'Материалът "{material.name}" е добавен успешно! Сега можете да добавите доставка.')
        return super().form_valid(form)


class MaterialUpdateView(LoginRequiredMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html'
    success_url = reverse_lazy('material_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирай {self.object.name}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Материалът "{self.object.name}" е обновен!')
        return super().form_valid(form)


class MaterialDeleteView(LoginRequiredMixin, DeleteView):
    model = Material
    template_name = 'inventory/material_confirm_delete.html'
    success_url = reverse_lazy('material_list')

    def form_valid(self, form):
        messages.success(self.request, f'Материалът "{self.object.name}" е изтрит!')
        return super().form_valid(form)


# ============ SUPPLIER VIEWS ============

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_queryset(self):
        return Supplier.objects.all().order_by('name')


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('supplier_list')


# ============ DELIVERY VIEWS ============

class DeliveryListView(LoginRequiredMixin, ListView):
    model = Delivery
    template_name = 'inventory/delivery_list.html'
    context_object_name = 'deliveries'

    def get_queryset(self):
        return Delivery.objects.all().select_related('material', 'supplier')


class DeliveryCreateView(LoginRequiredMixin, CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'inventory/delivery_form.html'
    success_url = reverse_lazy('delivery_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрирай доставка'
        return context

    def form_valid(self, form):
        delivery = form.save()
        messages.success(
            self.request,
            f'Доставката е регистрирана! Добавени {delivery.quantity} {delivery.material.unit} '
            f'от {delivery.material.name}. Обща стойност: {delivery.total_price:.2f} лв'
        )
        return super().form_valid(form)
