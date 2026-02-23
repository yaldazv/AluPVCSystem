from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    path('', views.installation_list, name='installation-list'),
    path('<int:pk>/', views.installation_detail, name='installation-detail'),
    path('add/', views.installation_create, name='installation-create'),
    path('<int:pk>/edit/', views.installation_update, name='installation-update'),
    path('<int:pk>/delete/confirm/', views.installation_delete_confirm, name='installation-delete-confirm'),
    path('<int:pk>/delete/', views.installation_delete, name='installation-delete'),
]
