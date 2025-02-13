# test_sms.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_system.settings")

from inventory.utils import send_sms_alert

test_message = "Test SMS from Django Twilio integration!"
test_phone = '+919537308502'  # Replace with your recipient number

send_sms_alert(test_message, test_phone)
