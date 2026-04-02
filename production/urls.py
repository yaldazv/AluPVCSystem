from django.urls import path, include
from . import views

app_name = 'production'

# URL patterns за заявки за оферта/оглед (НОВО)
quote_patterns = [
    path('', views.QuoteRequestListView.as_view(), name='quote-list'),
    path('add/', views.QuoteRequestCreateView.as_view(), name='quote-create'),
]

# URL patterns за поръчки
order_patterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('add/', views.OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order-update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order-delete'),

    # Тук използваме същите имена на маршрути както преди!
    path('<int:order_pk>/add-window-door/', views.CustomProductCreateView.as_view(), name='add-custom-product'),
    path('<int:order_pk>/add-ready-product/', views.ReadyProductCreateView.as_view(), name='add-ready-product'),
]

# URL patterns за прозорци/врати
custom_product_patterns = [
    path('<int:pk>/edit/', views.CustomProductUpdateView.as_view(), name='edit-custom-product'),
    path('<int:pk>/delete/', views.CustomProductDeleteView.as_view(), name='delete-custom-product'),
]

ready_product_patterns = [
    path('<int:pk>/edit/', views.ReadyProductUpdateView.as_view(), name='edit-ready-product'),
    path('<int:pk>/delete/', views.ReadyProductDeleteView.as_view(), name='delete-ready-product'),
]

urlpatterns = [
    path('quotes/', include(quote_patterns)),
    path('orders/', include(order_patterns)),
    path('custom-products/', include(custom_product_patterns)),
    path('ready-products/', include(ready_product_patterns)),
    path('api/orders/', views.OrderAPIView.as_view(), name='api-orders'),
]

