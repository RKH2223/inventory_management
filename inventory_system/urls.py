# inventory_system/urls.py

from django.contrib import admin
from django.urls import path, include, reverse_lazy # Import reverse_lazy
from django.contrib.auth import views as auth_views # Import Django's auth views

# Import your custom views from the inventory app
from inventory.views import CustomLoginView, register
# Assuming your dashboard view is also in inventory.views
# from inventory.views import DashboardView # Add if needed for explicit URL names

urlpatterns = [
    # 1. Django Admin Interface
    path('admin/', admin.site.urls),

    # 2. Your Custom Authentication URLs
    #    Place these BEFORE `include('django.contrib.auth.urls')` to ensure your
    #    custom views take precedence and are resolved first.

    # Custom Login URL: Maps to your CustomLoginView
    path('accounts/login/', CustomLoginView.as_view(), name='login'),

    # Custom Registration URL: Maps to your custom register function
    path('accounts/register/', register, name='register'),

    # Logout URL: Using Django's built-in LogoutView,
    # and redirecting to your 'login' page after logout.
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),

    # 3. Remaining Django Auth URLs (for password reset, change etc.)
    #    This includes password_reset, password_reset_done, password_reset_confirm,
    #    password_reset_complete.
    #    These will use Django's default templates (e.g., registration/password_reset_form.html)
    #    You would need to create those templates if you want to customize their appearance.
    path('accounts/', include('django.contrib.auth.urls')),

    # 4. Include your application's URLs (inventory app)
    #    This should generally be the last pattern for your main app to catch remaining routes.
    path('', include('inventory.urls')),
]