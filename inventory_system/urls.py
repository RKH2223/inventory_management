"""
URL configuration for inventory_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.http import HttpResponse
from django.urls import path, include  # Import include
from inventory.views import (
    DashboardView, add_reel, add_daily_usage,
    delete_reel, edit_reel, ReelReportView,
    ReportsView, CustomLoginView, register
)
from django.contrib.auth import views as auth_views


# def home(request):
#     return HttpResponse("Hello, your Django app is working!")

urlpatterns = [
    path('admin/', admin.site.urls),
    # path("", home),  # This sets the homepage URL
    path('', DashboardView.as_view(), name='dashboard'),
    path('add-reel/', add_reel, name='add_reel'),
    path('add-daily-usage/', add_daily_usage, name='add_daily_usage'),
    path('delete-reel/<int:pk>/', delete_reel, name='delete_reel'),
    path('edit-reel/<int:pk>/', edit_reel, name='edit_reel'),
    path('reel-report/<int:pk>/', ReelReportView.as_view(), name='reel_report'),
    path('reports/', ReportsView.as_view(), name='reports'),
    
    # Authentication URLs
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/register/', register, name='register'),
]