from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'b1.views.home', name='home'),
   url(r'^cdos/', include('cdos.urls', namespace='cdos')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^.*$', 'cdos.views.home', name='home'),
)
