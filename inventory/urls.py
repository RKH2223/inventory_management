from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),  # Keep this one
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('', views.DashboardView.as_view(), name='dashboard'),

    path('inventory/', views.inventory_view, name='inventory'),
    path('deepview/', views.deepview, name='deepview'),

    path('add-reel/', views.add_reel, name='add_reel'),
    path('edit-reel/<int:pk>/', views.edit_reel, name='edit_reel'),
    path('delete-reel/<int:pk>/', views.delete_reel, name='delete_reel'),

    path('add-daily-usage/', views.add_daily_usage, name='add_daily_usage'),
    path('reel-report/<int:pk>/', views.ReelReportView.as_view(), name='reel_report'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
]
