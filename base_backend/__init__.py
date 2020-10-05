from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


def get_password_reset_table():
    """
    Return the Password Reset model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.PASSWORD_RESET_TABLE, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("PHONE_VERIFICATION_OTP_TABLE must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "PHONE_VERIFICATION_OTP_TABLE refers to model '%s' that has not been installed"
            % settings.PASSWORD_RESET_TABLE)


def get_otp_verification_table():
    """
    Return the OTP Verification model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.PHONE_VERIFICATION_OTP_TABLE, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("PHONE_VERIFICATION_OTP_TABLE must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "PHONE_VERIFICATION_OTP_TABLE refers to model '%s' that has not been installed"
            % settings.PHONE_VERIFICATION_OTP_TABLE)
