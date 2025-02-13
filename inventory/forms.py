from django import forms
from .models import Reel, DailyUsage

class NewReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ['reel_code', 'reel_type', 'size_mm', 'weight_kg', 'current_stock']

class DailyUsageForm(forms.ModelForm):
    class Meta:
        model = DailyUsage
        fields = ['reel', 'used_weight', 'remarks']
