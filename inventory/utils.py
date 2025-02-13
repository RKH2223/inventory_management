# inventory/utils.py
from twilio.rest import Client
from django.conf import settings

def send_sms_alert(message, to_phone_number):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone = settings.TWILIO_PHONE_NUMBER

    client = Client(account_sid, auth_token)
    
    try:
        sms = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone_number
        )
        print("SMS sent successfully, SID:", sms.sid)
        return sms.sid
    except Exception as e:
        print("Error sending SMS:", e)
        return None
