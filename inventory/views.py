# from django.shortcuts import render
from django.contrib import messages
from .models import Reel
from .forms import NewReelForm, DailyUsageForm
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect






LOW_STOCK_THRESHOLD = 10.0


def inventory_view(request):
    # Your logic to fetch and display inventory
    return render(request, 'inventory.html')  # Change 'inventory.html' to your template file

def dashboard(request):
    reels = Reel.objects.all()
    low_stock_reels = reels.filter(current_stock__lte=LOW_STOCK_THRESHOLD)
    
    if low_stock_reels.exists():
        message_text = "Warning: The following reels have low stock: " + \
                       ", ".join([f"{reel.reel_code} ({reel.current_stock} kg)" for reel in low_stock_reels])
        messages.warning(request, message_text)
    
    if request.method == 'POST':
        # Determine which form is being submitted by checking a hidden field or button name.
        if 'submit_new_reel' in request.POST:
            new_reel_form = NewReelForm(request.POST)
            if new_reel_form.is_valid():
                new_reel_form.save()
                messages.success(request, "New reel added successfully.")
                return redirect('dashboard')
            daily_usage_form = DailyUsageForm()  # Empty form for daily usage
        elif 'submit_daily_usage' in request.POST:
            daily_usage_form = DailyUsageForm(request.POST)
            if daily_usage_form.is_valid():
                daily_usage_form.save()
                messages.success(request, "Daily usage logged successfully.")
                return redirect('dashboard')
            new_reel_form = NewReelForm()  # Empty form for new reel
    else:
        new_reel_form = NewReelForm()
        daily_usage_form = DailyUsageForm()
    
    context = {
        'reels': reels,
        'new_reel_form': new_reel_form,
        'daily_usage_form': daily_usage_form,
    }
    return render(request, 'inventory/dashboard.html', context)



def add_reel(request):
    if request.method == 'POST':
        form = NewReelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New reel added successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "There was an error adding the reel.")
    else:
        form = NewReelForm()
    return render(request, 'inventory/add_reel.html', {'form': form})

def add_daily_usage(request):
    if request.method == 'POST':
        form = DailyUsageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Daily usage logged successfully.")
            return redirect('dashboard')  # Redirect as needed
        else:
            messages.error(request, "There was an error logging daily usage.")
    else:
        form = DailyUsageForm()
    return render(request, 'inventory/add_daily_usage.html', {'form': form})




def delete_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    reel.delete()
    messages.success(request, f"Reel {reel.reel_code} has been deleted successfully.")
    return redirect('dashboard')


# Create your views here.
