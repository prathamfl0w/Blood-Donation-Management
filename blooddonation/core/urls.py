from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('donors/', views.show_donors, name='donors'),
    path('register/', views.register_view, name='register'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('donate/', views.donate_view, name='donate'),
    path('request-blood/', views.request_blood, name='request_blood'),
    path('profile/', views.profile_view, name='profile'),
    path('request-history/', views.request_history, name='request_history'),
    path('admin-donations/', views.admin_donations, name='admin_donations'),
    path('admin-requests/', views.admin_requests, name='admin_requests'),
    path('update-donation-status/<int:donation_id>/<str:status>/', 
         views.update_donation_status, name='update_donation_status'),
    path('update-request-status/<int:request_id>/<str:status>/', 
         views.update_request_status, name='update_request_status'),
]