from django.db import models
from django.contrib.auth.models import User

# Model representing a paper reel in your inventory
class Reel(models.Model):
    REEL_TYPE_CHOICES = [
        ('natural', 'Natural'),
        ('golden', 'Golden'),
    ]
    
    reel_code = models.CharField(max_length=100, unique=True, help_text="Unique code for this reel")
    reel_type = models.CharField(max_length=10, choices=REEL_TYPE_CHOICES, help_text="Type of reel: Natural or Golden")
    size_mm = models.DecimalField(max_digits=5, decimal_places=2, help_text="Size in mm (e.g., 26.00 to 52.00)")
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight of the reel in kg")
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Current stock available in kg")
    
    def __str__(self):
        return f"{self.reel_code} ({self.reel_type})"

# Model representing a daily usage entry for a reel
class DailyUsage(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name="usages")
    used_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight used in kg")
    usage_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Usage for {self.reel.reel_code} on {self.usage_date}"
    
    # Override save method to update reel's stock when new usage is recorded
    def save(self, *args, **kwargs):
        # Only update the stock when creating a new record (not on updates)
        if not self.pk:
            self.reel.current_stock -= self.used_weight
            self.reel.save()
        super().save(*args, **kwargs)

# Create your models here.
