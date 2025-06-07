# inventory/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DailyUsage, Reel

LOW_STOCK_THRESHOLD = 10.0
# Ensure this is different from your Twilio phone number
ALERT_PHONE_NUMBER = '+919426998061'  # Replace with a verified, different number

def check_low_stock(sender, instance, created, **kwargs):
    if created:
        reel = instance.reel
        if reel.current_stock <= LOW_STOCK_THRESHOLD:
            message = f"Alert: Stock for reel {reel.reel_code} is low. Current stock: {reel.current_stock} kg."
            print("Sending SMS alert:", message)
            sms_sid = send_sms_alert(message, ALERT_PHONE_NUMBER)
            print("SMS SID:", sms_sid)
