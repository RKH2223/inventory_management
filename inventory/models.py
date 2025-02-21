from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Reel(models.Model):
    REEL_TYPE_CHOICES = [
        ('natural', 'Natural'),
        ('golden', 'Golden'),
    ]
    
    reel_code = models.CharField(max_length=100, help_text="Code for this reel")
    reel_type = models.CharField(max_length=10, choices=REEL_TYPE_CHOICES, help_text="Type of reel: Natural or Golden")
    # reel_GSM =  models.DecimalField(max_digits=5,decimal_places=2,null=True,help_text="enter the GSM of paper ")
    size_inch = models.DecimalField(max_digits=5, decimal_places=2, help_text="Size in inch (e.g., 26.00 to 52.00)")
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight of the reel in kg")
    current_stock = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), editable=True, help_text="Current stock available in kg"
    )

    def __str__(self):
        return self.reel_code
    
    def save(self, *args, **kwargs):
        # Avoid calling save again for existing reels
        if not self.pk:  # Only set initial stock for new reels (not existing ones)
            self.current_stock = self.weight_kg
            
        super().save(*args, **kwargs)  # Create new reel
        


class DailyUsage(models.Model): 
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name="usages")
    # GSM = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name="gsm_reels")
    used_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight used in kg")
    usage_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Usage for {self.reel.reel_code} on {self.usage_date}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only reduce stock on first save
            if self.reel and self.used_weight:
                self.reel.current_stock -= self.used_weight
                self.reel.save()
        super().save(*args, **kwargs)