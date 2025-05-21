from django.urls import path
from .views import DashboardView, add_reel, add_daily_usage, delete_reel, ReelReportView, ReportsView, edit_reel

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('add-reel/', add_reel, name='add_reel'),
    path('add-daily-usage/', add_daily_usage, name='add_daily_usage'),
    path('delete-reel/<int:pk>/', delete_reel, name='delete_reel'),
    path('edit-reel/<int:pk>/', edit_reel, name='edit_reel'),
    path('reel-report/<int:pk>/', ReelReportView.as_view(), name='reel_report'),
    path('reports/', ReportsView.as_view(), name='reports'),
    # path('search/', views.search_reel, name='search_reel'),

    
    
    # path('deep', views.deepview, name='deep bhai view'),

]