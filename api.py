from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.db import IntegrityError
from django.conf.urls import url

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpNotFound, HttpBadRequest
from tastypie.utils import trailing_slash

from registration.models import RegistrationProfile

from .forms import RegistrationForm, LoginForm


class CreateUserResource(ModelResource):
    class Meta:
        allowed_methods = ['post']
        object_class = User
        resource_name = 'new-user'
        authorization = Authorization()
        include_resource_uri = False
        serializer = Serializer(formats=['json'])
        always_return_data = True
        fields = ['username']

    def obj_create(self, bundle, **kwargs):
        form = RegistrationForm(bundle.data)
        if form.is_valid():
            try:
                bundle.obj = RegistrationProfile.objects.create_inactive_user(
                    form.cleaned_data.get('username'),
                    form.cleaned_data.get('email'),
                    form.cleaned_data.get('password'),
                    None,
                    False
                )
            except IntegrityError:
                raise ImmediateHttpResponse(self.create_response(
                    bundle.request,
                    {'reason': 'Something went wrong! You shouldn\'t see this message at all.', 'success': False},
                    response_class=HttpBadRequest))
        else:
            errors = {k: v for k, v in form.errors.items() if k != '__all__'}
            raise ImmediateHttpResponse(self.create_response(
                bundle.request,
                {'errors': errors, 'reason': form.non_field_errors(), 'success': False},
                response_class=HttpBadRequest))
        return bundle


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_methods = ['get', 'post']
        fields = ['username', 'email', 'id']
        authorization = DjangoAuthorization()
        serializer = Serializer(formats=['json'])

    def full_dehydrate(self, bundle, for_list=False):
        bundle = super(UserResource, self).full_dehydrate(bundle, for_list)
        bundle.data['permissions'] = list(bundle.obj.get_all_permissions())
        return bundle

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/login%s$' % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name='api_login'),
            url(r'^(?P<resource_name>%s)/logout%s$' % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/current%s$' % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('current'), name='api_current'),
            url(r'^(?P<resource_name>%s)/activate%s$' % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('activate'), name='api_activate'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            bundle = self.full_dehydrate(self.build_bundle(obj=form.user))
            return self.create_response(request, bundle.data)
        return self.create_response(request, {
            'success': False,
            'reason': form.non_field_errors()
        }, HttpNotFound)

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)

    def current(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            bundle = self.full_dehydrate(self.build_bundle(obj=request.user))
            return self.create_response(request, bundle.data)
        else:
            return self.create_response(request, {'success': False}, HttpNotFound)

    def activate(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        user = RegistrationProfile.objects.activate_user(request.GET['key'])
        if not user:
            return self.create_response(request, {
                'success': False,
                'reason': 'Invalid activation key'
            }, HttpBadRequest)
        else:
            return self.create_response(request, {
                'success': True,
                'username': user.username,
                })
