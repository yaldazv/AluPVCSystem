from django.urls import path
from . import views

urlpatterns = [
    # Materials
    path('materials/', views.MaterialListView.as_view(), name='material_list'),
    path('materials/create/', views.MaterialCreateView.as_view(), name='material_create'),
    path('materials/<int:pk>/update/', views.MaterialUpdateView.as_view(), name='material_update'),
    path('materials/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='material_delete'),
    path('materials/<int:pk>/detail/', views.MaterialDetailView.as_view(), name='material_detail'),

    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),

    # Deliveries
    path('deliveries/', views.DeliveryListView.as_view(), name='delivery_list'),
    path('deliveries/create/', views.DeliveryCreateView.as_view(), name='delivery_create'),
]
