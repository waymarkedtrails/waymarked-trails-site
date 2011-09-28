from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('cycling.mapview.views',
    (r'^$', 'route_map_view', {}, 'simplemap'),
    (r'^relation/(?P<relid>\d+)$', 'route_map_view', {}, 'relationmap'),
    (r'^route/(?P<name>.+)$', 'route_map_view', {}, 'routemap'),
)

urlpatterns += patterns('',
    (r'^routebrowser/', include('cycling.routes.urls')),
    (r'^help/', include('cycling.helppages.urls')),
)

# for development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
)
