from django.conf.urls import patterns, include, url
from tastypie.api import Api

from .api import UserResource, CreateUserResource

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(CreateUserResource())

urlpatterns = patterns('',
    url(r'', include(v1_api.urls)),
)
