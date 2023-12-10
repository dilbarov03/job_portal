import random
import math
import requests
import string
import random
import re
from django.conf import settings
from django.core.mail import send_mail


def generate_confirmation_code() -> str:
    """Random code generator with 6 digit"""
    code = random.randint(100000, 999999)
    return code


def get_request_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_randon_string(length=32):
    characters = string.ascii_letters + string.digits
    size = len(characters)
    random_string = ""
    for _ in range(length):
        random_string = random_string + characters[random.randint(0, size - 1)]
    return random_string


def send_sms(phone, message) -> requests.Response:    
    url = settings.SMS_URL
    data = {
        'mobile_phone': phone,  # Replace with the phone number
        'message': message  # Replace with your message
    }
    headers = {
        'Authorization': f'Bearer {settings.SMS_TOKEN}',
    }

    response = requests.post(url, data=data, headers=headers)
    print(phone)

    if response.status_code == 200:
        # print('SMS sent successfully.')
        print(response.json())
    else:
        print('Failed to send SMS. Status code:', response.status_code)
        print('Response content:', response.text)
    return response





def get_mobile_identifier(request):
    return request.headers.get(settings.MobileDeviceIdentifierHeader, None)


def get_user_identifier(request):
    return request.headers.get(settings.VIEW_COUNT_HEADER, None)


def send_email(email, subject, message):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject=subject, message=message, html_message=message,
              from_email=email_from, recipient_list=recipient_list)