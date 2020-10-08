from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from accounts.models import User, Profile, City
from base_backend import _


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': str(_("Username")) + "/" + str(_("Phone")) + "/" + str(_("Email"))
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )


class OtpForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Code')
            }
        )
    )


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Username")
            }
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("First Name")
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Last Name")
            }
        )
    )
    phone = SimpleArrayField(forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Phone Number")
            }
        )
    ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )
    c_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Confirm Password")
            }
        )
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'placeholder': _("Email")
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', "first_name", "last_name", 'user_type', 'phone', 'email']


class ProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), empty_label=_('Choose a user'))
    photo = forms.ImageField(allow_empty_file=True)
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Address')
            }
        )
    )
    city = forms.ModelChoiceField(City.objects.all(), empty_label=_('Select a city'), required=False)
    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'placeholder': _('Birth Date')
            }
        )
    )

    class Meta:
        model = Profile
        fields = ['user', 'photo', 'address', 'city', 'birth_date', 'gender']
