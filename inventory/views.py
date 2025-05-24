from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Q, Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.paginator import Paginator


from .models import Reel, DailyUsage
from .forms import NewReelForm, DailyUsageForm

LOW_STOCK_THRESHOLD = 200  # Define threshold for low stock warning

class CustomLoginView(LoginRequiredMixin, View):
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

@login_required
def inventory_view(request):
    return render(request, 'inventory.html')  # Adjust template name as needed

@login_required
def deepview(request):
    return render(request, 'inventory/reel_list.html')

class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        reels = self.get_queryset().order_by('reel_code')

        if search_query:
            reels = reels.filter(
                Q(reel_code__icontains=search_query) |
                Q(reel_type__icontains=search_query)
            )

        total_reels = reels.count()
        total_stock = reels.aggregate(Sum('current_stock'))['current_stock__sum'] or 0
        low_stock_count = reels.filter(current_stock__lte=LOW_STOCK_THRESHOLD).count()
        avg_stock_per_reel = total_stock / total_reels if total_reels > 0 else 0

        paginator = Paginator(reels, 10)
        page_number = request.GET.get('page')
        reels = paginator.get_page(page_number)

        context = {
            'reels': reels,
            'total_reels': total_reels,
            'total_stock': total_stock,
            'low_stock_count': low_stock_count,
            'avg_stock_per_reel': avg_stock_per_reel,
            'search_query': search_query,
            'new_reel_form': NewReelForm(),
            'daily_usage_form': DailyUsageForm(),
        }

        return render(request, 'inventory/dashboard.html', context)

    def post(self, request, *args, **kwargs):
        if 'submit_new_reel' in request.POST:
            form = NewReelForm(request.POST)
            daily_usage_form = DailyUsageForm()
            if form.is_valid():
                reel_code = form.cleaned_data['reel_code']
                existing_reel = Reel.objects.filter(
                    reel_code=reel_code,
                    reel_type=form.cleaned_data['reel_type'],
                    size_inch=form.cleaned_data['size_inch'],
                    user=request.user
                ).first()

                if existing_reel:
                    existing_reel.current_stock += form.cleaned_data['weight_kg']
                    existing_reel.save()
                    messages.success(request, "Existing reel stock updated successfully.")
                else:
                    reel = form.save(commit=False)
                    reel.user = request.user
                    reel.save()
                    messages.success(request, "New reel added successfully.")
                
                cache.delete('low_stock_warnings')
                return redirect('dashboard')
            else:
                context = {'new_reel_form': form, 'daily_usage_form': daily_usage_form}
                return render(request, 'inventory/dashboard.html', context)

        elif 'submit_daily_usage' in request.POST:
            form = DailyUsageForm(request.POST)
            new_reel_form = NewReelForm()
            if form.is_valid():
                daily_usage = form.save(commit=False)
                if daily_usage.reel.user != request.user:
                    messages.error(request, "You cannot use reels that are not yours.")
                    context = {'new_reel_form': new_reel_form, 'daily_usage_form': form}
                    return render(request, 'inventory/dashboard.html', context)

                if daily_usage.used_weight <= 0 or daily_usage.used_weight > daily_usage.reel.current_stock:
                    messages.error(request, "Used weight must be greater than 0 and not exceed current stock.")
                    context = {'new_reel_form': new_reel_form, 'daily_usage_form': form}
                    return render(request, 'inventory/dashboard.html', context)

                Reel.objects.filter(id=daily_usage.reel.id).update(
                    current_stock=F('current_stock') - Decimal(daily_usage.used_weight)
                )
                daily_usage.user = request.user
                daily_usage.save()
                messages.success(request, "Daily usage logged successfully.")
                cache.delete('low_stock_warnings')
                return redirect('dashboard')
            else:
                context = {'new_reel_form': new_reel_form, 'daily_usage_form': form}
                return render(request, 'inventory/dashboard.html', context)

        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        return Reel.objects.filter(user=self.request.user).order_by('reel_code')

@login_required
def add_reel(request):
    if request.method == 'POST':
        form = NewReelForm(request.POST)
        if form.is_valid():
            reel_code = form.cleaned_data['reel_code']
            existing_reel = Reel.objects.filter(
                reel_code=reel_code,
                reel_type=form.cleaned_data['reel_type'],
                size_inch=form.cleaned_data['size_inch'],
                user=request.user
            ).first()

            if existing_reel:
                existing_reel.current_stock += form.cleaned_data['weight_kg']
                existing_reel.save()
                messages.success(request, "Existing reel stock updated successfully.")
            else:
                reel = form.save(commit=False)
                reel.user = request.user
                reel.save()
                messages.success(request, "New reel added successfully.")
            
            cache.delete('low_stock_warnings')
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NewReelForm()

    return render(request, 'inventory/add_reel.html', {'form': form})

@login_required
def add_daily_usage(request):
    if request.method == 'POST':
        form = DailyUsageForm(request.POST)
        if form.is_valid():
            daily_usage = form.save(commit=False)
            if daily_usage.reel.user != request.user:
                messages.error(request, "You cannot log usage for reels not owned by you.")
                return redirect('dashboard')

            if daily_usage.used_weight <= 0 or daily_usage.used_weight > daily_usage.reel.current_stock:
                messages.error(request, "Used weight must be greater than 0 and not exceed current stock.")
                return redirect('dashboard')

            Reel.objects.filter(id=daily_usage.reel.id).update(
                current_stock=F('current_stock') - Decimal(daily_usage.used_weight)
            )
            daily_usage.user = request.user
            daily_usage.save()
            messages.success(request, "Daily usage logged successfully.")
            cache.delete('low_stock_warnings')
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DailyUsageForm()

    return render(request, 'inventory/add_daily_usage.html', {'form': form})

@login_required
def delete_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk, user=request.user)
    reel.delete()
    messages.success(request, f"Reel {reel.reel_code} has been deleted successfully.")
    return redirect('dashboard')

@login_required
def edit_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk, user=request.user)
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

class ReelReportView(LoginRequiredMixin, DetailView):
    model = Reel
    template_name = 'inventory/reel_report.html'
    context_object_name = 'reel'

    def get_queryset(self):
        return Reel.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reel = self.get_object()

        usage_history = DailyUsage.objects.filter(reel=reel, user=self.request.user).order_by('-usage_date')
        total_usage = DailyUsage.objects.filter(reel=reel, user=self.request.user).aggregate(Sum('used_weight'))['used_weight__sum'] or 0

        monthly_usage = DailyUsage.objects.filter(reel=reel, user=self.request.user).annotate(
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

class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        reels = Reel.objects.filter(user=self.request.user)
        usage = DailyUsage.objects.filter(user=self.request.user)

        # Usage by month/year
        monthly_usage = usage.annotate(
            year=ExtractYear('usage_date'),
            month=ExtractMonth('usage_date')
        ).values('year', 'month').annotate(
            total_usage=Sum('used_weight')
        ).order_by('-year', '-month')

        # Reels by type
        reels_by_type = reels.values('reel_type').annotate(
            count=Count('id'),
            total_stock=Sum('current_stock')
        ).order_by('reel_type')

        context.update({
            'monthly_usage': monthly_usage,
            'reels_by_type': reels_by_type,
        })
        return context
