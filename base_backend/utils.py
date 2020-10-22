import random
import secrets
from functools import wraps

from json import JSONDecodeError

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, Func
from django.shortcuts import get_object_or_404

from base_backend import get_password_reset_table, get_otp_verification_table


# from restaurant.settings import EMAIL_HOST_USER


def generate_token(length=32):
    """
    generates a token with the specified length (default 32), this is being used as access token
    :return:
    """
    return secrets.token_hex(length)


def generate_random_code():
    """
    generates a 5 characters random code, this is being used as OTP
    :return:
    """
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    random_alphabet = random.choice(alphabet)
    randoms = [random_alphabet]
    for i in range(4):
        randoms.append(str(random.randint(0, 9)))

    code = ''.join(randoms)

    return code


def generate_random_password():
    password = ''
    for i in range(3):
        password += generate_random_code()

    return password


# def phone_sms_verification(phone):
#     """
#     creates a tuple of a random code (OTP) and a phone number, to verify the phone number provided by a user
#     :param phone: phone number provided by the user
#     :return:
#     """
#     code = generate_random_code()
#     sms = get_otp_verification_table().objects.filter(otp_code=code)
#
#     while sms.exists():
#         code = generate_random_code()
#         sms = get_otp_verification_table().objects.filter(otp_code=code)
#
#     get_otp_verification_table().objects.create(otp_code=code, number=phone)
#     message = "use this code: {0}, to confirm your {1} account phone number.".format(code, settings.APP_NAME)
#     send_sms(phone, message)
#
#
# def phone_reconfirmation(phone: get_otp_verification_table()):
#     message = "use this code: {0}, to confirm your {1} account phone number.".format(phone.otp_code, settings.APP_NAME)
#     send_sms(phone.number, message)


def send_sms(phone, message):
    """
    send an sms containing the message parameter to the phone parameter
    :param phone: the target phone
    :param message: the message to be sent
    :return:
    """
    try:
        param = {
            "apikey": '8b882e50-37e0-4b27-abef-bc6a9b661753',
            "clientid": 'c7911336-5c4c-4309-b5a9-d2f160c62b5f',
            "msisdn": phone,
            "sid": 'SKYLIGHT-DS',
            "msg": message,
            "fl": 0
        }

        url = "https://my.forwardvaluesms.com/vendorsms/pushsms.aspx"
        response = requests.get(url, params=param)
    except requests.exceptions.RequestException as e:
        print("Exception Occur: %s" % e)
        raise e.args

    try:
        print(response.json())
    except JSONDecodeError:
        print(response.content)


def check_balance():
    """
    checks the balance of the OTP account
    :return:
    """
    payload = {'clientid': 'c7911336-5c4c-4309-b5a9-d2f160c62b5f',
               'apikey': '8b882e50-37e0-4b27-abef-bc6a9b661753'}
    r = requests.get('http://www.dubaimirchi.com/API/Balance.aspx',
                     params=payload)
    print(r.url)
    print(r.content)


# def reset_user_password(token, attr, password):
#     """
#     resets the user password, after checking the reset credentials(phone,token) from the PasswordReset table
#     and verifying that the PasswordReset instance has not been used (verified over OTP).
#     :param token: the ResetPassword instance token credential
#     :param attr: the users phone number provided also in the PasswordReset
#     :param password: the new password
#     :return: True if the password
#     """
#     password_reset = get_object_or_404(get_password_reset_table(), Q(Q(phone=attr) | Q(email=attr)), token=token)
#     if not password_reset.used:
#         password_reset.used = True
#         password_reset.save()
#         user = get_object_or_404(get_user_model(), Q(Q(phone=attr) | Q(email=attr)))
#         user.set_password(password)
#         user.save()
#         return True
#     else:
#         return False


# def verify_sms_code_for_password_reset(code, token):
#     """
#     verifies OTP code from PasswordReset table, and set it as used if it exists
#     :param code: OTP
#     :param token: token provided to the user
#     :return: raises Http404 if the credentials don't exist or already used, else returns true
#     """
#     get_object_or_404(get_password_reset_table(), code=code, token=token, used=False)
#     return True


def verify_sms_code_for_phone_confirmation(code: str):
    """
    verifies if the code provided belongs to an sms verification operation
    :param code:
    :return:
    """
    verification = get_otp_verification_table().objects.filter(otp_code=code)
    if verification.exists():
        verification = verification.first()
        verification.confirmed = True
        verification.save()
        return True, verification.number
    return False, False


def activate_user_over_otp(code):
    """
    verifies the provided code if it belongs to account confirmation OTP then activates the user
    :param code:
    :return:
    """
    status, response = verify_sms_code_for_phone_confirmation(code)
    if status:
        user = get_user_model().objects.filter(phone=response)
        the_user = user.first()
        the_user.is_active = True
        the_user.save()
        return True
    return False


def set_notification_token(user, token):
    user.notifications_token = token
    user.save()
    return {'status': True,
            'message': 'Success'}


def api_login_required_factory():
    def decorator(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            request = args[0]
            if request and request.headers.get('authorization') is not None:
                user = get_user_model().objects.filter(access_token=request.headers.get('authorization'))
                if user.exists():
                    return function(*args, **kwargs)
            raise PermissionDenied

        return wrapped_function

    return decorator


def api_errors_extractor(form_errors):
    if form_errors:
        list_keys = list(form_errors.keys())
        list_values = list(form_errors.values())
        values = []
        for value in list_values:
            for value1 in value:
                values.append(value1)
        return list(zip(list_keys, values))


def handle_uploaded_file(file, directory):
    with open(directory, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def send_email(subject: str, email: str, message: str) -> int:
    return send_mail(
        subject=subject,
        message=message,
        # from_email=EMAIL_HOST_USER,
        recipient_list=email if isinstance(email, list) else [email]
    )


def get_current_week():
    from datetime import date
    return date.today().isocalendar()[1]


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
