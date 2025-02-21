from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-reel/', views.add_reel, name='add_reel'),
    path('add-daily-usage/', views.add_daily_usage, name='add_daily_usage'),
    path('delete-reel/<int:pk>/', views.delete_reel, name='delete_reel'),
    # path('search/', views.search_reel, name='search_reel'),

    
    
    # path('deep', views.deepview, name='deep bhai view'),

]