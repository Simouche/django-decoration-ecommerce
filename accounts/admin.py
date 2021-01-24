from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.models import Permission

from base_backend.admin import register_app_models
from . import signals

register_app_models("accounts")
try:
    admin.site.register(Permission)
except AlreadyRegistered:
    pass
