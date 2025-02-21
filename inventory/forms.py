
from django import forms
from .models import Reel, DailyUsage

class NewReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ['reel_code', 'reel_type', 'size_inch', 'weight_kg']  # Removed current_stock (auto-calculated)

class DailyUsageForm(forms.ModelForm):
    class Meta:
        model = DailyUsage
        fields = ['reel', 'used_weight', 'remarks']
