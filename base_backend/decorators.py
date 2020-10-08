from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def super_user_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='admin:login'):
    actual_decorator = user_passes_test(lambda u: u.is_active and u.is_superuser,
                                        login_url=login_url,
                                        redirect_field_name=redirect_field_name)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
