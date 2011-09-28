from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('hiking.mapview.views',
    (r'^$', 'route_map_view', {}, 'simplemap'),
    (r'^relation/(?P<relid>\d+)$', 'route_map_view', {}, 'relationmap'),
    (r'^route/(?P<name>.+)$', 'route_map_view', {}, 'routemap'),
)

urlpatterns += patterns('',
    (r'^routebrowser/', include('hiking.routes.urls')),
    (r'^help/', include('hiking.helppages.urls')),
)

# for development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
)
