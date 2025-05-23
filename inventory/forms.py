from django import forms
from .models import Reel, DailyUsage

from django.contrib.auth.forms import AuthenticationForm # We'll still use this as a base for simplicity


class NewReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ['reel_code', 'reel_type', 'size_inch', 'weight_kg']
        widgets = {
            'reel_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter reel code'
            }),
            'reel_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'size_inch': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter size in inches',
                'step': '0.01',
                'min': '26.00',
                'max': '52.00'
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter weight in kg',
                'step': '0.01',
                'min': '0'
            })
        }

    def clean_size_inch(self):
        size = self.cleaned_data['size_inch']
        if size < 26.00 or size > 52.00:
            raise forms.ValidationError("Size must be between 26.00 and 52.00 inches")
        return size

    def clean_weight_kg(self):
        weight = self.cleaned_data['weight_kg']
        if weight <= 0:
            raise forms.ValidationError("Weight must be greater than 0")
        return weight

class DailyUsageForm(forms.ModelForm):
    class Meta:
        model = DailyUsage
        fields = ['reel', 'used_weight', 'usage_date', 'remarks']
        widgets = {
            'reel': forms.Select(attrs={
                'class': 'form-control'
            }),
            'used_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter used weight in kg',
                'step': '0.01',
                'min': '0'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter any remarks (optional)',
                'rows': '3'
            }),
            'usage_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Added class for consistency
        }
        labels = { # Good to have these explicitly for better control
            'reel': 'Select Reel',
            'used_weight': 'Used Weight (Kg)',
            'usage_date': 'Usage Date',
            'remarks': 'Remarks (Optional)',
        }


    # --- ADD THIS __init__ METHOD HERE ---
    def __init__(self, *args, **kwargs):
        # Extract the 'user' object passed from the view, if it exists
        user = kwargs.pop('user', None)
        # Call the parent class's __init__ method
        super().__init__(*args, **kwargs)

        # If a user object was provided, filter the queryset for the 'reel' field
        if user:
            self.fields['reel'].queryset = Reel.objects.filter(user=user).order_by('reel_code')
        else:
            # If no user is provided, or for safety, ensure no reels are displayed
            self.fields['reel'].queryset = Reel.objects.none()

    def clean_used_weight(self):
        used_weight = self.cleaned_data['used_weight']
        reel = self.cleaned_data.get('reel')
        
        if reel and used_weight > reel.current_stock:
            raise forms.ValidationError(
                f"Used weight cannot exceed current stock ({reel.current_stock} kg)"
            )
        
        if used_weight <= 0:
            raise forms.ValidationError("Used weight must be greater than 0")
            
        return used_weight

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    # You can add custom validation or fields here if needed
    # For example, to ensure it doesn't show "This field is required" error directly for username/password:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = False
        self.fields['password'].label = False