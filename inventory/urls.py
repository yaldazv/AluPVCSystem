from django.urls import path
from . import views

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('add/', views.material_create, name='material_create'),
    path('<int:pk>/', views.material_detail, name='material_detail'),
    path('<int:pk>/edit/', views.material_update, name='material_update'),
    path('<int:pk>/delete/', views.material_delete, name='material_delete'),

    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),

    # Deliveries
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/add/', views.delivery_create, name='delivery_create'),
]
