from datetime import date

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

from base_backend import _
from base_backend.models import do_nothing, DeletableModel, BaseModel
from base_backend.validators import phone_validator


# Create your models here.

class User(AbstractUser):
    USER_TYPES = (('C', _('Client')), ('S', _('Staff')), ('A', _('Admin')))

    notification_token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    phones = ArrayField(base_field=models.CharField(
        _("Phone Number"),
        max_length=50,
        validators=[phone_validator],
        unique=True,
    ))
    is_active = models.BooleanField(
        _('Active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    user_type = models.CharField(
        _("Type"),
        max_length=1,
        choices=USER_TYPES,
        help_text=_("The user's type can be one of the available choices, "
                    "Client, Staff or Admin."),
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", 'user_type', 'phones', 'email']

    @property
    def full_name(self):
        return super().get_full_name()

    @property
    def get_age(self) -> int:
        today = date.today()
        dob = self.birth_date
        before_dob = (today.month, today.day) < (dob.month, dob.day)
        return today.year - self.birth_date.year - before_dob

    @property
    def confirmed_phone(self) -> bool:
        return False

    @property
    def confirmed_email(self) -> bool:
        return False

    @property
    def get_photo(self):
        try:
            return self.photo.url
        except ValueError:
            return ""

    def __str__(self):
        return self.full_name


class Profile(DeletableModel):
    GENDERS = (('M', 'Male'), ('F', 'Female'))

    user = models.OneToOneField('User', on_delete=do_nothing, related_name='profile')
    photo = models.ImageField(
        _('Profile Picture'),
        upload_to='profile/',
        help_text=_(
            "the user's profile picture."
        ),
        blank=True,
        null=True
    )
    address = models.CharField(_("Address"), max_length=255, null=True)
    city = models.ForeignKey('City', on_delete=do_nothing, null=True, blank=True, related_name='profiles',
                             verbose_name=_('City'))
    birth_date = models.DateField(_('Birth Date'), blank=True, null=True)
    gender = models.CharField(choices=GENDERS, max_length=1, default='M', verbose_name=_('Gender'), null=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


class Region(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=255, verbose_name=_('Arabic Name'))
    name_fr = models.CharField(max_length=255, verbose_name=_('English Name'))

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _("Regions")


class State(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=255, verbose_name=_('Arabic Name'))
    name_fr = models.CharField(max_length=255, verbose_name=_('English Name'))
    matricule = models.IntegerField(verbose_name=_('Matricule'))
    code_postal = models.IntegerField(verbose_name=_('Postal Code'))
    region = models.ForeignKey('Region', verbose_name=_('Region'), on_delete=do_nothing)

    def __str__(self):
        return "{0} {1}".format(self.matricule, self.name)

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _("States")


class City(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=255, verbose_name=_('Arabic Name'))
    name_en = models.CharField(max_length=255, verbose_name=_('English Name'))
    code_postal = models.IntegerField(verbose_name=_('Postal Code'))
    state = models.ForeignKey('State', on_delete=models.DO_NOTHING, related_name='cities', verbose_name=_('State'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _("Cities")


class Notification(BaseModel):
    pass
