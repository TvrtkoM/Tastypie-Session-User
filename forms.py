import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

    error_messages = {
        'invalid_login': _('Please enter a correct username and password. '
                           'Note that both fields are case-sensitive.'),
        'inactive': _('This account is inactive.'),
        'empty': _('Username and password fields are required'),
        }

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username or not password:
            raise forms.ValidationError(self.error_messages['empty'])
        else:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])
            elif not self.user.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        return cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(min_length=6)
    email = forms.EmailField()
    password1 = forms.CharField(min_length=7)
    password2 = forms.CharField(required=False)

    error_messages = {
        'invalid': _('Please enter correct data in the form. All fields are required.'),
        'nonequal_passwords': _('Entered passwords do not match.'),
    }

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if not username or not email or not password1:
            raise forms.ValidationError(self.error_messages['invalid'])
        if password1 and password1 != password2:
            raise forms.ValidationError(self.error_messages['nonequal_passwords'])
        else:
            cleaned_data['password'] = password1
            cleaned_data.pop('password1', None)
            cleaned_data.pop('password2', None)

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w_]+$', username):
            raise forms.ValidationError('Username must contain only letters, numbers and underscores.')
        elif User.objects.filter(username__exact=username).count() != 0:
            raise forms.ValidationError('User with this username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email).count() != 0:
            raise forms.ValidationError('User with this e-mail already exists.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 != password1:
            raise forms.ValidationError('Please retype the correct password.')
        return password2
