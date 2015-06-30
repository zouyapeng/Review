from django.conf.urls import patterns, include, url
from tastypie.api import NamespacedApi
from cdos.resource import SoftwareResource, ImageResource, UserResource

api = NamespacedApi(urlconf_namespace="cdos")
api.register(SoftwareResource())
api.register(ImageResource())
api.register(UserResource())

urlpatterns = patterns('',
               url(r'^api/', include(api.urls)),
)
