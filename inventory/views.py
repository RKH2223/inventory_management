from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reel, DailyUsage
from .forms import NewReelForm, DailyUsageForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewReelForm
from django.shortcuts import render, redirect
from .models import Reel
from .forms import NewReelForm
from django.contrib import messages
from django.db.models import F
from decimal import Decimal  # Import Decimal
from django.db.models import Q
from django.core.cache import cache
from django.db.models import Sum
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractYear, ExtractMonth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Avg
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv


class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        return self.success_url

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'inventory/register.html', {'form': form})

LOW_STOCK_THRESHOLD = 200.00

def inventory_view(request):
    return render(request, 'inventory.html')  # Change 'inventory.html' to your actual template file

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Reel
from .forms import NewReelForm, DailyUsageForm

LOW_STOCK_THRESHOLD = 200  # Define threshold for low stock warning


def deepview(request):
    return render(request, 'inventory/reel_list.html')


# def search_reel(request):
#     query = request.GET.get('q')  # Get search term from URL query parameters
#     try:
#         searched_reels = Reel.objects.filter(reel_code__icontains=query) if query else []
#     except Exception as e:
#         print("some issues in Database during the fetching the data.", e)
#     return render(request, 'inventory/dashboard.html', {'searched_reels': searched_reels , 'query': query})


class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string(
                'inventory/reel_list.html',
                {'reels': self.get_queryset()},
                request=request
            )
            return JsonResponse({'html': html})

        # Get search query if any
        search_query = request.GET.get('search', '')
        
        # Get all reels with consistent ordering
        reels = Reel.objects.all().order_by('reel_code')
        
        # Apply search filter if query exists
        if search_query:
            reels = reels.filter(
                Q(reel_code__icontains=search_query) |
                Q(reel_type__icontains=search_query)
            )
        
        # Calculate statistics
        total_reels = reels.count()
        total_stock = reels.aggregate(Sum('current_stock'))['current_stock__sum'] or 0
        low_stock_count = reels.filter(current_stock__lte=200).count()
        avg_stock_per_reel = total_stock / total_reels if total_reels > 0 else 0
        
        # Pagination
        paginator = Paginator(reels, 10)  # Show 10 reels per page
        page_number = request.GET.get('page')
        reels = paginator.get_page(page_number)
        
        context = {
            'reels': reels,
            'total_reels': total_reels,
            'total_stock': total_stock,
            'low_stock_count': low_stock_count,
            'avg_stock_per_reel': avg_stock_per_reel,
            'search_query': search_query,
        }
        
        return render(request, 'inventory/dashboard.html', context)

    def post(self, request, *args, **kwargs):
        if 'submit_new_reel' in request.POST:
            form = NewReelForm(request.POST)
            if form.is_valid():
                reel_code = form.cleaned_data['reel_code']
                existing_reel = Reel.objects.filter(
                    reel_code=reel_code,
                    reel_type=form.cleaned_data['reel_type'],
                    size_inch=form.cleaned_data['size_inch']
                ).first()

                if existing_reel:
                    existing_reel.current_stock += form.cleaned_data['weight_kg']
                    existing_reel.save()
                    messages.success(request, "Existing reel stock updated successfully.")
                else:
                    form.save()
                    messages.success(request, "New reel added successfully.")
                
                # Invalidate cache
                cache.delete('low_stock_warnings')
                return redirect('dashboard')
            else:
                messages.error(request, "Please correct the errors below.")
        
        elif 'submit_daily_usage' in request.POST:
            form = DailyUsageForm(request.POST)
            if form.is_valid():
                daily_usage = form.save(commit=False)
                if daily_usage.reel and daily_usage.used_weight:
                    if daily_usage.reel.current_stock >= daily_usage.used_weight:
                        Reel.objects.filter(id=daily_usage.reel.id).update(
                            current_stock=F('current_stock') - Decimal(daily_usage.used_weight)
                        )
                        daily_usage.save()
                        messages.success(request, "Daily usage logged successfully.")
                        # Invalidate cache
                        cache.delete('low_stock_warnings')
                    else:
                        messages.error(request, "Not enough stock available.")
                return redirect('dashboard')
            else:
                messages.error(request, "Please correct the errors below.")
        
        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        return Reel.objects.all().order_by('reel_code')

def add_reel(request):
    if request.method == 'POST':
        form = NewReelForm(request.POST)
        if form.is_valid():
            reel_code = form.cleaned_data['reel_code']
            existing_reel = Reel.objects.filter(
                reel_code=reel_code,
                reel_type=form.cleaned_data['reel_type'],
                size_inch=form.cleaned_data['size_inch']
            ).first()

            if existing_reel:
                existing_reel.current_stock += form.cleaned_data['weight_kg']
                existing_reel.save()
                messages.success(request, "Existing reel stock updated successfully.")
            else:
                form.save()
                messages.success(request, "New reel added successfully.")
            
            # Invalidate cache
            cache.delete('low_stock_warnings')
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NewReelForm()

    return render(request, 'inventory/add_reel.html', {'form': form})

def add_daily_usage(request):
    if request.method == 'POST':
        form = DailyUsageForm(request.POST)
        if form.is_valid():
            daily_usage = form.save(commit=False)
            if daily_usage.reel and daily_usage.used_weight:
                if daily_usage.reel.current_stock >= daily_usage.used_weight:
                    Reel.objects.filter(id=daily_usage.reel.id).update(
                        current_stock=F('current_stock') - Decimal(daily_usage.used_weight)
                    )
                    daily_usage.save()
                    messages.success(request, "Daily usage logged successfully.")
                    # Invalidate cache
                    cache.delete('low_stock_warnings')
                else:
                    messages.error(request, "Not enough stock available.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DailyUsageForm()

    return render(request, 'inventory/add_daily_usage.html', {'form': form})

def delete_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    reel.delete()
    messages.success(request, f"Reel {reel.reel_code} has been deleted successfully.")
    return redirect('dashboard')

def edit_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    if request.method == 'POST':
        form = NewReelForm(request.POST, instance=reel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Reel {reel.reel_code} has been updated successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NewReelForm(instance=reel)
    
    return render(request, 'inventory/edit_reel.html', {'form': form, 'reel': reel})

class ReelReportView(DetailView):
    model = Reel
    template_name = 'inventory/reel_report.html'
    context_object_name = 'reel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reel = self.get_object()

        # Get usage history for this reel
        usage_history = DailyUsage.objects.filter(reel=reel).order_by('-usage_date')
        total_usage = DailyUsage.objects.filter(reel=reel).aggregate(Sum('used_weight'))['used_weight__sum'] or 0

        # Get monthly usage statistics for this reel
        monthly_usage = DailyUsage.objects.filter(reel=reel).annotate(
            year=ExtractYear('usage_date'),
            month=ExtractMonth('usage_date')
        ).values('year', 'month').annotate(
            total_usage=Sum('used_weight')
        ).order_by('-year', '-month')

        context.update({
            'usage_history': usage_history,
            'total_usage': total_usage,
            'monthly_usage': monthly_usage,
        })
        return context

class ReportsView(TemplateView):
    template_name = 'inventory/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
         
        #Base query for daily usage
        usage_query = DailyUsage.objects.all()
        
        # Apply date filters if provided
        if start_date:
            usage_query = usage_query.filter(usage_date__gte=start_date)
        if end_date:
            usage_query = usage_query.filter(usage_date__lte=end_date)

        # Get reel-wise usage statistics
        reel_usage = usage_query.values(
            'reel__id',  # Add reel ID to the query
            'reel__reel_code',
            'reel__reel_type',
            'reel__size_inch'
        ).annotate(
            total_usage=Sum('used_weight'),
            usage_count=Count('id')
        ).order_by('-total_usage')

        # Get all reels for the filter dropdown
        all_reels = Reel.objects.all().order_by('reel_code')

        context.update({
            'reel_usage': reel_usage,
            'all_reels': all_reels,
            'start_date': start_date,
            'end_date': end_date,
        })
        return context