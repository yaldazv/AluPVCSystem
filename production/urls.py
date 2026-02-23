from django.urls import path, include
from . import views

app_name = 'production'

# URL patterns за поръчки
order_patterns = [
    path('', views.order_list, name='order-list'),
    path('add/', views.order_create, name='order-create'),
    path('<int:pk>/', views.order_detail, name='order-detail'),
    path('<int:pk>/edit/', views.order_update, name='order-update'),
    path('<int:pk>/delete/', views.order_delete, name='order-delete'),
    path('<int:order_pk>/add-window-door/', views.custom_product_create, name='add-custom-product'),
    path('<int:order_pk>/add-ready-product/', views.ready_product_create, name='add-ready-product'),
]

# URL patterns за прозорци/врати
custom_product_patterns = [
    path('<int:pk>/edit/', views.custom_product_update, name='edit-custom-product'),
    path('<int:pk>/delete/', views.custom_product_delete, name='delete-custom-product'),
]

# URL patterns за готови продукти
ready_product_patterns = [
    path('<int:pk>/edit/', views.ready_product_update, name='edit-ready-product'),
    path('<int:pk>/delete/', views.ready_product_delete, name='delete-ready-product'),
]

urlpatterns = [
    path('orders/', include(order_patterns)),
    path('custom-products/', include(custom_product_patterns)),
    path('ready-products/', include(ready_product_patterns)),
]
