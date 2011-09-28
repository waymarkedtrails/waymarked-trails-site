from datetime import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from django.conf import settings

def route_map_view(request, relid=None, name=None):
    if request.COOKIES.has_key('_hiking_location'):
        cookie = request.COOKIES['_hiking_location'].split('|')
    else:
        cookie = None

    extent = (693000, 5764000, 1150000, 6062100) 
    showroute = -1
    if relid is not None:
        try:
            obj = settings.ROUTE_TABLE_MODEL.objects.get(id=relid)
            extent = obj.geom.extent
            showroute = obj.id
        except:
            showroute = relid
    elif name is not None:
        try:
            obj = settings.ROUTE_TABLE_MODEL.objects.get(name__iexact=name)
            extent = obj.geom.extent
            showroute = obj.id
        except:
            showroute = 0

    if showroute == -1:
        # check for a cookie
        if cookie is not None:
            if len(cookie) >= 4:
                # XXX make sure the cookie is correct
                extent = cookie[:4]

    context = {'minlat': str(extent[1]), 'maxlat' : str(extent[3]),
            'minlon':  str(extent[0]), 'maxlon' : str(extent[2]),
            'showroute' : showroute, 'baseopacity' : '1.0',
            'routeopacity' : '0.8', 'hillopacity' : '0.0'
           }

    uf = open(settings._BASEDIR + '/../last_update')
    context['updatetime'] = datetime.strptime(uf.readline().strip(),
                                 '%Y-%m-%dT%H:%M:%SZ')
    uf.close()

    if cookie is not None:
        if len(cookie) >= 7:
            context['baseopacity'] = cookie[4]
            context['routeopacity'] = cookie[5]
            context['hillopacity'] = cookie[6]    

    return direct_to_template(request,
                              template='basemap.html', 
                              extra_context=context)
