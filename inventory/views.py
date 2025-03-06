from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reel
from .forms import NewReelForm, DailyUsageForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewReelForm
from .models import Reel
from django.shortcuts import render, redirect
from .models import Reel
from .forms import NewReelForm
from django.contrib import messages
from django.db.models import F
from decimal import Decimal  # Import Decimal
from django.db.models import Q



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


def dashboard(request):
    reels_list = Reel.objects.all()
    
    query = request.GET.get('q')  # Get search term from URL query parameters
    if query:
        try:
            reels = Reel.objects.filter(reel_code__icontains=query) if query else []
            if not reels:
                reels = Reel.objects.all()
                messages.warning(request, "No matches found in database.")

        except Exception as e:
            print("some issues in Database during the fetching the data.", e)
    else:
        reels = Reel.objects.all()

    # Pagination: Show 7 reels per page
    paginator = Paginator(reels, 7)  
    page_number = request.GET.get('page')
    reels = paginator.get_page(page_number)  # Get the reels for the current page

    low_stock_reels = reels_list.filter(current_stock__lte=LOW_STOCK_THRESHOLD)
    if low_stock_reels.exists():
        message_text = "Warning: The following reels have low stock: " + \
                       ", ".join([f"{reel.reel_code} ({reel.current_stock} kg)" for reel in low_stock_reels])
        messages.warning(request, message_text)

    if request.method == 'POST':
        if 'submit_new_reel' in request.POST:
            form = NewReelForm(request.POST)
            if form.is_valid():
                reel_code = form.cleaned_data['reel_code']
                weight_kg = form.cleaned_data['weight_kg']

                # Find existing reel with the same code, type, and size
                existing_reel = Reel.objects.filter(
                    reel_code=reel_code,
                    reel_type=form.cleaned_data['reel_type'],
                    reel_GSM =form.cleaned_data['reel_GSM'],
                    size_inch=form.cleaned_data['size_inch']
                ).first()

                if existing_reel:
                    existing_reel.current_stock += weight_kg  # Update existing stock
                    existing_reel.save()
                    messages.success(request, "Existing reel stock updated successfully.")
                else:
                    form.save()  # Create new reel
                    messages.success(request, "New reel added successfully.")

                return redirect('dashboard')
            
        elif 'submit_daily_usage' in request.POST:
            daily_usage_form = DailyUsageForm(request.POST)
            if daily_usage_form.is_valid():
                daily_usage_form.save()
                messages.success(request, "Daily usage logged successfully.")
                return redirect('dashboard')
    else:
        form = NewReelForm()
        daily_usage_form = DailyUsageForm()

    context = {
        # 'searched_reels': searched_reels,
        'reels': reels,  # Paginated reels
        'new_reel_form': form,
        'daily_usage_form': daily_usage_form,
        # 'search_query': search_query,
    }
    return render(request, 'inventory/dashboard.html', context)


# def dashboard(request):
#     reels = Reel.objects.all()
#     low_stock_reels = reels.filter(current_stock__lte=LOW_STOCK_THRESHOLD)

#     if low_stock_reels.exists():
#         message_text = "Warning: The following reels have low stock: " + \
#                        ", ".join([f"{reel.reel_code} ({reel.current_stock} kg)" for reel in low_stock_reels])
#         messages.warning(request, message_text)

#     if request.method == 'POST':
#         if 'submit_new_reel' in request.POST:
#             form = NewReelForm(request.POST)
#             if form.is_valid():
#                 reel_code = form.cleaned_data['reel_code']
#                 weight_kg = form.cleaned_data['weight_kg']

#                 reel, created = Reel.objects.get_or_create(
#                     reel_code=reel_code,
#                     defaults=form.cleaned_data  # If new, use form data
#                 )

#                 if not created:
#                     reel.current_stock += weight_kg  # Update existing stock
#                     reel.save()
                
#                 messages.success(request, "Reel added or updated successfully.")
#                 return redirect('dashboard')
            
#         elif 'submit_daily_usage' in request.POST:
#             daily_usage_form = DailyUsageForm(request.POST)
#             if daily_usage_form.is_valid():
#                 daily_usage_form.save()


#                 messages.success(request, "Daily usage logged successfully.")
#                 return redirect('dashboard')

#     else:
#         form = NewReelForm()
#         daily_usage_form = DailyUsageForm()

#     context = {
#         'reels': reels,
#         'new_reel_form': form,
#         'daily_usage_form': daily_usage_form,
#     }
#     return render(request, 'inventory/dashboard.html', context)

def add_reel(request):
    if request.method == 'POST':
        form = NewReelForm(request.POST)
        if form.is_valid():
            reel_code = form.cleaned_data['reel_code']
            reel_type = form.cleaned_data['reel_type']
            # reel_GSM = form.cleaned_data['reel_GSM']
            size_inch = form.cleaned_data['size_inch']
            new_weight = form.cleaned_data['weight_kg']

            # Debugging: Print values
            print(f"Adding reel: {reel_code}, {reel_type}, {size_inch}, {new_weight} kg")

            # Check if a reel with the same specs already exists
            existing_reel = Reel.objects.filter(
                reel_code=reel_code, 
                reel_type=reel_type, 
                # reel_GSM=reel_GSM,
                size_inch=size_inch
            ).first()

            if existing_reel:
                print(f"Existing reel found: {existing_reel.reel_code} | Current Stock: {existing_reel.current_stock} kg")

                # Add new weight to existing stock
                try:
                    existing_reel.current_stock += Decimal(new_weight)
                    existing_reel.save(update_fields=['current_stock'])
                    existing_reel.refresh_from_db()
                except:
                    print("not updated")

                print(f"Updated Stock: {existing_reel.current_stock} kg")
                messages.success(request, "Reel stock updated successfully.")
            else:
                # Create a new reel entry
                form.save()
                messages.success(request, "New reel added successfully.")

            return redirect('dashboard')
    
    else:
        form = NewReelForm()

    return render(request, 'inventory/add_reel.html', {'form': form})


def add_daily_usage(request):
    if request.method == 'POST':
        form = DailyUsageForm(request.POST)
        if form.is_valid():
            daily_usage = form.save(commit=False)  # Don't save yet

            if daily_usage.reel and daily_usage.used_weight:  # Ensure reel exists
                if daily_usage.reel.current_stock >= daily_usage.used_weight:
                    

                    Reel.objects.filter(id=daily_usage.reel.id).update(
                        current_stock=F('current_stock') - Decimal(daily_usage.used_weight)
                    )

                    messages.success(request, "Daily usage logged successfully.")
                    print('Daily usage updated: ', daily_usage.reel.current_stock)
                else:
                    messages.error(request, "Not enough stock available.")
            else:
                messages.error(request, "Invalid reel selection.")
            return redirect('dashboard')  
    else:
        form = DailyUsageForm()

    return render(request, 'inventory/add_daily_usage.html', {'form': form})

def delete_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    reel.delete()
    messages.success(request, f"Reel {reel.reel_code} has been deleted successfully.")
    return redirect('dashboard')