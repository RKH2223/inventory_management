from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reel, DailyUsage, CustomUser
from .forms import NewReelForm, DailyUsageForm
from django.db.models import F, Q, Sum, Count
from decimal import Decimal
from django.core.cache import cache
from django.views.generic import ListView, DetailView, TemplateView, View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models.functions import ExtractYear, ExtractMonth
from datetime import datetime
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages

LOW_STOCK_THRESHOLD = 200

# Custom login view without Django auth
class CustomLoginView(View):
    def get(self, request):
        # Clear any existing session data
        if 'user_id' in request.session:
            del request.session['user_id']
            del request.session['username']
        return render(request, 'inventory/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username)
            if user.check_password(password):
                # Store user info in session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Incorrect password.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")

        return render(request, 'inventory/login.html')




def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
        
            user = form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'inventory/register.html', {'form': form})




def logout_view(request):
    # Clear specific session variables
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    
    # Flush the entire session
    request.session.flush()
    
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# Replace @login_required and LoginRequiredMixin manually by checking session

def inventory_view(request):
    if not request.session.get('user_id'):
        return redirect('login')
    return render(request, 'inventory.html')


def deepview(request):
    if not request.session.get('user_id'):
        return redirect('login')
    return render(request, 'inventory/reel_list.html')


# Example for the dashboard view
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        # Filter reels by the logged-in user
        reels = Reel.objects.filter(user_id=user_id).order_by('reel_code')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string(
                'inventory/reel_list.html',
                {'reels': self.get_queryset()},
                request=request
            )
            return JsonResponse({'html': html})

        search_query = request.GET.get('search', '')
        reels = Reel.objects.filter(user_id=user_id).order_by('reel_code')  # filter by logged-in user

        if search_query:
            reels = reels.filter(
                Q(reel_code__icontains=search_query) |
                Q(reel_type__icontains=search_query)
            )

        total_reels = reels.count()
        total_stock = reels.aggregate(Sum('current_stock'))['current_stock__sum'] or 0
        low_stock_count = reels.filter(current_stock__lte=LOW_STOCK_THRESHOLD).count()
        avg_stock_per_reel = total_stock / total_reels if total_reels > 0 else 0

        from django.core.paginator import Paginator
        paginator = Paginator(reels, 5)
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
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        if 'submit_new_reel' in request.POST:
            form = NewReelForm(request.POST)
            if form.is_valid():
                reel_code = form.cleaned_data['reel_code']
                existing_reel = Reel.objects.filter(
                    user_id=user_id,
                    reel_code=reel_code,
                    reel_type=form.cleaned_data['reel_type'],
                    size_inch=form.cleaned_data['size_inch']
                ).first()

                if existing_reel:
                    existing_reel.current_stock += form.cleaned_data['weight_kg']
                    existing_reel.save()
                    messages.success(request, "Existing reel stock updated successfully.")
                else:
                    new_reel = form.save(commit=False)
                    new_reel.user_id = user_id
                    new_reel.save()
                    messages.success(request, "New reel added successfully.")

                cache.delete('low_stock_warnings')
                return redirect('dashboard')
            else:
                messages.error(request, "Please correct the errors below.")

        elif 'submit_daily_usage' in request.POST:
            form = DailyUsageForm(request.POST)
            if form.is_valid():
                daily_usage = form.save(commit=False)
                daily_usage.user_id = user_id

                if daily_usage.reel and daily_usage.used_weight:
                    if daily_usage.reel.current_stock >= daily_usage.used_weight:
                        Reel.objects.filter(id=daily_usage.reel.id).update(
                            current_stock=F('current_stock') - Decimal(daily_usage.used_weight)
                        )
                        daily_usage.save()
                        messages.success(request, "Daily usage logged successfully.")
                        cache.delete('low_stock_warnings')
                    else:
                        messages.error(request, "Not enough stock available.")
                return redirect('dashboard')
            else:
                messages.error(request, "Please correct the errors below.")

        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        return Reel.objects.filter(user_id=user_id).order_by('reel_code')


def add_reel(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        form = NewReelForm(request.POST)
        if form.is_valid():
            reel_code = form.cleaned_data['reel_code']
            existing_reel = Reel.objects.filter(
                user_id=user_id,
                reel_code=reel_code,
                reel_type=form.cleaned_data['reel_type'],
                size_inch=form.cleaned_data['size_inch']
            ).first()

            if existing_reel:
                existing_reel.current_stock += form.cleaned_data['weight_kg']
                existing_reel.save()
                messages.success(request, "Existing reel stock updated successfully.")
            else:
                new_reel = form.save(commit=False)
                new_reel.user_id = user_id
                new_reel.save()
                messages.success(request, "New reel added successfully.")

            cache.delete('low_stock_warnings')
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NewReelForm()

    return render(request, 'inventory/add_reel.html', {'form': form})


def add_daily_usage(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = DailyUsageForm(request.POST, user=user)
        if form.is_valid():
            daily_usage = form.save(commit=False)
            daily_usage.user_id = user_id

            if daily_usage.reel and daily_usage.used_weight:
                if daily_usage.reel.current_stock >= daily_usage.used_weight:
                    Reel.objects.filter(id=daily_usage.reel.id).update(
                        current_stock=F('current_stock') - Decimal(daily_usage.used_weight)
                    )
                    daily_usage.save()
                    messages.success(request, "Daily usage logged successfully.")
                    cache.delete('low_stock_warnings')
                else:
                    messages.error(request, "Not enough stock available.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DailyUsageForm(user=user)

    return render(request, 'inventory/add_daily_usage.html', {'form': form})


def delete_reel(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    reel = get_object_or_404(Reel, pk=pk, user_id=user_id)
    reel.delete()
    messages.success(request, f"Reel {reel.reel_code} has been deleted successfully.")
    return redirect('dashboard')


def edit_reel(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    reel = get_object_or_404(Reel, pk=pk, user_id=user_id)
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


class ReelReportView(TemplateView):
    template_name = 'inventory/reel_report.html'

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        reel = get_object_or_404(Reel, pk=kwargs.get('pk'), user_id=user_id)

        # Filter usage history by both reel and user_id
        usage_history = DailyUsage.objects.filter(reel=reel, user_id=user_id).order_by('-usage_date')
        total_usage = usage_history.aggregate(Sum('used_weight'))['used_weight__sum'] or 0

        context = {
            'reel': reel,
            'usage_history': usage_history,
            'total_usage': total_usage,
        }
        return render(request, self.template_name, context)


class ReportsView(TemplateView):
    template_name = 'inventory/reports.html'

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        reels = Reel.objects.filter(user_id=user_id)
        total_stock = reels.aggregate(Sum('current_stock'))['current_stock__sum'] or 0
        total_reels = reels.count()
        low_stock_count = reels.filter(current_stock__lte=LOW_STOCK_THRESHOLD).count()
        avg_stock = total_stock / total_reels if total_reels else 0

        # Date range filters
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        usage_data = DailyUsage.objects.filter(user_id=user_id)
        
        # Apply date filters if provided
        if start_date:
            usage_data = usage_data.filter(usage_date__gte=start_date)
        if end_date:
            usage_data = usage_data.filter(usage_date__lte=end_date)

        # Calculate monthly usage
        monthly_usage = usage_data.values('usage_date__year', 'usage_date__month').annotate(
            total_used=Sum('used_weight'),
            reel_count=Count('reel', distinct=True)
        ).order_by('usage_date__year', 'usage_date__month')

        # Calculate reel usage statistics
        reel_usage = usage_data.values(
            'reel__id', 'reel__reel_code', 'reel__reel_type', 'reel__size_inch'
        ).annotate(
            total_usage=Sum('used_weight'),
            usage_count=Count('id')
        ).order_by('-total_usage')

        context = {
            'total_stock': total_stock,
            'total_reels': total_reels,
            'low_stock_count': low_stock_count,
            'avg_stock': avg_stock,
            'monthly_usage': monthly_usage,
            'reel_usage': reel_usage,
            'start_date': start_date,
            'end_date': end_date,
        }
        return render(request, self.template_name, context)


def delete_daily_usage(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    usage = get_object_or_404(DailyUsage, pk=pk, user_id=user_id)
    reel = usage.reel
    used_weight = usage.used_weight
    
    # Add the used weight back to the reel's current stock
    reel.current_stock += used_weight
    reel.save()
    
    # Delete the usage entry
    usage.delete()
    
    messages.success(request, f"Usage entry of {used_weight}kg has been deleted and stock updated.")
    return redirect('reel_report', pk=reel.pk)
