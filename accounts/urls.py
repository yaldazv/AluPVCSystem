from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-create-user/', views.admin_create_user_view, name='admin_create_user'),
    path('pending-users/', views.pending_users_view, name='pending_users'),
    path('approve-user/<int:user_id>/', views.approve_user_view, name='approve_user'),
]
