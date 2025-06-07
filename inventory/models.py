# Add this import at the top
import hashlib

from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password_hash = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        return self.password_hash == hashlib.sha256(raw_password.encode()).hexdigest()

    def __str__(self):
        return self.username
    
class Reel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    REEL_TYPE_CHOICES = [
        ('natural','Natural'),
        ('golden','Golden'),
    ]
    
    reel_code = models.CharField(max_length=50, help_text="Code for this reel")
    reel_type = models.CharField(max_length=20, choices=REEL_TYPE_CHOICES, help_text="Type of reel: Natural or Golden")
    size_inch = models.DecimalField(max_digits=5, decimal_places=2, help_text="Size in inch (e.g., 26.00 to 52.00)")
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight of the reel in kg")
    current_stock = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), editable=True, help_text="Current stock available in kg"
    )
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['reel_code']

    def __str__(self):
        return f"{self.reel_code} - {self.reel_type} ({self.size_inch} inch)"
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        
        # Set current_stock = weight_kg only if this is a new instance (no pk yet)
        if not self.pk:
            self.current_stock = self.weight_kg

        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        
class DailyUsage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    used_weight = models.DecimalField(max_digits=10, decimal_places=2)
    usage_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-usage_date']

    def __str__(self):
        return f"{self.reel.reel_code} - {self.used_weight}kg on {self.usage_date}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only reduce stock on first save
            if self.reel and self.used_weight:
                self.reel.current_stock -= self.used_weight
                self.reel.save()
        super().save(*args, **kwargs)