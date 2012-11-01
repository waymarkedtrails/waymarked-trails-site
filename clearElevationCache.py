from django.conf import settings

# Location of cache you want to expire
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/waymarkedtrails-cache',
    }
}

settings.configure(CACHES=CACHES)

from django.core.cache import cache


def expire_relation(relation_id):
    cache.delete(relation_id)


